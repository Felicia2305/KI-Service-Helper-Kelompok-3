from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user_model import User
from ..services.auth_service import AuthService
from ..services.audit_service import AuditService
from ..schemas.auth_schema import RegisterRequest, TokenResponse
from ..schemas.user_schema import UserResponse
from ..limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["Auth"])

COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,        # wajib kalau samesite=none
        samesite="none",    # izinkan cross-site (fe & be beda domain)
        max_age=COOKIE_MAX_AGE,
        path="/",           # aktif di semua endpoint, bukan cuma /api/auth
    )

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    try:
        access_token, refresh_token = service.login_user(form.username, form.password)
        user = service.get_user_from_token(access_token)
        AuditService(db).log_event(
            user.id, "login_success", "auth",
            request.client.host if request.client else None, {}
        )
    except Exception:
        AuditService(db).log_event(
            None, "login_failed", "auth",
            request.client.host if request.client else None,
            {"email": form.username},
        )
        raise
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/minute")
def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService(db).register_user(data)
    AuditService(db).log_event(
        user.id, "register", "auth",
        request.client.host if request.client else None,
        {"role": user.role},
    )
    return user


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    service = AuthService(db)
    access_token = service.refresh_access_token(token)
    # rotate refresh token sekalian (best practice)
    user = service.get_user_from_token(access_token)
    _, new_refresh = service.login_user.__func__  # skip — gunakan cara di bawah
    AuditService(db).log_event(
        user.id, "token_refresh", "auth",
        request.client.host if request.client else None, {}
    )
    return TokenResponse(access_token=access_token)


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    AuthService(db).logout_user(str(current_user.id), request.cookies.get("refresh_token"))
    AuditService(db).log_event(
        current_user.id, "logout", "auth",
        request.client.host if request.client else None, {}
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",           # harus sama dengan path saat set
        samesite="none",
        secure=True,
    )
    return {"status": "ok"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user