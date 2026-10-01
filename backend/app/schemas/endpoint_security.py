"""Pydantic schemas for Step 16 Endpoint Security & Host Investigation Engine."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Host Schemas
# ---------------------------------------------------------------------------
class EndpointHostResponse(BaseModel):
    id: int
    stable_id: str
    hostname: str
    display_name: str
    platform: str
    platform_version: str
    architecture: str
    environment: str
    status: str
    risk_level: str
    ip_address: str | None = None
    mac_address: str | None = None
    os_build: str | None = None
    description: str
    last_activity_at: datetime | None = None
    is_synthetic: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EndpointHostListResponse(BaseModel):
    items: list[EndpointHostResponse]
    total: int
    skip: int
    limit: int


# ---------------------------------------------------------------------------
# Event Schemas
# ---------------------------------------------------------------------------
class EndpointEventResponse(BaseModel):
    id: int
    event_id: str
    host_id: int
    timestamp: datetime
    event_type: str
    event_category: str
    username: str | None = None
    process_name: str | None = None
    process_id: int | None = None
    parent_process_id: int | None = None
    parent_process_name: str | None = None
    command_summary: str | None = None
    integrity_level: str | None = None
    file_name: str | None = None
    file_path: str | None = None
    file_hash: str | None = None
    file_action: str | None = None
    source_ip: str | None = None
    source_port: int | None = None
    destination_ip: str | None = None
    destination_port: int | None = None
    protocol: str | None = None
    domain: str | None = None
    dns_query_type: str | None = None
    dns_response: str | None = None
    service_name: str | None = None
    service_display_name: str | None = None
    service_action: str | None = None
    persistence_type: str | None = None
    auth_method: str | None = None
    auth_failure_reason: str | None = None
    action: str | None = None
    result: str | None = None
    severity: str
    raw_event_reference: str | None = None
    metadata_json: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EndpointEventListResponse(BaseModel):
    items: list[EndpointEventResponse]
    total: int
    skip: int
    limit: int


class EndpointAuthenticationResponse(BaseModel):
    total: int
    events: list[EndpointEventResponse]
    summary: dict[str, Any]


# ---------------------------------------------------------------------------
# Investigation Schemas
# ---------------------------------------------------------------------------
class EndpointHypothesisResponse(BaseModel):
    id: int
    investigation_id: int
    statement: str
    status: str
    confidence: str
    analyst_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EndpointEvidenceResponse(BaseModel):
    id: int
    investigation_id: int
    hypothesis_id: int | None = None
    event_id: int | None = None
    evidence_type: str
    title: str
    description: str
    relevance: str
    artifact_data_json: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EndpointFindingResponse(BaseModel):
    id: int
    investigation_id: int
    title: str
    narrative: str
    mitre_attack_id: str | None = None
    severity: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EndpointConclusionResponse(BaseModel):
    id: int
    investigation_id: int
    summary: str
    verdict: str
    training_score: int
    score_breakdown_json: str | None = None
    lessons_learned: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EndpointInvestigationResponse(BaseModel):
    id: int
    stable_id: str
    host_id: int
    title: str
    description: str
    status: str
    priority: str
    user_id: int
    scenario_slug: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    host: EndpointHostResponse | None = None
    hypotheses: list[EndpointHypothesisResponse] = Field(default_factory=list)
    evidence: list[EndpointEvidenceResponse] = Field(default_factory=list)
    findings: list[EndpointFindingResponse] = Field(default_factory=list)
    conclusion: EndpointConclusionResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class EndpointInvestigationListResponse(BaseModel):
    items: list[EndpointInvestigationResponse]
    total: int
    skip: int
    limit: int


class EndpointInvestigationCreate(BaseModel):
    host_id: int
    title: str
    description: str
    priority: str = "P2"
    scenario_slug: str | None = None


class EndpointInvestigationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None


class EndpointHypothesisCreate(BaseModel):
    statement: str
    status: str = "OPEN"
    confidence: str = "MEDIUM"
    analyst_notes: str | None = None


class EndpointHypothesisUpdate(BaseModel):
    status: str | None = None
    confidence: str | None = None
    analyst_notes: str | None = None


class EndpointEvidenceCreate(BaseModel):
    title: str
    description: str
    evidence_type: str = "EVENT"
    relevance: str = "SUPPORTING"
    event_id: int | None = None
    hypothesis_id: int | None = None
    artifact_data: dict[str, Any] | None = None


class EndpointFindingCreate(BaseModel):
    title: str
    narrative: str
    mitre_attack_id: str | None = None
    severity: str = "MEDIUM"


class EndpointConclusionCreate(BaseModel):
    summary: str
    verdict: str
    lessons_learned: str | None = None


# ---------------------------------------------------------------------------
# Scenario Schemas
# ---------------------------------------------------------------------------
class EndpointScenarioResponse(BaseModel):
    id: int
    scenario_id: str
    slug: str
    title: str
    difficulty: str
    category: str
    target_host_stable_id: str
    description: str
    background: str
    objectives: list[str] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    estimated_minutes: int
    is_published: bool

    model_config = ConfigDict(from_attributes=True)


class ScenarioValidateRequest(BaseModel):
    answers: dict[str, Any]
