"""Pydantic v2 schemas for Step 17 Incident Response, Case Management & MITRE ATT&CK."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# MITRE ATT&CK Schemas
# ---------------------------------------------------------------------------
class AttackTechniqueBriefResponse(BaseModel):
    id: int
    technique_id: str
    name: str
    is_subtechnique: bool
    parent_technique_id: str | None = None
    platforms: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AttackTechniqueResponse(BaseModel):
    id: int
    technique_id: str
    tactic_id: int
    name: str
    description: str
    detection_guidance: str | None = None
    mitigation_guidance: str | None = None
    is_subtechnique: bool
    parent_technique_id: str | None = None
    platforms: str | None = None
    data_sources: str | None = None
    external_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AttackTacticResponse(BaseModel):
    id: int
    tactic_id: str
    name: str
    description: str
    external_url: str | None = None
    display_order: int
    techniques: list[AttackTechniqueResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TechniqueMappingRequest(BaseModel):
    technique_id_or_code: str | int
    mapping_confidence: str = "OBSERVED_EVIDENCE"
    evidence_summary: str | None = None
    phase: str | None = None


class IncidentTechniqueMappingResponse(BaseModel):
    id: int
    incident_id: int
    technique_id: int
    mapping_confidence: str
    evidence_summary: str | None = None
    phase: str | None = None
    mapped_at: datetime
    technique: AttackTechniqueResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Playbook Schemas
# ---------------------------------------------------------------------------
class IncidentPlaybookResponse(BaseModel):
    id: int
    playbook_id: str
    title: str
    description: str
    category: str
    severity_guidance: str
    primary_tactic_id: str | None = None
    phases_definition: str
    checklist_json: str
    recommended_actions_json: str
    version: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Evidence & Chain of Custody Schemas
# ---------------------------------------------------------------------------
class EvidenceAuditLogResponse(BaseModel):
    id: int
    evidence_id: int
    action: str
    details: str | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentEvidenceCreate(BaseModel):
    title: str
    description: str
    evidence_type: str
    source_engine: str
    source_id: str | None = None
    source_ref: str | None = None
    data_payload: Any = None
    relevance: str = "SUPPORTING"


class IncidentEvidenceUpdate(BaseModel):
    relevance: str | None = None
    is_contained: bool | None = None
    description: str | None = None


class IncidentEvidenceResponse(BaseModel):
    id: int
    evidence_id: str
    incident_id: int
    title: str
    description: str
    evidence_type: str
    source_engine: str
    source_id: str | None = None
    source_ref: str | None = None
    hash_sha256: str | None = None
    relevance: str
    is_contained: bool
    collected_at: datetime
    data_payload: str | None = None
    audit_logs: list[EvidenceAuditLogResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Timeline Schemas
# ---------------------------------------------------------------------------
class IncidentTimelineEventCreate(BaseModel):
    timestamp: datetime
    title: str
    description: str
    event_category: str = "OBSERVATION"
    source: str = "ANALYST"
    source_id: str | None = None
    mitre_technique_id: str | None = None
    is_milestone: bool = False


class IncidentTimelineEventResponse(BaseModel):
    id: int
    incident_id: int
    timestamp: datetime
    title: str
    description: str
    event_category: str
    source: str
    source_id: str | None = None
    mitre_technique_id: str | None = None
    is_milestone: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Response Action Schemas
# ---------------------------------------------------------------------------
class ResponseActionPropose(BaseModel):
    category: str
    action_type: str
    target_type: str
    target_identifier: str
    reason: str
    risk_assessment: str | None = None
    expected_impact: str | None = None


class ResponseActionResponse(BaseModel):
    id: int
    action_id: str
    incident_id: int
    category: str
    action_type: str
    target_type: str
    target_identifier: str
    status: str
    simulation_only: bool
    reason: str
    risk_assessment: str | None = None
    expected_impact: str | None = None
    simulated_outcome: str | None = None
    executed_at: datetime | None = None
    reverted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Hypothesis & Finding Schemas
# ---------------------------------------------------------------------------
class IncidentHypothesisCreate(BaseModel):
    statement: str
    confidence: str = "MEDIUM"
    rationale: str | None = None


class IncidentHypothesisUpdate(BaseModel):
    status: str
    confidence: str | None = None
    rationale: str | None = None


class IncidentHypothesisResponse(BaseModel):
    id: int
    hypothesis_id: str
    incident_id: int
    statement: str
    status: str
    confidence: str
    rationale: str | None = None
    tested_at: datetime | None = None
    concluded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class IncidentFindingCreate(BaseModel):
    title: str
    description: str
    severity: str = "MEDIUM"
    confidence: str = "HIGH"
    affected_systems: str | None = None
    affected_accounts: str | None = None
    indicators_observed: str | None = None
    mitre_technique: str | None = None
    mitre_tactic: str | None = None


class IncidentFindingResponse(BaseModel):
    id: int
    finding_id: str
    incident_id: int
    title: str
    description: str
    severity: str
    confidence: str
    affected_systems: str | None = None
    affected_accounts: str | None = None
    indicators_observed: str | None = None
    mitre_technique: str | None = None
    mitre_tactic: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Note & Alert Links
# ---------------------------------------------------------------------------
class IncidentNoteCreate(BaseModel):
    note: str


class IncidentNoteResponse(BaseModel):
    id: int
    incident_id: int
    user_id: int | None = None
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentAlertResponse(BaseModel):
    id: int
    incident_id: int
    alert_id: int
    role: str
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Incident Core Schemas
# ---------------------------------------------------------------------------
class IncidentCreate(BaseModel):
    title: str
    description: str
    incident_type: str = "NETWORK_INTRUSION"
    severity: str = "MEDIUM"
    priority: str = "P2"
    playbook_id: int | None = None
    case_id: int | None = None
    lead_analyst: str | None = None
    detected_at: datetime | None = None


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    incident_type: str | None = None
    severity: str | None = None
    priority: str | None = None
    status: str | None = None
    phase: str | None = None
    classification: str | None = None
    lead_analyst: str | None = None
    summary: str | None = None
    impact_assessment: str | None = None
    root_cause: str | None = None
    lessons_learned: str | None = None
    recommendations: str | None = None
    assigned_to_id: int | None = None
    playbook_id: int | None = None
    case_id: int | None = None


class EscalateAlertRequest(BaseModel):
    alert_id: int
    title: str | None = None
    severity: str | None = None
    playbook_id: int | None = None


class IncidentBriefResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    description: str
    incident_type: str
    severity: str
    priority: str
    status: str
    phase: str
    classification: str
    lead_analyst: str | None = None
    detected_at: datetime
    contained_at: datetime | None = None
    closed_at: datetime | None = None
    simulation_mode: bool
    evidence_count: int = 0
    actions_count: int = 0
    techniques_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class IncidentDetailResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    description: str
    incident_type: str
    severity: str
    priority: str
    status: str
    phase: str
    classification: str
    case_id: int | None = None
    assigned_to_id: int | None = None
    playbook_id: int | None = None
    lead_analyst: str | None = None
    detected_at: datetime
    contained_at: datetime | None = None
    eradicated_at: datetime | None = None
    recovered_at: datetime | None = None
    closed_at: datetime | None = None
    summary: str | None = None
    impact_assessment: str | None = None
    root_cause: str | None = None
    lessons_learned: str | None = None
    recommendations: str | None = None
    simulation_mode: bool
    playbook: IncidentPlaybookResponse | None = None
    alerts: list[IncidentAlertResponse] = Field(default_factory=list)
    evidence: list[IncidentEvidenceResponse] = Field(default_factory=list)
    timeline_events: list[IncidentTimelineEventResponse] = Field(default_factory=list)
    hypotheses: list[IncidentHypothesisResponse] = Field(default_factory=list)
    findings: list[IncidentFindingResponse] = Field(default_factory=list)
    response_actions: list[ResponseActionResponse] = Field(default_factory=list)
    technique_mappings: list[IncidentTechniqueMappingResponse] = Field(default_factory=list)
    notes: list[IncidentNoteResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class IncidentListResponse(BaseModel):
    items: list[IncidentDetailResponse]
    total: int
    skip: int
    limit: int
