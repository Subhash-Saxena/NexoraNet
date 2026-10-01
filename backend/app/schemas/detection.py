"""Pydantic schemas for the Step 11 Network Detection Engine."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AlertConfidence,
    AlertSeverity,
    AlertStatus,
    DetectionRunStatus,
    EvidenceType,
    RuleCategory,
    RuleStatus,
)

# ============================================================================
# Detection Rule Schemas
# ============================================================================


class DetectionRuleBase(BaseModel):
    """Base fields for detection rules."""

    rule_id: str = Field(..., max_length=50, description="Unique code, e.g. NET-TCP-001")
    name: str = Field(..., max_length=200)
    description: str
    category: RuleCategory | str
    severity: AlertSeverity | str
    confidence_default: AlertConfidence | str = AlertConfidence.MEDIUM
    status: RuleStatus | str = RuleStatus.ENABLED
    logic_type: str = "THRESHOLD"
    conditions: dict[str, Any] = Field(default_factory=dict)
    threshold: float | None = None
    time_window_seconds: int | None = None
    mitre_attack_id: str | None = None
    mitre_technique: str | None = None
    explanation_template: str
    investigation_guide: str


class DetectionRuleCreate(DetectionRuleBase):
    """Request model to create or author a custom detection rule."""

    @field_validator("conditions", mode="before")
    @classmethod
    def parse_conditions(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return v


class DetectionRuleUpdate(BaseModel):
    """Request model to update an existing detection rule."""

    name: str | None = None
    description: str | None = None
    category: RuleCategory | str | None = None
    severity: AlertSeverity | str | None = None
    confidence_default: AlertConfidence | str | None = None
    status: RuleStatus | str | None = None
    logic_type: str | None = None
    conditions: dict[str, Any] | None = None
    threshold: float | None = None
    time_window_seconds: int | None = None
    mitre_attack_id: str | None = None
    mitre_technique: str | None = None
    explanation_template: str | None = None
    investigation_guide: str | None = None


class DetectionRuleResponse(DetectionRuleBase):
    """API response model for a detection rule."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_builtin: bool
    author_id: int | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("conditions", mode="before")
    @classmethod
    def parse_conditions(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return v


class DetectionRuleTestRequest(BaseModel):
    """Request parameters to test a rule against a capture without persisting alerts."""

    rule_id: str | None = None
    conditions: dict[str, Any] | None = None
    threshold: float | None = None
    time_window_seconds: int | None = None
    capture_id: int


class DetectionRuleTestResponse(BaseModel):
    """Simulation test results for a rule evaluation."""

    rule_id: str
    matches_found: int
    sample_matches: list[dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: int
    message: str


# ============================================================================
# Alert Evidence Schemas
# ============================================================================


class AlertEvidenceResponse(BaseModel):
    """Concrete evidence reference attached to a detection alert."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: int
    evidence_type: EvidenceType | str
    packet_id: int | None = None
    packet_number: int | None = None
    timestamp: float | None = None
    description: str
    evidence_data: dict[str, Any] | None = None
    created_at: datetime

    @field_validator("evidence_data", mode="before")
    @classmethod
    def parse_evidence_data(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return v


# ============================================================================
# Alert Notes & History Schemas
# ============================================================================


class AlertNoteCreate(BaseModel):
    """Request model for an analyst to append notes to an alert."""

    note: str = Field(..., min_length=1, max_length=4000)


class AlertNoteResponse(BaseModel):
    """Response model for an analyst note."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: int
    user_id: int | None = None
    author_name: str | None = None
    note: str
    created_at: datetime
    updated_at: datetime


class AlertStatusHistoryResponse(BaseModel):
    """Audit log entry for an alert triage state change."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: int
    user_id: int | None = None
    actor_name: str | None = None
    previous_status: str | None = None
    new_status: str
    reason: str | None = None
    created_at: datetime


class AlertStatusUpdateRequest(BaseModel):
    """Request body to change the workflow triage state of an alert."""

    status: AlertStatus | str
    reason: str | None = Field(None, max_length=1000)


# ============================================================================
# Detection Alert Schemas
# ============================================================================


class DetectionAlertListItem(BaseModel):
    """Summarized alert model for lists and dashboards."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int
    rule_id: int
    rule_code: str | None = None
    title: str
    category: RuleCategory | str
    severity: AlertSeverity | str
    confidence: AlertConfidence | str
    status: AlertStatus | str
    source_ip: str | None = None
    source_port: int | None = None
    destination_ip: str | None = None
    destination_port: int | None = None
    protocol: str | None = None
    first_seen_timestamp: float | None = None
    last_seen_timestamp: float | None = None
    packet_count: int = 1
    created_at: datetime


class DetectionAlertDetail(DetectionAlertListItem):
    """Full deep-inspection model for an individual detection alert."""

    explanation: str
    mitre_attack_id: str | None = None
    mitre_technique: str | None = None
    investigation_steps: list[str] = Field(default_factory=list)
    evidence: list[AlertEvidenceResponse] = Field(default_factory=list)
    notes: list[AlertNoteResponse] = Field(default_factory=list)
    status_history: list[AlertStatusHistoryResponse] = Field(default_factory=list)

    @field_validator("investigation_steps", mode="before")
    @classmethod
    def parse_investigation_steps(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                res = json.loads(v)
                if isinstance(res, list):
                    return res
                return [res]
            except (json.JSONDecodeError, TypeError, ValueError):
                return [v]
        return v or []


# ============================================================================
# Detection Run Schemas
# ============================================================================


class DetectionRunCreate(BaseModel):
    """Request model to initiate a detection analysis run."""

    source_type: str = Field(default="PCAP", description="'PCAP' or 'SIMULATOR'")
    capture_id: int | None = None
    simulation_scenario_id: int | None = None
    rule_ids: list[str] | None = Field(default=None, description="Optional rule codes filter")


class DetectionRunResponse(BaseModel):
    """Execution status and summary for a detection run."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    source_type: str
    capture_id: int | None = None
    simulation_scenario_id: int | None = None
    status: DetectionRunStatus | str
    rules_evaluated: int
    rules_matched: int
    alerts_generated: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int
    error_message: str | None = None
    summary: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("summary", mode="before")
    @classmethod
    def parse_summary(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return v


# ============================================================================
# Statistics & Analytics Schemas
# ============================================================================


class DetectionStatsResponse(BaseModel):
    """Overall statistics for the detection engine and SOC analyst dashboard."""

    total_runs: int = 0
    total_alerts: int = 0
    active_alerts: int = 0
    alerts_by_severity: dict[str, int] = Field(default_factory=dict)
    alerts_by_category: dict[str, int] = Field(default_factory=dict)
    alerts_by_status: dict[str, int] = Field(default_factory=dict)
    top_matching_rules: list[dict[str, Any]] = Field(default_factory=list)
    recent_alerts: list[DetectionAlertListItem] = Field(default_factory=list)
