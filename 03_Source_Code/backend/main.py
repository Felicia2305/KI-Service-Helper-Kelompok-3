import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from apps.database import engine
from apps.models import User, ServiceType, Ticket  # noqa: F401 — pastikan semua model terdaftar
from apps.database import Base
from apps.routes import auth_routes, ticket_routes, service_routes
from apps.limiter import limiter
from apps.config import settings
from dotenv import load_dotenv
load_dotenv()

if settings.AUTO_CREATE_TABLES:
    # Buat semua tabel saat startup hanya untuk setup development eksplisit.
    Base.metadata.create_all(bind=engine)

_error_logger = logging.getLogger("iash.error")

app = FastAPI(
    title="IASH API",
    description="IPB Academic Service Helper — Backend API",
    version="1.0.0",
)

if settings.is_production and settings.trusted_hosts_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts_list)

if settings.is_production or settings.FORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)


# Global exception handler — cegah stack trace bocor ke client
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    _error_logger.error(
        "UNHANDLED_EXCEPTION method=%s path=%s error=%s",
        request.method, request.url.path, str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    if request.headers.get("content-length") and int(request.headers["content-length"]) > settings.MAX_REQUEST_SIZE:
        return JSONResponse(status_code=413, content={"detail": "Request terlalu besar."})
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if request.url.path in {"/docs", "/docs/oauth2-redirect", "/redoc"}:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com"
        )
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path.startswith("/api/auth"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(auth_routes.router)
app.include_router(service_routes.router)
app.include_router(ticket_routes.router)


@app.get("/")
def health_check():
    return {"status": "ok", "app": "IASH API"}

app = app
