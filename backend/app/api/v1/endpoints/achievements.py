"""Achievements API Endpoints."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import AchievementResponse
from app.services.analytics.achievement_service import AchievementService

router = APIRouter()


@router.get("", response_model=list[AchievementResponse])
@router.get("/", response_model=list[AchievementResponse], include_in_schema=False)
def get_all_achievements(
    db: DbSession, current_user: CurrentUser
) -> list[dict[str, Any]]:
    """Retrieve all platform educational achievements with current student progress and unlock states."""
    return AchievementService.get_user_achievements(db, current_user)


@router.get("/me", response_model=list[AchievementResponse])
def get_my_achievements(
    db: DbSession, current_user: CurrentUser
) -> list[dict[str, Any]]:
    """Alias for current learner's achievements."""
    return AchievementService.get_user_achievements(db, current_user)
