from uuid import UUID
from sqlalchemy.orm import Session
from ..models.user_model import User


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
