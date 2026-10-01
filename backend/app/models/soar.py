"""Database models for Step 18 SOAR Security Automation Engine.

Simulates educational Security Orchestration, Automation, and Response.
Strictly offline and non-destructive.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import (
    PlaybookExecutionStatus,
    PlaybookRiskLevel,
    PlaybookStatus,
    PlaybookTriggerType,
    StepExecutionStatus,
)


class AutomationPlaybook(TimeStampedModel):
    """Educational SOAR Playbook definition."""

    __tablename__ = "automation_playbooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    playbook_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=PlaybookStatus.ENABLED, nullable=False, index=True
    )
    trigger_type: Mapped[str] = mapped_column(
        String(50), default=PlaybookTriggerType.ALERT_CREATED, nullable=False, index=True
    )
    trigger_filter_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(
        String(20), default=PlaybookRiskLevel.LOW, nullable=False
    )
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    simulation_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)

    # Relationships
    steps: Mapped[list["AutomationStep"]] = relationship(
        "AutomationStep",
        back_populates="playbook",
        cascade="all, delete-orphan",
        order_by="AutomationStep.step_order",
    )
    executions: Mapped[list["PlaybookExecution"]] = relationship(
        "PlaybookExecution", back_populates="playbook", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AutomationPlaybook {self.playbook_id}: {self.name}>"


class AutomationStep(TimeStampedModel):
    """Discrete sequential step inside an automation playbook."""

    __tablename__ = "automation_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    playbook_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("automation_playbooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    condition_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    on_failure: Mapped[str] = mapped_column(String(20), default="STOP", nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    playbook: Mapped["AutomationPlaybook"] = relationship("AutomationPlaybook", back_populates="steps")

    def __repr__(self) -> str:
        return f"<AutomationStep {self.step_order}: {self.name} ({self.action_type})>"


class PlaybookExecution(TimeStampedModel):
    """Record of a playbook run against an alert, IOC, or incident."""

    __tablename__ = "playbook_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    execution_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    playbook_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("automation_playbooks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trigger_source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(30), default=PlaybookExecutionStatus.QUEUED, nullable=False, index=True
    )
    current_step_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    requested_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approval_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    approval_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    simulation_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    artifacts_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    playbook: Mapped["AutomationPlaybook"] = relationship("AutomationPlaybook", back_populates="executions")
    step_logs: Mapped[list["ExecutionStepLog"]] = relationship(
        "ExecutionStepLog",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="ExecutionStepLog.step_order",
    )

    def __repr__(self) -> str:
        return f"<PlaybookExecution {self.execution_id}: {self.status}>"


class ExecutionStepLog(TimeStampedModel):
    """Audit and output log for an individual executed step."""

    __tablename__ = "execution_step_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    execution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("playbook_executions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("automation_steps.id", ondelete="SET NULL"), nullable=True
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default=StepExecutionStatus.RUNNING, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_attempt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    simulation_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    execution: Mapped["PlaybookExecution"] = relationship("PlaybookExecution", back_populates="step_logs")

    def __repr__(self) -> str:
        return f"<ExecutionStepLog Step {self.step_order} ({self.status})>"


class AutomationAuditLog(TimeStampedModel):
    """Immutable audit trail for all SOAR automation events and state transitions."""

    __tablename__ = "automation_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    execution_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(100), nullable=False)
    previous_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    simulation_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<AutomationAuditLog {self.action} on {self.target_id} by {self.actor}>"
