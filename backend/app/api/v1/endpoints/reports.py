"""Assessment Reports API Endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import AssessmentReportResponse
from app.services.analytics.report_service import ReportService

router = APIRouter()


@router.get("/assessment", response_model=AssessmentReportResponse)
def get_assessment_report(
    db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Retrieve the latest assessment report for the authenticated student."""
    return ReportService.get_latest_assessment_report(db, current_user)


@router.post("/assessment/generate", response_model=AssessmentReportResponse, status_code=status.HTTP_201_CREATED)
def generate_assessment_report(
    db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Generate a fresh archival learning assessment report with current telemetry."""
    return ReportService.generate_assessment_report(db, current_user)


@router.get("/{report_uuid}", response_model=AssessmentReportResponse)
def get_report_by_uuid(
    report_uuid: str, db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Retrieve a specific report by UUID with IDOR access authorization."""
    try:
        return ReportService.get_report_by_uuid(db, current_user, report_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
