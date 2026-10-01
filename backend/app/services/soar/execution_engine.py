"""Execution Engine for Educational SOAR Playbooks.

Executes sequential playbook steps using allowlisted action handlers and
whitelist-based condition evaluation. Handles approval pauses, idempotency,
automatic retries, and comprehensive audit logging.
Strictly offline and non-destructive.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.enums import (
    ApprovalStatus,
    PlaybookExecutionStatus,
    PlaybookStatus,
    StepExecutionStatus,
)
from app.models.soar import (
    AutomationAuditLog,
    AutomationPlaybook,
    AutomationStep,
    ExecutionStepLog,
    PlaybookExecution,
)
from app.services.soar.action_handlers import ActionHandlerRegistry
from app.services.soar.condition_evaluator import SafeConditionEvaluator
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Orchestrates deterministic SOAR playbook runs with educational safety."""

    @classmethod
    def trigger_playbook(
        cls,
        db: Session,
        playbook_id: str | int,
        trigger_source: str,
        source_id: str,
        requested_by: str = "analyst",
        idempotency_key: str | None = None,
        initial_context: dict[str, Any] | None = None,
    ) -> PlaybookExecution:
        """Initialize or retrieve an execution instance and begin execution."""
        # 1. Resolve playbook
        if isinstance(playbook_id, int):
            playbook = db.query(AutomationPlaybook).filter(AutomationPlaybook.id == playbook_id).first()
        else:
            playbook = (
                db.query(AutomationPlaybook)
                .filter(
                    (AutomationPlaybook.playbook_id == playbook_id)
                    | (AutomationPlaybook.name == playbook_id)
                )
                .first()
            )

        if not playbook:
            raise ValueError(f"Playbook '{playbook_id}' not found.")

        if playbook.status != PlaybookStatus.ENABLED:
            raise ValueError(f"Playbook '{playbook.name}' is currently {playbook.status} and cannot be executed.")

        # 2. Check Idempotency Key
        actual_idempotency_key = idempotency_key or f"{playbook.playbook_id}:{trigger_source}:{source_id}"
        existing_exec = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.idempotency_key == actual_idempotency_key)
            .first()
        )
        if existing_exec:
            logger.info("Idempotent hit for execution key %s", actual_idempotency_key)
            return existing_exec

        # 3. Create new PlaybookExecution
        execution_uuid = f"EXEC-{uuid.uuid4().hex[:10].upper()}"
        execution = PlaybookExecution(
            execution_id=execution_uuid,
            playbook_id=playbook.id,
            trigger_source=trigger_source,
            source_id=str(source_id),
            idempotency_key=actual_idempotency_key,
            status=PlaybookExecutionStatus.QUEUED,
            current_step_order=0,
            total_steps=len(playbook.steps),
            requested_by=requested_by,
            simulation_only=True,
            started_at=datetime.now(timezone.utc),
            artifacts_json=json.dumps({"initial_context": initial_context or {}}),
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        # Audit start
        cls._log_audit(
            db=db,
            execution_id=execution.execution_id,
            action="EXECUTION_TRIGGERED",
            actor=requested_by,
            target_type="PLAYBOOK",
            target_id=playbook.playbook_id,
            new_state=PlaybookExecutionStatus.QUEUED,
            reason=f"Triggered by {trigger_source} id={source_id}",
        )

        # 4. Check playbook-level approval
        if playbook.requires_approval:
            execution.status = PlaybookExecutionStatus.WAITING_APPROVAL
            execution.approval_status = ApprovalStatus.PENDING
            execution.approval_reason = (
                f"Playbook '{playbook.name}' is marked high-risk and requires human analyst approval before starting."
            )
            db.commit()
            db.refresh(execution)
            cls._log_audit(
                db=db,
                execution_id=execution.execution_id,
                action="PLAYBOOK_APPROVAL_REQUIRED",
                actor=requested_by,
                target_type="PLAYBOOK_EXECUTION",
                target_id=execution.execution_id,
                new_state=PlaybookExecutionStatus.WAITING_APPROVAL,
                reason=execution.approval_reason,
            )
            return execution

        # 5. Run execution loop
        return cls._run_execution_loop(db=db, execution=execution, initial_context=initial_context)

    @classmethod
    def resume_execution(
        cls,
        db: Session,
        execution_id: str,
        actor: str = "analyst",
    ) -> PlaybookExecution:
        """Resume an execution that was paused waiting for approval."""
        execution = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.execution_id == execution_id)
            .first()
        )
        if not execution:
            raise ValueError(f"Playbook execution '{execution_id}' not found.")

        if execution.status not in (
            PlaybookExecutionStatus.APPROVED,
            PlaybookExecutionStatus.WAITING_APPROVAL,
        ):
            raise ValueError(
                f"Execution '{execution_id}' cannot be resumed from status '{execution.status}'."
            )

        # Reconstruct context from saved artifacts
        context: dict[str, Any] = {}
        if execution.artifacts_json:
            try:
                data = json.loads(execution.artifacts_json)
                context = data.get("context", data.get("initial_context", {}))
            except (json.JSONDecodeError, ValueError, TypeError):
                context = {}

        return cls._run_execution_loop(db=db, execution=execution, initial_context=context)

    @classmethod
    def _run_execution_loop(
        cls,
        db: Session,
        execution: PlaybookExecution,
        initial_context: dict[str, Any] | None = None,
    ) -> PlaybookExecution:
        """Main sequential step runner."""
        playbook = execution.playbook
        steps = sorted(playbook.steps, key=lambda s: s.step_order)

        # Base execution context
        context: dict[str, Any] = {
            "execution_id": execution.execution_id,
            "playbook_id": playbook.playbook_id,
            "trigger_source": execution.trigger_source,
            "source_id": execution.source_id,
            "requested_by": execution.requested_by,
            "approved_by": execution.approved_by,
            "simulation_only": True,
            "step_results": {},
        }
        if initial_context:
            context.update(initial_context)

        # Load existing step outputs if resuming
        if execution.artifacts_json:
            try:
                saved = json.loads(execution.artifacts_json)
                if "step_results" in saved:
                    context["step_results"].update(saved["step_results"])
                if "context" in saved:
                    context.update(saved["context"])
            except (json.JSONDecodeError, ValueError, TypeError):
                logger.debug("Failed parsing saved artifacts during context restoration")


        execution.status = PlaybookExecutionStatus.RUNNING
        db.commit()

        executed_count = 0
        failed_or_paused = False

        for step in steps:
            # If we're resuming, skip already completed or skipped steps
            if step.step_order <= execution.current_step_order:
                # Check if this step was completed
                existing_log = (
                    db.query(ExecutionStepLog)
                    .filter(
                        ExecutionStepLog.execution_id == execution.id,
                        ExecutionStepLog.step_order == step.step_order,
                    )
                    .first()
                )
                if existing_log and existing_log.status in (
                    StepExecutionStatus.COMPLETED,
                    StepExecutionStatus.SKIPPED,
                ):
                    continue

            # Update pointer
            execution.current_step_order = step.step_order
            db.commit()

            # Check if step is enabled
            if not step.enabled:
                cls._record_step_log(
                    db=db,
                    execution=execution,
                    step=step,
                    status=StepExecutionStatus.SKIPPED,
                    output_summary=json.dumps({"reason": "Step is disabled"}),
                )
                continue

            # Check condition if any
            if step.condition_json:
                try:
                    cond_dict = json.loads(step.condition_json)
                    meets_cond = SafeConditionEvaluator.evaluate(cond_dict, context)
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.warning("Error evaluating condition for step %s: %s", step.name, e)
                    meets_cond = False

                if not meets_cond:
                    cls._record_step_log(
                        db=db,
                        execution=execution,
                        step=step,
                        status=StepExecutionStatus.SKIPPED,
                        output_summary=json.dumps({"reason": "Condition evaluated to false"}),
                    )
                    continue

            # Check step approval requirement
            if step.requires_approval and execution.approval_status != ApprovalStatus.APPROVED:
                execution.status = PlaybookExecutionStatus.WAITING_APPROVAL
                execution.approval_status = ApprovalStatus.PENDING
                execution.approval_reason = f"Step {step.step_order} ('{step.name}') requires analyst authorization."
                cls._save_artifacts(db, execution, context)
                db.commit()

                cls._log_audit(
                    db=db,
                    execution_id=execution.execution_id,
                    action="STEP_APPROVAL_REQUIRED",
                    actor="system",
                    target_type="STEP",
                    target_id=str(step.id),
                    previous_state=PlaybookExecutionStatus.RUNNING,
                    new_state=PlaybookExecutionStatus.WAITING_APPROVAL,
                    reason=execution.approval_reason,
                )
                failed_or_paused = True
                break

            # Execute step with retry mechanism (max 2 retries)
            max_retries = min(max(step.retry_count, 0), 2)
            step_success = False
            last_error: str | None = None
            step_output: dict[str, Any] = {}

            # Prepare step parameters
            step_params: dict[str, Any] = {}
            if step.parameters_json:
                try:
                    step_params = json.loads(step.parameters_json)
                except (json.JSONDecodeError, ValueError, TypeError):
                    step_params = {}

            # Interpolate context into parameters if string references exist
            interpolated_params = cls._interpolate_params(step_params, context)

            for attempt in range(max_retries + 1):
                try:
                    step_output = ActionHandlerRegistry.execute(
                        db=db,
                        action_type=step.action_type,
                        parameters=interpolated_params,
                        context=context,
                    )
                    step_success = True
                    break
                except Exception as e:  # noqa: BLE001
                    last_error = f"{type(e).__name__}: {e!s}"
                    logger.error(
                        "Execution %s Step %s attempt %d failed: %s",
                        execution.execution_id,
                        step.name,
                        attempt,
                        last_error,
                    )

            if step_success:
                cls._record_step_log(
                    db=db,
                    execution=execution,
                    step=step,
                    status=StepExecutionStatus.COMPLETED,
                    input_summary=json.dumps(interpolated_params),
                    output_summary=json.dumps(step_output),
                )
                context["step_results"][step.name] = step_output
                context.update(step_output)
                executed_count += 1
            else:
                cls._record_step_log(
                    db=db,
                    execution=execution,
                    step=step,
                    status=StepExecutionStatus.FAILED,
                    input_summary=json.dumps(interpolated_params),
                    error_code="ACTION_ERROR",
                    error_message=last_error or "Unknown step execution failure",
                    retry_attempt=max_retries,
                )

                if step.on_failure == "STOP":
                    execution.status = PlaybookExecutionStatus.FAILED
                    execution.error_message = (
                        f"Step {step.step_order} ('{step.name}') failed: {last_error}"
                    )
                    execution.completed_at = datetime.now(timezone.utc)
                    execution.result_summary = f"Playbook halted at step {step.step_order} due to error: {last_error}"
                    cls._save_artifacts(db, execution, context)
                    db.commit()

                    cls._log_audit(
                        db=db,
                        execution_id=execution.execution_id,
                        action="EXECUTION_FAILED",
                        actor="system",
                        target_type="PLAYBOOK_EXECUTION",
                        target_id=execution.execution_id,
                        previous_state=PlaybookExecutionStatus.RUNNING,
                        new_state=PlaybookExecutionStatus.FAILED,
                        reason=execution.error_message,
                    )
                    failed_or_paused = True
                    break
                else:
                    # CONTINUE on failure
                    logger.warning("Step %s failed but on_failure=CONTINUE. Continuing.", step.name)

        # Check if completed all steps
        if not failed_or_paused and execution.status != PlaybookExecutionStatus.WAITING_APPROVAL:
            execution.status = PlaybookExecutionStatus.COMPLETED
            execution.completed_at = datetime.now(timezone.utc)
            execution.result_summary = (
                f"Successfully completed {executed_count} steps for {playbook.name} in safe educational simulation."
            )
            cls._save_artifacts(db, execution, context)
            db.commit()

            cls._log_audit(
                db=db,
                execution_id=execution.execution_id,
                action="EXECUTION_COMPLETED",
                actor="system",
                target_type="PLAYBOOK_EXECUTION",
                target_id=execution.execution_id,
                previous_state=PlaybookExecutionStatus.RUNNING,
                new_state=PlaybookExecutionStatus.COMPLETED,
                reason=execution.result_summary,
            )

        db.refresh(execution)
        return execution

    @classmethod
    def _interpolate_params(cls, params: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Safely interpolate context variables into parameter strings."""
        result: dict[str, Any] = {}
        for k, v in params.items():
            if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
                field = v[2:-2].strip()
                val = SafeConditionEvaluator._get_field_value(field, context)
                result[k] = val if val is not None else v
            else:
                result[k] = v
        return result


    @classmethod
    def _save_artifacts(cls, db: Session, execution: PlaybookExecution, context: dict[str, Any]) -> None:
        """Persist accumulated context into artifacts_json."""
        try:
            # Strip non-serializable objects if any
            clean_context = json.loads(json.dumps(context, default=str))
            execution.artifacts_json = json.dumps({"context": clean_context, "step_results": clean_context.get("step_results", {})})
        except (TypeError, ValueError) as e:
            logger.warning("Could not serialize artifacts_json: %s", e)

    @classmethod
    def _record_step_log(
        cls,
        db: Session,
        execution: PlaybookExecution,
        step: AutomationStep,
        status: str,
        input_summary: str | None = None,
        output_summary: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
        retry_attempt: int = 0,
    ) -> ExecutionStepLog:
        """Create or update step execution log."""
        log = ExecutionStepLog(
            execution_id=execution.id,
            step_id=step.id,
            step_order=step.step_order,
            step_name=step.name,
            action_type=step.action_type,
            status=status,
            input_summary=input_summary,
            output_summary=output_summary,
            error_code=error_code,
            error_message=error_message,
            retry_attempt=retry_attempt,
            simulation_only=True,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()
        return log

    @classmethod
    def _log_audit(
        cls,
        db: Session,
        execution_id: str,
        action: str,
        actor: str,
        target_type: str,
        target_id: str,
        new_state: str | None = None,
        previous_state: str | None = None,
        reason: str | None = None,
    ) -> AutomationAuditLog:
        """Add immutable entry to automation audit trail."""
        audit = AutomationAuditLog(
            execution_id=execution_id,
            action=action,
            actor=actor,
            target_type=target_type,
            target_id=target_id,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
            simulation_only=True,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit)
        db.commit()
        return audit
