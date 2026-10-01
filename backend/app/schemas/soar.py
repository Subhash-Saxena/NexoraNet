"""Pydantic schemas for Step 18 SOAR Security Automation Engine.

Supports educational playbooks, step logs, approvals, dry-run testing, and KPIs.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    PlaybookRiskLevel,
    PlaybookStatus,
    PlaybookTriggerType,
)


# --- Step Schemas ---
class AutomationStepBase(BaseModel):
    step_order: int
    name: str
    description: str | None = None
    action_type: str
    parameters_json: str | None = None
    condition_json: str | None = None
    requires_approval: bool = False
    timeout_seconds: int = 30
    enabled: bool = True
    on_failure: str = "STOP"
    retry_count: int = 0


class AutomationStepCreate(AutomationStepBase):
    parameters: dict[str, Any] | None = None
    condition: dict[str, Any] | None = None


class AutomationStepResponse(AutomationStepBase):
    id: int
    playbook_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



# --- Playbook Schemas ---
class AutomationPlaybookBase(BaseModel):
    name: str
    description: str
    category: str
    version: str = "1.0"
    status: str = PlaybookStatus.ENABLED
    trigger_type: str = PlaybookTriggerType.ALERT_CREATED
    trigger_filter_json: str | None = None
    risk_level: str = PlaybookRiskLevel.LOW
    requires_approval: bool = False


class AutomationPlaybookCreate(BaseModel):
    name: str
    description: str
    category: str
    trigger_type: str = PlaybookTriggerType.ALERT_CREATED
    trigger_filter: dict[str, Any] | None = None
    risk_level: str = PlaybookRiskLevel.LOW
    requires_approval: bool = False
    steps: list[dict[str, Any]] | None = None


class AutomationPlaybookUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    status: str | None = None
    risk_level: str | None = None
    requires_approval: bool | None = None


class AutomationPlaybookResponse(AutomationPlaybookBase):
    id: int
    playbook_id: str
    is_system: bool
    simulation_only: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    steps_count: int = 0

    model_config = ConfigDict(from_attributes=True)



class AutomationPlaybookDetailResponse(AutomationPlaybookResponse):
    steps: list[AutomationStepResponse] = []


# --- Execution Step Log Schemas ---
class ExecutionStepLogResponse(BaseModel):
    id: int
    execution_id: int
    step_id: int | None
    step_order: int
    step_name: str
    action_type: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    input_summary: str | None
    output_summary: str | None
    error_code: str | None
    error_message: str | None
    retry_attempt: int
    simulation_only: bool

    model_config = ConfigDict(from_attributes=True)



# --- Execution Schemas ---
class PlaybookExecutionTriggerRequest(BaseModel):
    playbook_id: str
    trigger_source: str = "ALERT"
    source_id: str
    idempotency_key: str | None = None
    context: dict[str, Any] | None = None


class PlaybookExecutionResponse(BaseModel):
    id: int
    execution_id: str
    playbook_id: int
    playbook_identifier: str = ""
    playbook_name: str = ""
    trigger_source: str
    source_id: str
    status: str
    current_step_order: int
    total_steps: int
    requested_by: str
    approved_by: str | None
    approval_status: str | None
    approval_reason: str | None
    started_at: datetime
    completed_at: datetime | None
    simulation_only: bool
    result_summary: str | None
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)



class PlaybookExecutionDetailResponse(PlaybookExecutionResponse):
    artifacts_json: str | None
    step_logs: list[ExecutionStepLogResponse] = []


# --- Approval Schemas ---
class ApprovalActionRequest(BaseModel):
    reason: str | None = Field(default=None, description="Analyst rationale for approval or rejection")


# --- Dry Run Schemas ---
class DryRunRequest(BaseModel):
    mock_input: dict[str, Any] = Field(default_factory=dict)


class DryRunStepResult(BaseModel):
    step_order: int
    step_name: str
    action_type: str
    condition_met: bool
    requires_approval: bool
    status_preview: str
    parameters_preview: dict[str, Any]


class DryRunResponse(BaseModel):
    playbook_id: str
    playbook_name: str
    dry_run: bool
    total_steps: int
    executable_steps: int
    simulated_steps: list[DryRunStepResult]


# --- Audit & Metrics Schemas ---
class AutomationAuditLogResponse(BaseModel):
    id: int
    execution_id: str
    action: str
    actor: str
    target_type: str
    target_id: str
    previous_state: str | None
    new_state: str | None
    reason: str | None
    simulation_only: bool
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)



class SoarMetricsResponse(BaseModel):
    total_playbooks: int
    enabled_playbooks: int
    total_executions: int
    completed_executions: int
    waiting_approval: int
    failed_executions: int
    success_rate_percent: float
    analyst_hours_saved: float
    top_playbooks: list[dict[str, Any]]
