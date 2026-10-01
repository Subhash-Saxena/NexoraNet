"""Educational Certificates API Endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.schemas.analytics import CertificateVerifyResponse
from app.services.analytics.report_service import ReportService

router = APIRouter()


@router.get("/verify/{verification_code}", response_model=CertificateVerifyResponse)
def verify_certificate(
    verification_code: str, db: DbSession
) -> dict[str, Any]:
    """Public read-only verification for internal NexoraNet educational completion certificates."""
    try:
        return ReportService.verify_certificate(db, verification_code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
