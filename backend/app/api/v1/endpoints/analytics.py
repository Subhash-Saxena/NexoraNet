"""Student Analytics API Endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import (
    LearningProgressSummaryResponse,
    StudentOverviewResponse,
)
from app.services.analytics.student_analytics_service import StudentAnalyticsService

router = APIRouter()


@router.get("/overview", response_model=StudentOverviewResponse)
def get_analytics_overview(
    db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Retrieve comprehensive student overview telemetry, learning time, streak, and recent activity."""
    return StudentAnalyticsService.get_overview(db, current_user)


@router.get("/progress", response_model=LearningProgressSummaryResponse)
def get_learning_progress(
    db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Retrieve detailed learning progress across modules, topics, and completion percentages."""
    return StudentAnalyticsService.get_learning_progress(db, current_user)


@router.get("/activity", response_model=list[dict[str, Any]])
def get_activity_timeline(
    db: DbSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100, description="Page limit")] = 20,
) -> list[dict[str, Any]]:
    """Retrieve unified chronological learning timeline across lessons, labs, tests, and challenges."""
    return StudentAnalyticsService.get_activity_feed(db, current_user, limit=limit)


@router.get("/trends", response_model=dict[str, Any])
def get_performance_trends(
    db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Retrieve historical trends for exam accuracy, lab completion, and challenge solving."""
    return StudentAnalyticsService.get_trends(db, current_user)
