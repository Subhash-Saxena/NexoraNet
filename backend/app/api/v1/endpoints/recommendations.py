"""Pedagogical Recommendations API Endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import RecommendationResponse
from app.services.analytics.recommendation_engine_service import (
    RecommendationEngineService,
)

router = APIRouter()


@router.get("", response_model=list[RecommendationResponse])
@router.get("/", response_model=list[RecommendationResponse], include_in_schema=False)
def get_recommendations(
    db: DbSession, current_user: CurrentUser
) -> list[dict[str, Any]]:
    """Retrieve actionable, neutral study recommendations with pedagogical justifications."""
    return RecommendationEngineService.get_recommendations(db, current_user)


@router.post("/{recommendation_id}/dismiss", response_model=dict[str, Any])
def dismiss_recommendation(
    recommendation_id: int, db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Dismiss a study recommendation."""
    success = RecommendationEngineService.dismiss_recommendation(db, current_user, recommendation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found or already dismissed.",
        )
    return {"status": "dismissed", "recommendation_id": recommendation_id}
