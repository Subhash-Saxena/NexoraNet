"""Scenario Attempt Service for Educational SOC Scenarios.

Manages learner progression through the 9 investigation stages,
state transitions, progressive hint unlocks, and final grading.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.enums import ScenarioAttemptStatus, ScenarioStage
from app.models.soc_scenario import ScenarioAttempt, SocScenario
from app.services.soc_scenarios.scenario_scoring_service import ScenarioScoringService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

STAGE_SEQUENCE = [
    ScenarioStage.STAGE_1_INITIAL_SIGNAL,
    ScenarioStage.STAGE_2_EVIDENCE_SELECTION,
    ScenarioStage.STAGE_3_CORRELATION,
    ScenarioStage.STAGE_4_HYPOTHESIS,
    ScenarioStage.STAGE_5_VALIDATION,
    ScenarioStage.STAGE_6_MITRE_MAPPING,
    ScenarioStage.STAGE_7_RESPONSE_DECISION,
    ScenarioStage.STAGE_8_OUTCOME,
    ScenarioStage.STAGE_9_LESSONS_LEARNED,
]


class ScenarioAttemptService:
    """Orchestrates learner interactive sessions through SOC scenarios."""

    @classmethod
    def start_attempt(
        cls,
        db: Session,
        scenario_identifier: str | int,
        user_id: int | None = None,
    ) -> ScenarioAttempt:
        """Initialize a new attempt session for a scenario."""
        if isinstance(scenario_identifier, int) or (isinstance(scenario_identifier, str) and scenario_identifier.isdigit()):
            scenario = db.query(SocScenario).filter(SocScenario.id == int(scenario_identifier)).first()
        else:
            scenario = db.query(SocScenario).filter(SocScenario.scenario_id == str(scenario_identifier)).first()

        if not scenario:
            raise ValueError(f"Scenario '{scenario_identifier}' not found.")

        attempt_id = f"ATT-{uuid.uuid4().hex[:10].upper()}"
        attempt = ScenarioAttempt(
            attempt_id=attempt_id,
            scenario_id=scenario.id,
            user_id=user_id,
            status=ScenarioAttemptStatus.IN_PROGRESS,
            current_stage=ScenarioStage.STAGE_1_INITIAL_SIGNAL,
            stage_data_json="{}",
            hints_used=0,
            score=0.0,
            started_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    @classmethod
    def get_attempt(cls, db: Session, attempt_id: str) -> ScenarioAttempt | None:
        """Fetch attempt record by unique ID."""
        return db.query(ScenarioAttempt).filter(ScenarioAttempt.attempt_id == attempt_id).first()

    @classmethod
    def update_stage_data(
        cls,
        db: Session,
        attempt_id: str,
        stage_name: str,
        stage_payload: dict[str, Any],
        advance_stage: bool = False,
    ) -> ScenarioAttempt:
        """Save learner inputs for current stage and optionally advance to next stage."""
        attempt = cls.get_attempt(db, attempt_id)
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found.")

        if attempt.status == ScenarioAttemptStatus.COMPLETED:
            raise ValueError(f"Attempt '{attempt_id}' is already finalized and cannot be modified.")

        # Update JSON stage data
        try:
            current_data = json.loads(attempt.stage_data_json) if attempt.stage_data_json else {}
        except (json.JSONDecodeError, ValueError, TypeError):
            current_data = {}

        current_data[stage_name] = stage_payload
        attempt.stage_data_json = json.dumps(current_data)

        if advance_stage:
            current_idx = STAGE_SEQUENCE.index(attempt.current_stage) if attempt.current_stage in STAGE_SEQUENCE else 0
            if current_idx < len(STAGE_SEQUENCE) - 1:
                attempt.current_stage = STAGE_SEQUENCE[current_idx + 1]

        db.commit()
        db.refresh(attempt)
        return attempt

    @classmethod
    def unlock_hint(
        cls,
        db: Session,
        attempt_id: str,
    ) -> dict[str, Any]:
        """Reveal next progressive hint and log penalty deduction."""
        attempt = cls.get_attempt(db, attempt_id)
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found.")

        scenario = attempt.scenario
        hints: list[str] = []
        if scenario.hints_json:
            try:
                hints = json.loads(scenario.hints_json)
            except (json.JSONDecodeError, ValueError, TypeError):
                hints = []

        if not hints:
            return {"hint": "No additional hints available for this scenario.", "hints_used": attempt.hints_used, "remaining": 0}

        if attempt.hints_used >= len(hints):
            return {
                "hint": hints[-1],
                "hints_used": attempt.hints_used,
                "remaining": 0,
                "message": "All hints have already been unlocked.",
            }

        unlocked_hint = hints[attempt.hints_used]
        attempt.hints_used += 1
        db.commit()
        db.refresh(attempt)

        return {
            "hint": unlocked_hint,
            "hints_used": attempt.hints_used,
            "remaining": len(hints) - attempt.hints_used,
            "penalty_applied": ScenarioScoringService.HINT_PENALTY_POINTS,
        }

    @classmethod
    def submit_and_evaluate(
        cls,
        db: Session,
        attempt_id: str,
        final_stage_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Finalize attempt, evaluate all stages, calculate score, and return results."""
        attempt = cls.get_attempt(db, attempt_id)
        if not attempt:
            raise ValueError(f"Attempt '{attempt_id}' not found.")

        if final_stage_data:
            try:
                data = json.loads(attempt.stage_data_json) if attempt.stage_data_json else {}
            except (json.JSONDecodeError, ValueError, TypeError):
                data = {}
            data.update(final_stage_data)
            attempt.stage_data_json = json.dumps(data)

        stage_data: dict[str, Any] = {}
        if attempt.stage_data_json:
            try:
                stage_data = json.loads(attempt.stage_data_json)
            except (json.JSONDecodeError, ValueError, TypeError):
                stage_data = {}

        result = ScenarioScoringService.calculate_score(
            scenario=attempt.scenario,
            stage_data=stage_data,
            hints_used=attempt.hints_used,
        )

        attempt.status = ScenarioAttemptStatus.COMPLETED
        attempt.score = result["score"]
        attempt.score_breakdown_json = json.dumps(result["breakdown"])
        attempt.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(attempt)

        return {
            "attempt_id": attempt.attempt_id,
            "scenario_id": attempt.scenario.scenario_id,
            "scenario_title": attempt.scenario.title,
            "status": attempt.status,
            "score": result["score"],
            "max_score": result["max_score"],
            "passed": result["passed"],
            "breakdown": result["breakdown"],
            "feedback": result["feedback"],
            "solution_explanation": attempt.scenario.solution_explanation,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        }
