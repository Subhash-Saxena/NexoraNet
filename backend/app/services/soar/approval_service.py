"""Approval Workflow Service for SOAR Playbooks.

Enforces analyst authorization gates before potentially disruptive actions run.
Maintains an immutable audit log of approvals, rejections, and cancellations.
"""

from datetime import datetime, timezone

from app.models.enums import ApprovalStatus, PlaybookExecutionStatus
from app.models.soar import AutomationAuditLog, PlaybookExecution
from sqlalchemy.orm import Session


class ApprovalService:
    """Manages manual approval gates for high-risk educational SOAR playbooks."""

    @classmethod
    def request_approval(
        cls,
        db: Session,
        execution: PlaybookExecution,
        reason: str | None = None,
    ) -> PlaybookExecution:
        """Mark an execution as WAITING_APPROVAL and audit the event."""
        execution.status = PlaybookExecutionStatus.WAITING_APPROVAL
        execution.approval_status = ApprovalStatus.PENDING
        execution.approval_reason = reason or "Awaiting security analyst review and authorization"

        audit = AutomationAuditLog(
            execution_id=execution.execution_id,
            action="APPROVAL_REQUESTED",
            actor=execution.requested_by,
            target_type="PLAYBOOK_EXECUTION",
            target_id=execution.execution_id,
            previous_state=PlaybookExecutionStatus.RUNNING,
            new_state=PlaybookExecutionStatus.WAITING_APPROVAL,
            reason=execution.approval_reason,
            simulation_only=True,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit)
        db.commit()
        db.refresh(execution)
        return execution

    @classmethod
    def approve(
        cls,
        db: Session,
        execution_id: str,
        approver: str,
        reason: str | None = None,
    ) -> PlaybookExecution:
        """Approve an execution gate and allow it to proceed."""
        execution = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.execution_id == execution_id)
            .first()
        )
        if not execution:
            raise ValueError(f"Playbook execution '{execution_id}' not found.")

        if execution.status != PlaybookExecutionStatus.WAITING_APPROVAL:
            raise ValueError(
                f"Execution '{execution_id}' is not in WAITING_APPROVAL status (current: {execution.status})."
            )

        execution.status = PlaybookExecutionStatus.APPROVED
        execution.approved_by = approver
        execution.approval_status = ApprovalStatus.APPROVED
        execution.approved_at = datetime.now(timezone.utc)
        execution.approval_reason = reason or "Authorized by security analyst."

        audit = AutomationAuditLog(
            execution_id=execution.execution_id,
            action="APPROVED",
            actor=approver,
            target_type="PLAYBOOK_EXECUTION",
            target_id=execution.execution_id,
            previous_state=PlaybookExecutionStatus.WAITING_APPROVAL,
            new_state=PlaybookExecutionStatus.APPROVED,
            reason=execution.approval_reason,
            simulation_only=True,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit)
        db.commit()
        db.refresh(execution)
        return execution

    @classmethod
    def reject(
        cls,
        db: Session,
        execution_id: str,
        rejector: str,
        reason: str | None = None,
    ) -> PlaybookExecution:
        """Reject execution gate, cancelling further automation steps."""
        execution = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.execution_id == execution_id)
            .first()
        )
        if not execution:
            raise ValueError(f"Playbook execution '{execution_id}' not found.")

        if execution.status != PlaybookExecutionStatus.WAITING_APPROVAL:
            raise ValueError(
                f"Execution '{execution_id}' is not in WAITING_APPROVAL status (current: {execution.status})."
            )

        execution.status = PlaybookExecutionStatus.CANCELLED
        execution.approved_by = rejector
        execution.approval_status = ApprovalStatus.REJECTED
        execution.completed_at = datetime.now(timezone.utc)
        execution.approval_reason = reason or "Rejected by security analyst."
        execution.result_summary = f"Execution rejected by analyst {rejector}."

        audit = AutomationAuditLog(
            execution_id=execution.execution_id,
            action="REJECTED",
            actor=rejector,
            target_type="PLAYBOOK_EXECUTION",
            target_id=execution.execution_id,
            previous_state=PlaybookExecutionStatus.WAITING_APPROVAL,
            new_state=PlaybookExecutionStatus.CANCELLED,
            reason=execution.approval_reason,
            simulation_only=True,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit)
        db.commit()
        db.refresh(execution)
        return execution

    @classmethod
    def cancel(
        cls,
        db: Session,
        execution_id: str,
        actor: str,
        reason: str | None = None,
    ) -> PlaybookExecution:
        """Cancel an execution regardless of current pending status."""
        execution = (
            db.query(PlaybookExecution)
            .filter(PlaybookExecution.execution_id == execution_id)
            .first()
        )
        if not execution:
            raise ValueError(f"Playbook execution '{execution_id}' not found.")

        if execution.status in (
            PlaybookExecutionStatus.COMPLETED,
            PlaybookExecutionStatus.CANCELLED,
            PlaybookExecutionStatus.FAILED,
        ):
            raise ValueError(f"Execution '{execution_id}' is already finalized ({execution.status}).")

        prev_status = execution.status
        execution.status = PlaybookExecutionStatus.CANCELLED
        execution.completed_at = datetime.now(timezone.utc)
        execution.result_summary = reason or f"Cancelled by {actor}."

        audit = AutomationAuditLog(
            execution_id=execution.execution_id,
            action="CANCELLED",
            actor=actor,
            target_type="PLAYBOOK_EXECUTION",
            target_id=execution.execution_id,
            previous_state=prev_status,
            new_state=PlaybookExecutionStatus.CANCELLED,
            reason=reason,
            simulation_only=True,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit)
        db.commit()
        db.refresh(execution)
        return execution
