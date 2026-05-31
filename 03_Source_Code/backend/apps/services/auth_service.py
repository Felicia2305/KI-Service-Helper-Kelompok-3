from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..config import settings
from ..models.user_model import User
from ..repositories.user_repository import UserRepository
from ..schemas.auth_schema import RegisterRequest
from ..logger import security_logger

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self._repo = UserRepository(db)

    def register(self, data: RegisterRequest) -> User:
        if self._repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email sudah terdaftar.",
            )
        hashed = _pwd_context.hash(data.password)
        return self._repo.create(
            email=data.email,
            password_hash=hashed,
            nama=data.nama,
            nim_nip=data.nim_nip,
            role=data.role,
        )

    def login(self, email: str, password: str) -> str:
        user = self._repo.get_by_email(email)
        if not user or not _pwd_context.verify(password, user.password_hash):
            security_logger.warning("LOGIN_FAILED email=%s", email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email atau password salah.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            security_logger.warning("LOGIN_INACTIVE email=%s", email)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun tidak aktif.",
            )
        security_logger.info("LOGIN_SUCCESS email=%s role=%s", user.email, user.role)
        return self._create_token(str(user.id))

    def get_user_from_token(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self._repo.get_by_id(user_id)
        if user is None:
            raise credentials_exception
        return user

    def _create_token(self, user_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
