"""Administrative & Content Management API Endpoints (Enforces Server-Side Admin Authorization)."""

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminUser, DbSession
from app.schemas.admin import (
    AdminAuditLogResponse,
    AdminContentItemResponse,
    AdminContentPublishResponse,
    AdminDashboardResponse,
)
from app.services.analytics.admin_content_service import AdminContentService

router = APIRouter()


@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_admin_dashboard(
    db: DbSession, current_admin: AdminUser
) -> dict[str, Any]:
    """
    Retrieve platform-wide content health, active learner telemetry, and publication breakdown.
    CRITICAL: Requires administrator authorization. Students receive HTTP 403 Forbidden.
    """
    return AdminContentService.get_dashboard_metrics(db)


@router.get("/content", response_model=list[AdminContentItemResponse])
def list_admin_content(
    db: DbSession,
    current_admin: AdminUser,
    content_type: Annotated[str | None, Query(description="Filter by type: QUESTION, CHALLENGE, LAB, LESSON")] = None,
    status_filter: Annotated[str | None, Query(alias="status", description="Filter by status: PUBLISHED, DRAFT, ARCHIVED")] = None,
    search: Annotated[str | None, Query(description="Search title/code")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict[str, Any]]:
    """List and filter content items across educational modules for administrative management."""
    return AdminContentService.list_content(
        db=db,
        content_type=content_type,
        status=status_filter,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.post("/content/{content_type}/{content_id}/publish", response_model=AdminContentPublishResponse)
def publish_content(
    content_type: str,
    content_id: str,
    db: DbSession,
    current_admin: AdminUser,
) -> dict[str, Any]:
    """Validate and publish a content item, updating version records and logging to audit ledger."""
    try:
        return AdminContentService.publish_content(
            db=db, actor=current_admin, content_type=content_type, content_id=content_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/content/{content_type}/{content_id}/unpublish", response_model=dict[str, Any])
def unpublish_content(
    content_type: str,
    content_id: str,
    db: DbSession,
    current_admin: AdminUser,
) -> dict[str, Any]:
    """Unpublish content to draft status."""
    try:
        return AdminContentService.unpublish_content(
            db=db, actor=current_admin, content_type=content_type, content_id=content_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/content/{content_type}/{content_id}/archive", response_model=dict[str, Any])
def archive_content(
    content_type: str,
    content_id: str,
    db: DbSession,
    current_admin: AdminUser,
) -> dict[str, Any]:
    """Archive content item from student access."""
    try:
        return AdminContentService.archive_content(
            db=db, actor=current_admin, content_type=content_type, content_id=content_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/audit", response_model=list[AdminAuditLogResponse])
def list_admin_audit_logs(
    db: DbSession,
    current_admin: AdminUser,
    action: Annotated[str | None, Query(description="Filter by audit action")] = None,
    target_type: Annotated[str | None, Query(description="Filter by target type")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[dict[str, Any]]:
    """Retrieve immutable audit ledger records of administrative changes."""
    return AdminContentService.list_audit_logs(
        db=db, action=action, target_type=target_type, limit=limit, offset=offset
    )


@router.get("/analytics", response_model=dict[str, Any])
def get_admin_analytics(
    db: DbSession, current_admin: AdminUser
) -> dict[str, Any]:
    """Platform-wide learner engagement metrics and aggregate activity volume."""
    return AdminContentService.get_dashboard_metrics(db)
