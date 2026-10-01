import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.health import router as health_router
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.errors import register_exception_handlers

logger = logging.getLogger("nexoranet.main")
settings = get_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforce defense-in-depth HTTP security response headers."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if settings.STRICT_SECURITY_HEADERS:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = (
                "geolocation=(), camera=(), microphone=(), payment=()"
            )
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline';"
            )
            if settings.ENVIRONMENT == "production":
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains"
                )
        return response


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for application startup and shutdown tasks."""
    logger.info("Initializing NexoraNet API service...")
    # Validate production security invariants at startup
    if settings.ENVIRONMENT == "production":
        settings.validate_production_configuration()
        logger.info("Production configuration validated successfully.")

    # Auto-seed database if curriculum topics or default users are missing
    try:
        from app.db.session import SessionLocal
        from app.models.curriculum import Topic
        from app.seed.seed_db import seed_database
        with SessionLocal() as db:
            topic_count = db.query(Topic).count()
            if topic_count == 0:
                logger.info("Database topics table is empty. Running automatic seed...")
                seed_database(db)
                logger.info("Automatic database seeding completed successfully.")
            else:
                logger.info("Database curriculum already present (%d topics).", topic_count)
    except Exception as exc:
        logger.warning("Database seed check encountered an issue (non-fatal): %s", exc)

    yield
    logger.info("Shutting down NexoraNet API service.")


def create_application() -> FastAPI:
    """Application factory for NexoraNet API."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="NexoraNet - Interactive Computer Networking and Cybersecurity Learning Platform API",
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Centralized exception handlers
    register_exception_handlers(app, is_debug=settings.DEBUG)

    # Health & Readiness endpoints (both /api/health and /health root probes)
    app.include_router(health_router, prefix="/api")
    app.include_router(health_router)

    # API v1 routes: /api/v1/...
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": settings.PROJECT_NAME,
            "tagline": settings.PROJECT_TAGLINE,
            "version": settings.VERSION,
            "status": "online",
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "health": "/api/health",
            "ready": "/api/ready",
        }

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )
