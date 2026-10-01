from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import DifficultyLevel, RecommendationPriority, RecommendationType

if TYPE_CHECKING:
    from app.models.curriculum import Topic
    from app.models.user import User


class PerformanceSnapshot(TimeStampedModel):
    """Archival performance state capture for longitudinal tracking and auditability."""

    __tablename__ = "performance_snapshots"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    questions_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attempts_analyzed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recommended_difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
    )
    strong_topic_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    developing_topic_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    needs_practice_topic_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", backref="performance_snapshots")

    def __repr__(self) -> str:
        return (
            f"<PerformanceSnapshot user_id={self.user_id} "
            f"acc={self.overall_accuracy}% diff={self.recommended_difficulty}>"
        )


class RecommendationEvent(TimeStampedModel):
    """Event log for recommendation interactions and conversions."""

    __tablename__ = "recommendation_events"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recommendation_type: Mapped[RecommendationType] = mapped_column(
        Enum(RecommendationType, native_enum=False, length=30),
        nullable=False,
        index=True,
    )
    priority: Mapped[RecommendationPriority] = mapped_column(
        Enum(RecommendationPriority, native_enum=False, length=20),
        default=RecommendationPriority.MEDIUM,
        nullable=False,
    )
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    action_url: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(32), default="GENERATED", nullable=False
    )  # "GENERATED", "CLICKED", "STARTED"

    # Relationships
    user: Mapped["User"] = relationship("User", backref="recommendation_events")
    topic: Mapped["Topic | None"] = relationship("Topic")

    def __repr__(self) -> str:
        return (
            f"<RecommendationEvent user_id={self.user_id} "
            f"type={self.recommendation_type} event={self.event_type}>"
        )
