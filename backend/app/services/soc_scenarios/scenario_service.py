"""Scenario Service for Advanced Educational SOC Scenarios.

Provides scenario catalog browsing, filtering, details retrieval,
and learner engagement statistics.
"""

from typing import Any

from app.models.enums import ScenarioAttemptStatus
from app.models.soc_scenario import ScenarioAttempt, SocScenario
from sqlalchemy import func
from sqlalchemy.orm import Session


class ScenarioService:
    """Manages scenario catalog access and student progress metrics."""

    @classmethod
    def list_scenarios(
        cls,
        db: Session,
        difficulty: str | None = None,
        category: str | None = None,
        search: str | None = None,
    ) -> list[SocScenario]:
        """Query scenarios with optional filters."""
        query = db.query(SocScenario).filter(SocScenario.is_active.is_(True))

        if difficulty:
            query = query.filter(SocScenario.difficulty == difficulty)
        if category:
            query = query.filter(SocScenario.category == category)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                (SocScenario.title.ilike(pattern))
                | (SocScenario.description.ilike(pattern))
                | (SocScenario.scenario_id.ilike(pattern))
            )

        return query.order_by(SocScenario.id).all()

    @classmethod
    def get_scenario(cls, db: Session, identifier: str | int) -> SocScenario | None:
        """Fetch scenario by integer ID or string scenario_id."""
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            sc = db.query(SocScenario).filter(SocScenario.id == int(identifier)).first()
            if sc:
                return sc
        return db.query(SocScenario).filter(SocScenario.scenario_id == str(identifier)).first()

    @classmethod
    def get_scenario_metrics(cls, db: Session, user_id: int | None = None) -> dict[str, Any]:
        """Calculate high-level completion statistics for scenarios."""
        total_scenarios = db.query(SocScenario).filter(SocScenario.is_active.is_(True)).count()
        total_attempts = db.query(ScenarioAttempt).count()
        completed_attempts = (
            db.query(ScenarioAttempt)
            .filter(ScenarioAttempt.status == ScenarioAttemptStatus.COMPLETED)
            .count()
        )

        avg_score_query = (
            db.query(func.avg(ScenarioAttempt.score))
            .filter(ScenarioAttempt.status == ScenarioAttemptStatus.COMPLETED)
            .scalar()
        )
        avg_score = round(float(avg_score_query), 1) if avg_score_query else 0.0

        user_completed = 0
        if user_id:
            user_completed = (
                db.query(ScenarioAttempt)
                .filter(
                    ScenarioAttempt.user_id == user_id,
                    ScenarioAttempt.status == ScenarioAttemptStatus.COMPLETED,
                )
                .count()
            )

        # Scenarios by difficulty
        diff_counts = (
            db.query(SocScenario.difficulty, func.count(SocScenario.id))
            .filter(SocScenario.is_active.is_(True))
            .group_by(SocScenario.difficulty)
            .all()
        )

        # Scenarios by category
        cat_counts = (
            db.query(SocScenario.category, func.count(SocScenario.id))
            .filter(SocScenario.is_active.is_(True))
            .group_by(SocScenario.category)
            .all()
        )

        return {
            "total_scenarios": total_scenarios,
            "total_attempts": total_attempts,
            "completed_attempts": completed_attempts,
            "avg_score": avg_score,
            "user_completed": user_completed,
            "difficulty_distribution": {d: c for d, c in diff_counts},
            "category_distribution": {c: count for c, count in cat_counts},
        }
