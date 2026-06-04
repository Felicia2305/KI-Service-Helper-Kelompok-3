import hashlib
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import ExpiredSignatureError, JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..config import settings
from ..models.user_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.auth_schema import RegisterRequest
from ..logger import security_logger


class AuthService:
    def __init__(self, db: Session):
        self._repo = UserRepository(db)

    def register_user(self, data: RegisterRequest) -> User:
        if self._repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invalid credentials",
            )
        hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt(rounds=12)).decode()
        return self._repo.create(
            email=data.email,
            password_hash=hashed,
            nama=data.nama,
            nim_nip=data.nim_nip,
            role=data.role,
        )

    def register(self, data: RegisterRequest) -> User:
        return self.register_user(data)

    def login_user(self, email: str, password: str) -> tuple[str, str]:
        user = self._repo.get_by_email(email)
        if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            security_logger.warning("LOGIN_FAILED email=%s", email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            security_logger.warning("LOGIN_INACTIVE email=%s", email)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun tidak aktif.",
            )
        security_logger.info("LOGIN_SUCCESS email=%s role=%s", user.email, user.role)
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(str(user.id))
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        self._repo.save_refresh_token(user.id, self._hash_token(refresh_token), datetime.fromtimestamp(payload["exp"], timezone.utc))
        return access_token, refresh_token

    def login(self, email: str, password: str) -> str:
        access_token, _ = self.login_user(email, password)
        return access_token

    def get_user_from_token(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "access":
                raise credentials_exception
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise credentials_exception

        user = self._repo.get_by_id(user_id)
        if user is None:
            raise credentials_exception
        return user

    def refresh_access_token(self, refresh_token: str | None) -> str:
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token_row = self._repo.get_refresh_token(self._hash_token(refresh_token))
        if token_row is None or token_row.revoked_at is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user = self._repo.get_by_id(payload["sub"])
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return self._create_access_token(user)

    def logout_user(self, user_id: str | None = None, refresh_token: str | None = None) -> None:
        if refresh_token:
            self._repo.revoke_refresh_token(self._hash_token(refresh_token))
            return
        if user_id:
            self._repo.revoke_user_refresh_tokens(user_id)

    def _create_access_token(self, user: User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user.id), "role": user.role, "type": "access", "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def _create_refresh_token(self, user_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"sub": user_id, "type": "refresh", "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
