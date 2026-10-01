"""Pydantic request and response schemas for Step 12 SOC Dashboard & Triage."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    AlertStatus,
    CaseStatus,
    FindingConfidence,
    HypothesisStatus,
    InvestigationAlertRelationship,
    InvestigationStatus,
    TrainingPriority,
    TriageClassification,
)

# ==============================================================================
# Overview & Metrics Schemas
# ==============================================================================


class SocOverviewMetrics(BaseModel):
    """Aggregate high-level metrics for the SOC dashboard."""

    total_alerts: int
    new_alerts: int
    acknowledged_alerts: int
    investigating_alerts: int
    closed_alerts: int
    false_positives: int
    p1_alerts: int
    p2_alerts: int
    p3_alerts: int
    p4_alerts: int
    open_investigations: int
    active_cases: int
    packets_analyzed_total: int
    flows_analyzed_total: int
    active_rules_count: int


class SocOverviewResponse(BaseModel):
    """Full payload for GET /api/v1/soc/overview."""

    environment_status: str = "Offline Training Environment"
    safety_disclaimer: str = (
        "All events shown here are synthetic or derived from offline PCAP telemetry analysis. "
        "No live monitoring, interception, or real-world response is performed."
    )
    metrics: SocOverviewMetrics
    priority_alerts: list["SocAlertItem"] = []
    recent_runs: list[dict[str, Any]] = []
    recent_investigations: list["InvestigationBriefResponse"] = []
    learning_recommendations: list[dict[str, str]] = []


class SocStatisticsResponse(BaseModel):
    """Statistical distributions for dashboard charts."""

    alerts_by_severity: dict[str, int]
    alerts_by_category: dict[str, int]
    alerts_by_priority: dict[str, int]
    alerts_by_status: dict[str, int]
    alerts_by_classification: dict[str, int]
    alerts_by_protocol: dict[str, int]
    top_sources: list[dict[str, Any]]
    top_destinations: list[dict[str, Any]]
    average_evidence_count: float
    average_investigation_duration_minutes: float
    trend_over_time: list[dict[str, Any]]


class SocActivityItem(BaseModel):
    """Timeline activity feed item."""

    id: str
    activity_type: str
    title: str
    description: str
    timestamp: datetime
    reference_type: str | None = None
    reference_id: str | None = None
    actor_name: str | None = None


# ==============================================================================
# Alert Queue & Details Schemas
# ==============================================================================


class SocAlertItem(BaseModel):
    """List item for the SOC analyst alert queue."""

    id: int
    run_id: int
    rule_id: int
    rule_code: str | None = None
    capture_id: int | None = None
    title: str
    category: str
    severity: str
    confidence: str
    status: str
    classification: str
    priority: str
    priority_reason: str | None = None
    assigned_to_id: int | None = None
    assigned_to_name: str | None = None
    source_ip: str | None = None
    source_port: int | None = None
    destination_ip: str | None = None
    destination_port: int | None = None
    protocol: str | None = None
    first_seen_timestamp: float | None = None
    last_seen_timestamp: float | None = None
    packet_count: int
    evidence_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertTimelineEvent(BaseModel):
    """Chronological event in the alert timeline."""

    timestamp: datetime | float
    time_display: str
    event_type: str
    title: str
    description: str
    actor_name: str | None = None


class RelatedAlertItem(BaseModel):
    """Correlated related alert."""

    id: int
    title: str
    category: str
    severity: str
    priority: str
    status: str
    source_ip: str | None = None
    destination_ip: str | None = None
    correlation_reason: str
    created_at: datetime


class EndpointContext(BaseModel):
    """Network statistics and context for an endpoint."""

    ip: str
    packet_count: int
    byte_count: int
    protocols: list[str]
    ports: list[int]
    first_seen: float | None = None
    last_seen: float | None = None


class NetworkContextResponse(BaseModel):
    """Source and destination endpoint context."""

    source: EndpointContext | None = None
    destination: EndpointContext | None = None
    conversation_summary: str | None = None


class SocAlertDetailResponse(SocAlertItem):
    """Comprehensive alert view for triage and forensic analysis."""

    explanation: str
    mitre_attack_id: str | None = None
    mitre_technique: str | None = None
    investigation_steps: list[str] = []
    rule_description: str | None = None
    evidence: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []
    status_history: list[dict[str, Any]] = []
    timeline: list[AlertTimelineEvent] = []
    related_alerts: list[RelatedAlertItem] = []
    network_context: NetworkContextResponse
    investigations: list["InvestigationBriefResponse"] = []


class AlertAcknowledgeRequest(BaseModel):
    """Request to acknowledge an alert."""

    reason: str | None = "Acknowledged by analyst for triage."


class AlertClassificationRequest(BaseModel):
    """Request to classify an alert and optionally transition its status."""

    classification: TriageClassification
    reason: str
    status: AlertStatus | None = None


class AlertBulkActionRequest(BaseModel):
    """Safe bulk operations on alerts."""

    alert_ids: list[int]
    action: str = Field(..., description="'ACKNOWLEDGE', 'ASSIGN', 'CLOSE', or 'SET_CLASSIFICATION'")
    assigned_to_id: int | None = None
    classification: TriageClassification | None = None
    status: AlertStatus | None = None
    reason: str | None = None


# ==============================================================================
# Investigation Schemas
# ==============================================================================


class InvestigationBriefResponse(BaseModel):
    """Lightweight summary of an investigation."""

    id: int
    investigation_id: str
    title: str
    status: str
    priority: str
    classification: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationHypothesisResponse(BaseModel):
    """An analytical hypothesis formulated in an investigation."""

    id: int
    investigation_id: int
    hypothesis_text: str
    status: str
    reasoning: str | None = None
    supporting_evidence_ids: list[str] = []
    created_by_name: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationFindingResponse(BaseModel):
    """Substantiated finding in an investigation."""

    id: int
    investigation_id: int
    title: str
    description: str
    evidence_summary: str | None = None
    confidence: str
    created_by_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationEvidenceResponse(BaseModel):
    """Granular evidence item referenced in an investigation."""

    id: int
    investigation_id: int
    evidence_type: str
    reference_id: str | None = None
    capture_id: int | None = None
    packet_number: int | None = None
    description: str
    evidence_data: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationNoteResponse(BaseModel):
    """Analyst note inside an investigation."""

    id: int
    investigation_id: int
    user_id: int | None = None
    author_name: str | None = None
    note: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationDetailResponse(BaseModel):
    """Full detail view of an investigation."""

    id: int
    investigation_id: str
    title: str
    description: str
    status: str
    priority: str
    classification: str
    created_by_id: int | None = None
    created_by_name: str | None = None
    assigned_to_id: int | None = None
    assigned_to_name: str | None = None
    started_at: datetime
    closed_at: datetime | None = None
    conclusion: str | None = None
    recommendations: str | None = None
    created_at: datetime
    updated_at: datetime
    alerts: list[SocAlertItem] = []
    evidence: list[InvestigationEvidenceResponse] = []
    hypotheses: list[InvestigationHypothesisResponse] = []
    findings: list[InvestigationFindingResponse] = []
    notes: list[InvestigationNoteResponse] = []
    cases: list[dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)


class InvestigationCreateRequest(BaseModel):
    """Payload to create an investigation."""

    title: str
    description: str
    priority: TrainingPriority = TrainingPriority.P3
    alert_ids: list[int] = []
    case_id: int | None = None


class InvestigationUpdateRequest(BaseModel):
    """Payload to update an investigation."""

    title: str | None = None
    description: str | None = None
    status: InvestigationStatus | None = None
    priority: TrainingPriority | None = None
    classification: TriageClassification | None = None
    conclusion: str | None = None
    recommendations: str | None = None
    assigned_to_id: int | None = None


class InvestigationAlertAddRequest(BaseModel):
    """Add alert to investigation."""

    alert_id: int
    relationship_type: InvestigationAlertRelationship = InvestigationAlertRelationship.RELATED


class InvestigationEvidenceAddRequest(BaseModel):
    """Add evidence reference to investigation."""

    evidence_type: str
    reference_id: str | None = None
    capture_id: int | None = None
    packet_number: int | None = None
    description: str
    evidence_data: dict[str, Any] | None = None


class InvestigationHypothesisCreateRequest(BaseModel):
    """Create a new hypothesis."""

    hypothesis_text: str
    status: HypothesisStatus = HypothesisStatus.UNTESTED
    reasoning: str | None = None
    supporting_evidence_ids: list[str] = []


class InvestigationHypothesisUpdateRequest(BaseModel):
    """Update hypothesis status or reasoning."""

    status: HypothesisStatus | None = None
    reasoning: str | None = None
    supporting_evidence_ids: list[str] | None = None


class InvestigationFindingCreateRequest(BaseModel):
    """Create a substantiated finding."""

    title: str
    description: str
    evidence_summary: str | None = None
    confidence: FindingConfidence = FindingConfidence.MEDIUM


class InvestigationNoteCreateRequest(BaseModel):
    """Create a note in an investigation."""

    note: str


# ==============================================================================
# Case Schemas
# ==============================================================================


class CaseBriefResponse(BaseModel):
    """Summary of a case."""

    id: int
    case_id: str
    title: str
    status: str
    priority: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseDetailResponse(BaseModel):
    """Detailed case representation."""

    id: int
    case_id: str
    title: str
    description: str
    status: str
    priority: str
    created_by_name: str | None = None
    assigned_to_name: str | None = None
    summary: str | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    alerts: list[SocAlertItem] = []
    investigations: list[InvestigationBriefResponse] = []
    notes: list[dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)


class CaseCreateRequest(BaseModel):
    """Payload to create a case."""

    title: str
    description: str
    priority: TrainingPriority = TrainingPriority.P3
    alert_ids: list[int] = []
    investigation_ids: list[int] = []


class CaseUpdateRequest(BaseModel):
    """Payload to update a case."""

    title: str | None = None
    description: str | None = None
    status: CaseStatus | None = None
    priority: TrainingPriority | None = None
    summary: str | None = None
    assigned_to_id: int | None = None


class CaseAlertAddRequest(BaseModel):
    """Add alert to case."""

    alert_id: int


class CaseInvestigationAddRequest(BaseModel):
    """Add investigation to case."""

    investigation_id: int


class CaseNoteCreateRequest(BaseModel):
    """Create note in case."""

    note: str


# ==============================================================================
# Detection Coverage Schemas
# ==============================================================================


class CategoryCoverageItem(BaseModel):
    """Detection rule coverage per category."""

    category: str
    total_rules: int
    active_rules: int
    severity_distribution: dict[str, int]
    mitre_techniques: list[str]


class DetectionCoverageResponse(BaseModel):
    """Overall training detection coverage matrix."""

    disclaimer: str = "Current NexoraNet training detection coverage."
    categories: list[CategoryCoverageItem]
    total_rules: int
    active_rules: int


# ==============================================================================
# Audit & Notification Schemas
# ==============================================================================


class SocAuditLogResponse(BaseModel):
    """Audit log entry."""

    id: int
    actor_name: str
    action: str
    object_type: str
    object_id: str
    details: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SocNotificationResponse(BaseModel):
    """In-app SOC notification."""

    id: int
    title: str
    message: str
    notification_type: str
    reference_type: str | None = None
    reference_id: str | None = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# SOC Challenge Scenarios & Datasets Schemas
# ==============================================================================


class SocChallengeResponse(BaseModel):
    """SOC challenge overview."""

    id: int
    slug: str
    title: str
    description: str
    scenario_type: str
    difficulty: str
    capture_id: int | None = None
    instructions: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SocChallengeDetailResponse(SocChallengeResponse):
    """Detailed SOC challenge with associated telemetry."""

    expected_observations: list[str] = []
    sample_alerts: list[SocAlertItem] = []
    capture_name: str | None = None


class SocChallengeSubmitRequest(BaseModel):
    """Student submission for SOC challenge evaluation."""

    investigation_id: int
    identified_evidence: list[str]
    observations: str
    hypothesis: str
    classification: TriageClassification
    conclusion: str


class SocChallengeResultResponse(BaseModel):
    """Educational feedback and score for a challenge submission."""

    attempt_id: int
    challenge_id: int
    status: str
    score: float
    score_breakdown: dict[str, float]
    what_you_did_well: list[str]
    evidence_identified: list[str]
    investigation_steps_completed: list[str]
    suggested_review: list[dict[str, str]]


class TrainingDatasetItem(BaseModel):
    """Pre-built training dataset specification."""

    dataset_id: str
    name: str
    category: str
    description: str
    packet_count: int
    alert_count: int
    is_active: bool = False
