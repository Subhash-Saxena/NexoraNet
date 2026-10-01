from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import (
    ConfidenceLevel,
    DifficultyLevel,
    RecommendationPriority,
    RecommendationType,
    TopicPerformanceStatus,
)


class DifficultyStats(BaseModel):
    """Aggregate volume and accuracy metrics for a specific difficulty tier."""

    seen: int = 0
    correct: int = 0
    accuracy: float = 0.0


class DifficultyPerformanceSummary(BaseModel):
    """Tiered accuracy distribution across all three difficulty levels."""

    BEGINNER: DifficultyStats = Field(default_factory=DifficultyStats)
    INTERMEDIATE: DifficultyStats = Field(default_factory=DifficultyStats)
    ADVANCED: DifficultyStats = Field(default_factory=DifficultyStats)


class TopicPerformanceItem(BaseModel):
    """Topic-level performance state with explainable diagnostic indicators."""

    topic_id: int
    topic_title: str
    topic_slug: str
    status: TopicPerformanceStatus
    questions_seen: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    unanswered: int = 0
    accuracy: float = 0.0
    recent_accuracy: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.INSUFFICIENT
    recommended_action: str
    last_attempt_at: datetime | None = None
    difficulty_distribution: dict[str, DifficultyStats] = Field(default_factory=dict)


class RecommendationItem(BaseModel):
    """Actionable recommendation with explicit rationale."""

    id: str
    type: RecommendationType
    title: str
    reason: str
    priority: RecommendationPriority
    topic_id: int | None = None
    topic_slug: str | None = None
    recommended_difficulty: DifficultyLevel | None = None
    action_label: str
    action_url: str


class AdaptiveOverviewResponse(BaseModel):
    """Comprehensive performance dashboard and personalized guidance overview."""

    user_id: int
    has_sufficient_data: bool
    data_message: str
    overall_accuracy: float = 0.0
    total_questions_analyzed: int = 0
    total_attempts_analyzed: int = 0
    recommended_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    difficulty_reason: str
    difficulty_performance: DifficultyPerformanceSummary
    top_topics_needing_practice: list[TopicPerformanceItem] = Field(default_factory=list)
    strongest_topics: list[TopicPerformanceItem] = Field(default_factory=list)
    all_topics: list[TopicPerformanceItem] = Field(default_factory=list)
    next_action: RecommendationItem | None = None
    recommendations: list[RecommendationItem] = Field(default_factory=list)


class StartAdaptiveTestRequest(BaseModel):
    """Parameters for launching a dynamically compiled adaptive practice session."""

    question_count: int = Field(default=20, ge=5, le=50)
    duration_minutes: int = Field(default=20, ge=5, le=90)
    focus_topic_ids: list[int] | None = None


class TrackRecommendationEventRequest(BaseModel):
    """Telemetry payload for logging student recommendation engagement."""

    recommendation_type: RecommendationType
    title: str
    reason: str
    action_url: str
    event_type: str = "CLICKED"
    topic_id: int | None = None
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
