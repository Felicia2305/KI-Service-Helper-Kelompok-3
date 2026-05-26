from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models.user_model import User
from .services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    return AuthService(db).get_user_from_token(token)


def require_staff(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "mahasiswa":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya staff yang dapat mengakses ini.")
    return current_user


def require_mahasiswa(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "mahasiswa":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hanya mahasiswa yang dapat mengakses ini.")
    return current_user
