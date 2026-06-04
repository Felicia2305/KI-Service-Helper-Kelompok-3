from uuid import UUID
from sqlalchemy.orm import Session
from ..models.user_model import User
from ..models.refresh_token_model import RefreshToken


class UserRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self._db.query(User).filter(User.email == email).first()

    def create(self, email: str, password_hash: str, nama: str, nim_nip: str, role: str) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            nama=nama,
            nim_nip=nim_nip,
            role=role,
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def save_refresh_token(self, user_id: UUID, token_hash: str, expires_at) -> RefreshToken:
        token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self._db.add(token)
        self._db.commit()
        self._db.refresh(token)
        return token

    def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        return self._db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    def revoke_refresh_token(self, token_hash: str) -> None:
        token = self.get_refresh_token(token_hash)
        if token:
            self._db.delete(token)
            self._db.commit()

    def revoke_user_refresh_tokens(self, user_id: UUID) -> None:
        self._db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        self._db.commit()
