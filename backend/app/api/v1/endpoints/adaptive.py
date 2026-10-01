"""
Adaptive Performance and Recommendation API Endpoints.

Provides server-authoritative diagnostic reporting, explainable topic competency
indicators, and personalized next-step recommendations without client-side trusting.
"""


from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.models.adaptive import RecommendationEvent
from app.schemas.adaptive import (
    AdaptiveOverviewResponse,
    RecommendationItem,
    TopicPerformanceItem,
    TrackRecommendationEventRequest,
)
from app.services.adaptive_performance_service import adaptive_performance_service
from app.services.recommendation_service import recommendation_service

router = APIRouter()


@router.get("/overview", response_model=AdaptiveOverviewResponse)
def get_adaptive_overview(
    db: DbSession,
    current_user: CurrentUser,
) -> AdaptiveOverviewResponse:
    """
    Retrieve holistic student performance diagnostics and personalized guidance.
    Server-authoritative calculation based on recent examination performance.
    """
    perf = adaptive_performance_service.calculate_user_performance(
        user_id=current_user.id,
        db=db,
    )
    recs = recommendation_service.generate_recommendations(
        user_id=current_user.id,
        performance_data=perf,
        db=db,
    )
    next_action = recommendation_service.get_highest_priority_recommendation(recs)

    return AdaptiveOverviewResponse(
        user_id=current_user.id,
        has_sufficient_data=perf["has_sufficient_data"],
        data_message=perf["data_message"],
        overall_accuracy=perf["overall_accuracy"],
        total_questions_analyzed=perf["total_questions_analyzed"],
        total_attempts_analyzed=perf["total_attempts_analyzed"],
        recommended_difficulty=perf["recommended_difficulty"],
        difficulty_reason=perf["difficulty_reason"],
        difficulty_performance=perf["difficulty_performance"],
        top_topics_needing_practice=perf["top_topics_needing_practice"],
        strongest_topics=perf["strongest_topics"],
        all_topics=perf["all_topics"],
        next_action=next_action,
        recommendations=recs,
    )


@router.get("/topic-performance", response_model=list[TopicPerformanceItem])
def get_topic_performance(
    db: DbSession,
    current_user: CurrentUser,
    active_only: bool = Query(False, description="Filter only to topics with recorded questions"),
) -> list[TopicPerformanceItem]:
    """Retrieve fine-grained topic performance diagnostics."""
    perf = adaptive_performance_service.calculate_user_performance(
        user_id=current_user.id,
        db=db,
    )
    topics = perf["active_topics"] if active_only else perf["all_topics"]
    return topics


@router.get("/recommendations", response_model=list[RecommendationItem])
def get_recommendations(
    db: DbSession,
    current_user: CurrentUser,
) -> list[RecommendationItem]:
    """Retrieve categorized curriculum and practice recommendations."""
    perf = adaptive_performance_service.calculate_user_performance(
        user_id=current_user.id,
        db=db,
    )
    return recommendation_service.generate_recommendations(
        user_id=current_user.id,
        performance_data=perf,
        db=db,
    )


@router.get("/recommendations/next", response_model=RecommendationItem | None)
def get_next_recommended_action(
    db: DbSession,
    current_user: CurrentUser,
) -> RecommendationItem | None:
    """Retrieve the single highest-priority recommended next step."""
    perf = adaptive_performance_service.calculate_user_performance(
        user_id=current_user.id,
        db=db,
    )
    recs = recommendation_service.generate_recommendations(
        user_id=current_user.id,
        performance_data=perf,
        db=db,
    )
    return recommendation_service.get_highest_priority_recommendation(recs)


@router.post("/events", status_code=201)
def track_recommendation_event(
    payload: TrackRecommendationEventRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Log student engagement with recommendations for telemetry and efficacy analysis."""
    event = RecommendationEvent(
        user_id=current_user.id,
        recommendation_type=payload.recommendation_type,
        priority=payload.priority,
        topic_id=payload.topic_id,
        title=payload.title,
        reason=payload.reason,
        action_url=payload.action_url,
        event_type=payload.event_type,
    )
    db.add(event)
    db.commit()
    return {"status": "recorded"}
