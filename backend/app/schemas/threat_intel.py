"""Pydantic schemas for Step 13 Threat Intelligence & IOC Investigation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Threat Intel Sources
# ---------------------------------------------------------------------------
class ThreatIntelSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    description: str | None = None
    reliability: str
    enabled: bool
    is_synthetic: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------
class IndicatorBriefResponse(BaseModel):
    id: int
    indicator_id: str
    indicator_type: str
    hash_type: str | None = None
    value: str
    normalized_value: str
    display_value: str
    source_name: str
    classification: str
    confidence: str
    severity: str
    status: str
    mitre_attack_id: str | None = None
    mitre_technique: str | None = None
    is_synthetic: bool
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndicatorObservationResponse(BaseModel):
    id: int
    indicator_id: int
    capture_id: int | None = None
    packet_number: int | None = None
    alert_id: int | None = None
    investigation_id: int | None = None
    case_id: int | None = None
    observation_type: str
    context_data: str | None = None
    observed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndicatorTimelineResponse(BaseModel):
    id: int
    indicator_id: int
    event_type: str
    title: str
    description: str | None = None
    actor_name: str
    event_timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndicatorNoteResponse(BaseModel):
    id: int
    indicator_id: int
    user_id: int | None = None
    author_name: str
    note: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IndicatorRelationshipResponse(BaseModel):
    id: int
    source_indicator_id: int
    target_indicator_id: int
    relationship_type: str
    description: str | None = None
    confidence: str
    created_at: datetime
    target_indicator: IndicatorBriefResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class IndicatorDetailResponse(IndicatorBriefResponse):
    false_positive_reason: str | None = None
    description: str | None = None
    tags: str | None = None
    is_watched: bool = False
    source: ThreatIntelSourceResponse | None = None
    observations: list[IndicatorObservationResponse] = Field(default_factory=list)
    outgoing_relationships: list[IndicatorRelationshipResponse] = Field(default_factory=list)
    incoming_relationships: list[IndicatorRelationshipResponse] = Field(default_factory=list)
    timeline_events: list[IndicatorTimelineResponse] = Field(default_factory=list)
    notes: list[IndicatorNoteResponse] = Field(default_factory=list)


class IndicatorCreateRequest(BaseModel):
    raw_value: str = Field(..., min_length=1, max_length=2048, description="Target IP, domain, URL, hash, or email")
    indicator_type: str | None = Field(default=None, description="Optional explicit indicator type")
    description: str | None = None
    tags: list[str] | None = None
    source_name: str = "Manual Analyst Submission"


class IndicatorClassificationUpdateRequest(BaseModel):
    classification: str = Field(..., description="BENIGN, SUSPICIOUS, MALICIOUS, or FALSE_POSITIVE")
    reason: str = Field(..., min_length=5, description="Documented analytical rationale")
    status: str | None = Field(default=None, description="ACTIVE, EXPIRED, REVOKED, or FALSE_POSITIVE")


class IndicatorNoteCreateRequest(BaseModel):
    note: str = Field(..., min_length=1, max_length=5000)


class RelationshipCreateRequest(BaseModel):
    target_indicator_id: int
    relationship_type: str = "RELATED_TO"
    description: str | None = None
    confidence: str = "MEDIUM"


# ---------------------------------------------------------------------------
# Watchlist
# ---------------------------------------------------------------------------
class WatchlistCreateRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=1000)
    expires_at: datetime | None = None


class WatchlistResponse(BaseModel):
    id: int
    indicator_id: int
    user_id: int
    reason: str
    added_by: str
    expires_at: datetime | None = None
    created_at: datetime
    indicator: IndicatorBriefResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Graph & Correlation
# ---------------------------------------------------------------------------
class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    severity: str = "INFO"
    details: dict[str, Any] = Field(default_factory=dict)


class GraphLink(BaseModel):
    source: str
    target: str
    label: str


class ThreatIntelGraphResponse(BaseModel):
    root_indicator_id: int
    nodes: list[GraphNode]
    links: list[GraphLink]


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------
class ThreatIntelChallengeBriefResponse(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: str
    category: str
    objective: str
    target_indicator_value: str
    expected_classification: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ThreatIntelChallengeDetailResponse(ThreatIntelChallengeBriefResponse):
    scenario_description: str
    expected_observations: str | None = None
    rubric_description: str | None = None


class ChallengeSubmitRequest(BaseModel):
    selected_classification: str = Field(..., description="BENIGN, SUSPICIOUS, MALICIOUS, or FALSE_POSITIVE")
    hypothesis_text: str = Field(..., min_length=10, description="Hypothesis evaluating source reliability and reputation")
    evidence_notes: str = Field(..., min_length=10, description="Observed network artifacts and telemetry review")
    conclusion: str = Field(..., min_length=10, description="Actionable SOC disposition and defensive recommendations")


class ChallengeAttemptResponse(BaseModel):
    id: int
    challenge_id: int
    user_id: int
    selected_classification: str
    hypothesis_text: str
    evidence_notes: str
    conclusion: str
    score: float
    passed: bool
    feedback: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Overview & Search
# ---------------------------------------------------------------------------
class ThreatIntelOverviewResponse(BaseModel):
    total_indicators: int
    by_classification: dict[str, int]
    by_type: dict[str, int]
    by_severity: dict[str, int]
    active_watchlists: int
    total_challenges: int
    recent_indicators: list[IndicatorBriefResponse]


class ImportResponse(BaseModel):
    total_records: int
    imported: int
    skipped: int
    errors: list[dict[str, Any]]
    sample_imported: list[dict[str, Any]]
