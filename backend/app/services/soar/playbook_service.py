"""Playbook Service for SOAR Automation.

Provides CRUD, validation, dry-run testing, and analytics KPI metrics
for educational SOAR security playbooks.
"""

import json
import uuid
from typing import Any

from app.models.enums import (
    PlaybookExecutionStatus,
    PlaybookRiskLevel,
    PlaybookStatus,
    PlaybookTriggerType,
)
from app.models.soar import (
    AutomationPlaybook,
    AutomationStep,
    PlaybookExecution,
)
from app.services.soar.condition_evaluator import SafeConditionEvaluator
from sqlalchemy import func
from sqlalchemy.orm import Session


class PlaybookService:
    """Manages playbook lifecycle, validation, metrics, and dry-run testing."""

    @classmethod
    def list_playbooks(
        cls,
        db: Session,
        category: str | None = None,
        status: str | None = None,
        trigger_type: str | None = None,
    ) -> list[AutomationPlaybook]:
        """Query playbooks with optional filters."""
        query = db.query(AutomationPlaybook)
        if category:
            query = query.filter(AutomationPlaybook.category == category)
        if status:
            query = query.filter(AutomationPlaybook.status == status)
        if trigger_type:
            query = query.filter(AutomationPlaybook.trigger_type == trigger_type)
        return query.order_by(AutomationPlaybook.playbook_id).all()

    @classmethod
    def get_playbook(cls, db: Session, identifier: str | int) -> AutomationPlaybook | None:
        """Fetch playbook by integer id or string playbook_id."""
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            pb = db.query(AutomationPlaybook).filter(AutomationPlaybook.id == int(identifier)).first()
            if pb:
                return pb
        return (
            db.query(AutomationPlaybook)
            .filter(AutomationPlaybook.playbook_id == str(identifier))
            .first()
        )

    @classmethod
    def create_playbook(
        cls,
        db: Session,
        name: str,
        description: str,
        category: str,
        trigger_type: str = PlaybookTriggerType.ALERT_CREATED,
        trigger_filter: dict[str, Any] | None = None,
        risk_level: str = PlaybookRiskLevel.LOW,
        requires_approval: bool = False,
        steps_data: list[dict[str, Any]] | None = None,
        created_by: str = "analyst",
    ) -> AutomationPlaybook:
        """Create a new educational playbook with ordered steps."""
        playbook_id = f"SOAR-PB-{uuid.uuid4().hex[:6].upper()}"

        playbook = AutomationPlaybook(
            playbook_id=playbook_id,
            name=name,
            description=description,
            category=category,
            version="1.0",
            status=PlaybookStatus.ENABLED,
            trigger_type=trigger_type,
            trigger_filter_json=json.dumps(trigger_filter) if trigger_filter else None,
            risk_level=risk_level,
            requires_approval=requires_approval,
            is_system=False,
            simulation_only=True,
            created_by=created_by,
        )
        db.add(playbook)
        db.flush()

        if steps_data:
            for idx, s in enumerate(steps_data, start=1):
                step = AutomationStep(
                    playbook_id=playbook.id,
                    step_order=s.get("step_order", idx),
                    name=s.get("name", f"Step {idx}"),
                    description=s.get("description"),
                    action_type=s["action_type"],
                    parameters_json=json.dumps(s.get("parameters", {})),
                    condition_json=json.dumps(s.get("condition")) if s.get("condition") else None,
                    requires_approval=s.get("requires_approval", False),
                    timeout_seconds=s.get("timeout_seconds", 30),
                    enabled=s.get("enabled", True),
                    on_failure=s.get("on_failure", "STOP"),
                    retry_count=min(s.get("retry_count", 0), 2),
                )
                db.add(step)

        db.commit()
        db.refresh(playbook)
        return playbook

    @classmethod
    def update_playbook_status(
        cls,
        db: Session,
        playbook_id: str | int,
        status: str,
    ) -> AutomationPlaybook:
        """Enable, disable, or draft a playbook."""
        playbook = cls.get_playbook(db, playbook_id)
        if not playbook:
            raise ValueError(f"Playbook '{playbook_id}' not found.")

        playbook.status = status
        db.commit()
        db.refresh(playbook)
        return playbook

    @classmethod
    def dry_run_playbook(
        cls,
        db: Session,
        playbook_id: str | int,
        mock_input: dict[str, Any],
    ) -> dict[str, Any]:
        """Perform a dry-run evaluation of conditions and parameter bindings without DB side effects."""
        playbook = cls.get_playbook(db, playbook_id)
        if not playbook:
            raise ValueError(f"Playbook '{playbook_id}' not found.")

        results: list[dict[str, Any]] = []
        simulated_context = {
            "execution_id": "DRY-RUN-001",
            "playbook_id": playbook.playbook_id,
            "trigger_source": "DRY_RUN",
            "source_id": "MOCK-SOURCE",
            "simulation_only": True,
            **mock_input,
        }

        for step in sorted(playbook.steps, key=lambda s: s.step_order):
            condition_met = True
            if step.condition_json:
                try:
                    cond_dict = json.loads(step.condition_json)
                    condition_met = SafeConditionEvaluator.evaluate(cond_dict, simulated_context)
                except (json.JSONDecodeError, ValueError, TypeError):
                    condition_met = False

            step_params = {}
            if step.parameters_json:
                try:
                    step_params = json.loads(step.parameters_json)
                except (json.JSONDecodeError, ValueError, TypeError):
                    step_params = {}

            results.append({
                "step_order": step.step_order,
                "step_name": step.name,
                "action_type": step.action_type,
                "condition_met": condition_met,
                "requires_approval": step.requires_approval,
                "status_preview": "WOULD_EXECUTE" if condition_met else "WOULD_SKIP",
                "parameters_preview": step_params,
            })

        return {
            "playbook_id": playbook.playbook_id,
            "playbook_name": playbook.name,
            "dry_run": True,
            "simulated_steps": results,
            "total_steps": len(playbook.steps),
            "executable_steps": sum(1 for r in results if r["status_preview"] == "WOULD_EXECUTE"),
        }

    @classmethod
    def get_metrics(cls, db: Session) -> dict[str, Any]:
        """Calculate SOAR automation KPIs for educational dashboard."""
        total_playbooks = db.query(AutomationPlaybook).count()
        enabled_playbooks = (
            db.query(AutomationPlaybook)
            .filter(AutomationPlaybook.status == PlaybookStatus.ENABLED)
            .count()
        )
        total_executions = db.query(PlaybookExecution).count()
        completed_executions = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.status == PlaybookExecutionStatus.COMPLETED)
            .count()
        )
        waiting_approval = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.status == PlaybookExecutionStatus.WAITING_APPROVAL)
            .count()
        )
        failed_executions = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.status == PlaybookExecutionStatus.FAILED)
            .count()
        )

        # Estimated analyst time saved (18 minutes per completed automation)
        hours_saved = round((completed_executions * 18) / 60, 1)

        # Success rate
        success_rate = (
            round((completed_executions / total_executions) * 100, 1)
            if total_executions > 0
            else 100.0
        )

        # Top playbooks
        top_playbooks = (
            db.query(
                AutomationPlaybook.name,
                AutomationPlaybook.playbook_id,
                func.count(PlaybookExecution.id).label("exec_count"),
            )
            .join(PlaybookExecution, PlaybookExecution.playbook_id == AutomationPlaybook.id)
            .group_by(AutomationPlaybook.id)
            .order_by(func.count(PlaybookExecution.id).desc())
            .limit(5)
            .all()
        )

        return {
            "total_playbooks": total_playbooks,
            "enabled_playbooks": enabled_playbooks,
            "total_executions": total_executions,
            "completed_executions": completed_executions,
            "waiting_approval": waiting_approval,
            "failed_executions": failed_executions,
            "success_rate_percent": success_rate,
            "analyst_hours_saved": hours_saved,
            "top_playbooks": [
                {"name": name, "playbook_id": pid, "executions": count}
                for name, pid, count in top_playbooks
            ],
        }
