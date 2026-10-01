"""Database models for Step 18 Advanced SOC Scenario Engine.

Simulates 9-stage educational cybersecurity investigations.
Strictly offline and non-destructive.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import (
    ScenarioAttemptStatus,
    ScenarioCategory,
    ScenarioDifficulty,
    ScenarioStage,
)

if TYPE_CHECKING:
    from app.models.user import User


class SocScenario(TimeStampedModel):
    """Advanced educational SOC scenario definition."""

    __tablename__ = "soc_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    scenario_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(
        String(20), default=ScenarioDifficulty.INTERMEDIATE, nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(50), default=ScenarioCategory.SOC_INVESTIGATION, nullable=False, index=True
    )
    learning_objectives: Mapped[str] = mapped_column(Text, nullable=False)
    initial_signal_json: Mapped[str] = mapped_column(Text, nullable=False)
    available_evidence_json: Mapped[str] = mapped_column(Text, nullable=False)
    correlation_targets_json: Mapped[str] = mapped_column(Text, nullable=False)
    hypotheses_options_json: Mapped[str] = mapped_column(Text, nullable=False)
    mitre_techniques_json: Mapped[str] = mapped_column(Text, nullable=False)
    response_options_json: Mapped[str] = mapped_column(Text, nullable=False)
    scoring_rubric_json: Mapped[str] = mapped_column(Text, nullable=False)
    hints_json: Mapped[str] = mapped_column(Text, nullable=False)
    solution_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=20, nullable=False)

    # Relationships
    attempts: Mapped[list["ScenarioAttempt"]] = relationship(
        "ScenarioAttempt", back_populates="scenario", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SocScenario {self.scenario_id}: {self.title}>"


class ScenarioAttempt(TimeStampedModel):
    """Learner's attempt record through the 9-stage investigation process."""

    __tablename__ = "scenario_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    attempt_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    scenario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("soc_scenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default=ScenarioAttemptStatus.IN_PROGRESS, nullable=False, index=True
    )
    current_stage: Mapped[str] = mapped_column(
        String(50), default=ScenarioStage.STAGE_1_INITIAL_SIGNAL, nullable=False
    )
    stage_data_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    score_breakdown_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    scenario: Mapped["SocScenario"] = relationship("SocScenario", back_populates="attempts")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ScenarioAttempt {self.attempt_id} ({self.status}) - Score: {self.score}>"
