"""Pydantic schemas for Step 14 Threat Hunting & Investigation Workspace."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Overview & Summary
# ---------------------------------------------------------------------------
class HuntOverviewResponse(BaseModel):
    total_hunts: int
    active_hunts: int
    completed_hunts: int
    total_datasets: int
    total_events: int
    total_scenarios: int
    recent_hunts: list[HuntResponse]


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------
class DatasetBase(BaseModel):
    dataset_id: str
    name: str
    description: str
    dataset_type: str = "PCAP"
    source: str = "SYSTEM"


class DatasetCreate(DatasetBase):
    metadata: dict[str, Any] | None = None


class DatasetResponse(DatasetBase):
    id: int
    event_count: int
    status: str
    time_start: datetime | None = None
    time_end: datetime | None = None
    metadata_json: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetAnalyticsResponse(BaseModel):
    dataset_id: int
    code: str
    name: str
    total_events: int
    time_range: dict[str, str | None]
    protocols: dict[str, int]
    event_types: dict[str, int]
    top_source_ips: list[dict[str, Any]]
    top_destination_ips: list[dict[str, Any]]
    top_domains: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Telemetry Events & Querying
# ---------------------------------------------------------------------------
class EventCondition(BaseModel):
    field: str
    operator: str = "=="
    value: Any


class HuntEventResponse(BaseModel):
    id: int
    event_id: str
    dataset_id: int
    event_type: str
    timestamp: datetime
    source_ip: str | None = None
    destination_ip: str | None = None
    source_port: int | None = None
    destination_port: int | None = None
    protocol: str | None = None
    domain: str | None = None
    url: str | None = None
    ioc_id: int | None = None
    alert_id: int | None = None
    soc_alert_id: int | None = None
    pcap_capture_id: int | None = None
    pcap_packet_number: int | None = None
    severity: str | None = None
    action: str | None = None
    status: str | None = None
    summary: str | None = None
    payload_preview: str | None = None
    metadata_json: str | None = None

    model_config = ConfigDict(from_attributes=True)


class HuntQueryRequest(BaseModel):
    dataset_id: int | None = None
    conditions: list[EventCondition] | None = None
    query_string: str | None = None
    search_text: str | None = None
    conjunction: str = "AND"
    limit: int = 50
    offset: int = 0
    sort_by: str = "timestamp"
    sort_desc: bool = True


class HuntQueryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    events: list[HuntEventResponse]
    took_ms: float
    conditions_used: list[dict[str, Any]]
    explanation: str


# ---------------------------------------------------------------------------
# Threat Hunts
# ---------------------------------------------------------------------------
class HuntBase(BaseModel):
    title: str
    description: str
    objective: str
    difficulty: str = "BEGINNER"
    dataset_id: int | None = None
    scenario_slug: str | None = None
    initial_pivot_type: str | None = None
    initial_pivot_value: str | None = None


class HuntCreate(HuntBase):
    pass


class HuntLaunchFromAlert(BaseModel):
    alert_id: int
    dataset_id: int | None = None
    title: str | None = None


class HuntLaunchFromIOC(BaseModel):
    ioc_id: int
    dataset_id: int | None = None
    title: str | None = None


class HuntResponse(HuntBase):
    id: int
    hunt_id: str
    status: str
    user_id: int
    query_history: str | None = None
    conclusion: str | None = None
    conclusion_disposition: str | None = None
    score: float | None = None
    score_breakdown: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Hypotheses
# ---------------------------------------------------------------------------
class HuntHypothesisCreate(BaseModel):
    title: str
    description: str
    confidence: str = "MEDIUM"


class HuntHypothesisUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    confidence: str | None = None
    analyst_reasoning: str | None = None


class HuntHypothesisResponse(BaseModel):
    id: int
    hunt_id: int
    title: str
    description: str
    status: str
    confidence: str
    analyst_reasoning: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------
class HuntEvidenceCreate(BaseModel):
    hypothesis_id: int | None = None
    evidence_type: str = "EVENT"
    source_id: str
    description: str
    relevance: str = "SUPPORTING"
    analyst_note: str | None = None
    data_snapshot: dict[str, Any] | None = None


class HuntEvidenceUpdate(BaseModel):
    hypothesis_id: int | None = None
    relevance: str | None = None
    analyst_note: str | None = None


class HuntEvidenceResponse(BaseModel):
    id: int
    hunt_id: int
    hypothesis_id: int | None = None
    evidence_type: str
    source_id: str
    description: str
    relevance: str
    analyst_note: str | None = None
    data_snapshot: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------
class HuntFindingCreate(BaseModel):
    title: str
    description: str
    finding_type: str = "OBSERVATION"
    confidence: str = "MEDIUM"
    evidence_count: int = 0
    mitigation_recommendation: str | None = None


class HuntFindingResponse(BaseModel):
    id: int
    hunt_id: int
    title: str
    description: str
    finding_type: str
    confidence: str
    evidence_count: int
    mitigation_recommendation: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
class HuntNoteCreate(BaseModel):
    content: str
    related_event_id: str | None = None
    related_alert_id: int | None = None
    related_ioc_id: int | None = None
    related_hypothesis_id: int | None = None


class HuntNoteResponse(BaseModel):
    id: int
    hunt_id: int
    user_id: int
    author_name: str
    content: str
    related_event_id: str | None = None
    related_alert_id: int | None = None
    related_ioc_id: int | None = None
    related_hypothesis_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Detailed Hunt Response with Nested Entities
# ---------------------------------------------------------------------------
class HuntDetailResponse(HuntResponse):
    dataset: DatasetResponse | None = None
    hypotheses: list[HuntHypothesisResponse] = []
    evidence: list[HuntEvidenceResponse] = []
    findings: list[HuntFindingResponse] = []
    notes: list[HuntNoteResponse] = []


# ---------------------------------------------------------------------------
# Timeline, Graph, Pivots, & Conclusions
# ---------------------------------------------------------------------------
class TimelineBucket(BaseModel):
    time_slot: str
    event_count: int
    alert_count: int
    ioc_count: int
    breakdown: dict[str, int]


class TimelineMilestone(BaseModel):
    event_id: str
    timestamp: str
    event_type: str
    summary: str | None = None
    severity: str
    source_ip: str | None = None
    destination_ip: str | None = None


class HuntTimelineResponse(BaseModel):
    total_events: int
    interval: str
    buckets: list[TimelineBucket]
    milestones: list[TimelineMilestone]


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    severity: str = "INFO"
    metadata: dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    label: str


class EntityGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    focus: str | None = None


class PivotRequest(BaseModel):
    entity_type: str
    entity_value: str


class PivotResponse(BaseModel):
    entity_type: str
    entity_value: str
    matched_events_count: int
    matched_events: list[dict[str, Any]]
    matched_iocs: list[dict[str, Any]]
    matched_alerts: list[dict[str, Any]]
    suggested_questions: list[str]


class HuntConclusionRequest(BaseModel):
    conclusion: str
    conclusion_disposition: str


class HuntScoreResponse(BaseModel):
    hunt_id: str
    total_score: float
    max_score: int
    grade: str
    breakdown: dict[str, Any]


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------
class HuntScenarioResponse(BaseModel):
    slug: str
    title: str
    difficulty: str
    category: str
    estimated_minutes: int
    mitre_tactics: list[str]
    mitre_techniques: list[str]
    brief: str
    objective: str
    background: str
    dataset_code: str
    initial_pivot_type: str | None = None
    initial_pivot_value: str | None = None
    guided_questions: list[str]
    suggested_hypotheses: list[dict[str, str]]
    expected_findings: list[dict[str, str]]


# Resolve circular reference for HuntOverviewResponse
HuntOverviewResponse.model_rebuild()
