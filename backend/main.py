import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.database import engine
from app.models import User, ServiceType, Ticket  # noqa: F401 — pastikan semua model terdaftar
from app.database import Base
from app.routes import auth_routes, ticket_routes, service_routes
from app.limiter import limiter
from app.config import settings

# Buat semua tabel saat startup (development)
Base.metadata.create_all(bind=engine)

_error_logger = logging.getLogger("iash.error")

app = FastAPI(
    title="IASH API",
    description="IPB Academic Service Helper — Backend API",
    version="1.0.0",
)

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
        content={"detail": "Terjadi kesalahan internal. Silakan coba lagi."},
    )

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", settings.FRONTEND_URL],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth_routes.router)
app.include_router(service_routes.router)
app.include_router(ticket_routes.router)


@app.get("/")
def health_check():
    return {"status": "ok", "app": "IASH API"}
