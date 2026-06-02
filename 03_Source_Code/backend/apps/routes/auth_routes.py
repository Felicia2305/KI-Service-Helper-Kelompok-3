from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user_model import User
from ..services.auth_service import AuthService
from ..schemas.auth_schema import RegisterRequest, TokenResponse
from ..schemas.user_schema import UserResponse
from ..limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = AuthService(db).login(form.username, form.password)
    return TokenResponse(access_token=token)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(data)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
