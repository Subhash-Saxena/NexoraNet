import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.health import HealthCheckResponse, ReadinessResponse

logger = logging.getLogger("nexoranet.health")
router = APIRouter()
settings = get_settings()

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check() -> HealthCheckResponse:
    """Return platform operational liveness status and service identity."""
    return HealthCheckResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
    )


@router.get("/ready", response_model=ReadinessResponse, tags=["Health"])
def readiness_check(db: DbSession) -> ReadinessResponse:
    """Verify system readiness and database connectivity without disclosing secrets."""
    try:
        # Perform low-overhead connectivity ping against configured database
        db.execute(text("SELECT 1"))
        return ReadinessResponse(
            status="ready",
            service=settings.PROJECT_NAME,
            database="connected",
        )
    except (SQLAlchemyError, Exception) as e:
        logger.error(f"Readiness check failed: Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": settings.PROJECT_NAME,
                "database": "disconnected",
            },
        ) from e
