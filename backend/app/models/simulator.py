"""Database models for Network Simulator topologies, scenarios, and attempts."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel

if TYPE_CHECKING:
    from app.models.user import User


class SimulatorTopology(TimeStampedModel):
    """User-created or prebuilt network topology definition."""

    __tablename__ = "simulator_topologies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="BEGINNER", nullable=False)
    is_prebuilt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    topology_data: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<SimulatorTopology id={self.id} name='{self.name}' is_prebuilt={self.is_prebuilt}>"


class SimulatorScenario(TimeStampedModel):
    """Curated simulator challenges and tutorials with validation criteria."""

    __tablename__ = "simulator_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), default="BEGINNER", nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="FUNDAMENTALS", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    learning_objectives: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    initial_topology: Mapped[str | None] = mapped_column(Text, nullable=True)     # JSON topology
    tasks: Mapped[str | None] = mapped_column(Text, nullable=True)                # JSON tasks array
    validation_rules: Mapped[str | None] = mapped_column(Text, nullable=True)     # JSON rules array
    hints: Mapped[str | None] = mapped_column(Text, nullable=True)                # JSON hints array
    solution_explanation: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    attempts: Mapped[list["SimulatorScenarioAttempt"]] = relationship(
        "SimulatorScenarioAttempt", back_populates="scenario", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SimulatorScenario id={self.id} slug='{self.slug}' difficulty='{self.difficulty}'>"


class SimulatorScenarioAttempt(TimeStampedModel):
    """Student progress and validation results on a specific scenario."""

    __tablename__ = "simulator_scenario_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("simulator_scenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="IN_PROGRESS", nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    validation_results: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    scenario: Mapped["SimulatorScenario"] = relationship(
        "SimulatorScenario", back_populates="attempts"
    )

    def __repr__(self) -> str:
        return f"<SimulatorScenarioAttempt id={self.id} user_id={self.user_id} scenario_id={self.scenario_id} status='{self.status}'>"
