"""Pydantic schemas for Step 15 SIEM & Security Log Analysis Engine."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Log Sources
# ---------------------------------------------------------------------------
class LogSourceBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str
    source_type: str = Field(..., max_length=64)
    platform: str = Field(..., max_length=64)
    vendor: str = Field(..., max_length=100)
    version: str | None = None
    status: str = "ACTIVE"
    is_synthetic: bool = True


class LogSourceResponse(LogSourceBase):
    id: int
    stable_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------
class SecurityLogDatasetResponse(BaseModel):
    id: int
    stable_id: str
    name: str
    description: str
    dataset_type: str
    difficulty: str
    event_count: int
    start_time: datetime | None = None
    end_time: datetime | None = None
    is_synthetic: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetImportRequest(BaseModel):
    dataset_id: int
    content: str
    format: str = "JSON"
    source_id: int | None = None


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
class SecurityEventResponse(BaseModel):
    id: int
    event_id: str
    timestamp: datetime
    event_type: str
    event_category: str
    source_type: str
    host: str | None = None
    username: str | None = None
    source_ip: str | None = None
    source_port: int | None = None
    destination_ip: str | None = None
    destination_port: int | None = None
    protocol: str | None = None
    action: str | None = None
    status: str | None = None
    severity: str
    process_name: str | None = None
    domain: str | None = None
    message: str | None = None
    dataset_id: int

    model_config = ConfigDict(from_attributes=True)


class SecurityEventDetailResponse(SecurityEventResponse):
    parent_process: str | None = None
    command_summary: str | None = None
    file_name: str | None = None
    file_hash: str | None = None
    url: str | None = None
    authentication_method: str | None = None
    result: str | None = None
    metadata_json: str | None = None
    raw_event_id: int | None = None
    source_id: int | None = None
    raw_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Search & Query
# ---------------------------------------------------------------------------
class QueryCondition(BaseModel):
    field: str
    operator: str = "="
    value: Any


class SiemSearchRequest(BaseModel):
    dataset_id: int | None = None
    conditions: list[QueryCondition] | None = None
    logical_op: str = "AND"
    not_conditions: list[QueryCondition] | None = None
    search_text: str | None = None
    time_preset: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    quick_filter: str | None = None
    limit: int = 50
    offset: int = 0
    sort_by: str = "timestamp"
    sort_asc: bool = False


class SiemSearchResponse(BaseModel):
    total: int
    limit: int
    offset: int
    execution_time_ms: float
    human_readable: str
    events: list[SecurityEventResponse]


# ---------------------------------------------------------------------------
# Aggregations & Dashboard
# ---------------------------------------------------------------------------
class SiemAggregateRequest(BaseModel):
    dataset_id: int | None = None
    time_preset: str | None = None


class TopEntityItem(BaseModel):
    name: str
    count: int


class TimeSeriesBucket(BaseModel):
    bucket: str
    timestamp: str
    total: int
    auth_failures: int
    firewall_blocks: int
    dns_queries: int


class SiemAggregateResponse(BaseModel):
    total_events: int
    auth_failures: int
    firewall_blocks: int
    dns_queries: int
    high_severity_count: int
    by_severity: dict[str, int]
    by_source_type: dict[str, int]
    by_category: dict[str, int]
    top_source_ips: list[TopEntityItem]
    top_dest_ports: list[TopEntityItem]
    top_hosts: list[TopEntityItem]
    top_users: list[TopEntityItem]
    top_domains: list[TopEntityItem]
    timeline: list[TimeSeriesBucket]


# ---------------------------------------------------------------------------
# Correlation Rules & Alerts
# ---------------------------------------------------------------------------
class LogCorrelationRuleResponse(BaseModel):
    id: int
    stable_id: str
    name: str
    description: str
    category: str
    severity: str
    confidence: str
    status: str
    version: str
    logic: str
    time_window_seconds: int
    explanation: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogCorrelationRuleCreate(BaseModel):
    stable_id: str
    name: str
    description: str
    category: str
    severity: str = "MEDIUM"
    confidence: str = "HIGH"
    logic: str
    time_window_seconds: int = 300
    explanation: str


class LogCorrelationRuleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    severity: str | None = None
    confidence: str | None = None
    status: str | None = None
    logic: str | None = None
    time_window_seconds: int | None = None
    explanation: str | None = None


class CorrelationAlertResponse(BaseModel):
    id: int
    alert_id: str
    rule_id: int
    dataset_id: int
    timestamp: datetime
    title: str
    category: str
    severity: str
    confidence: str
    status: str
    event_count: int
    source_context: str | None = None
    evidence_summary: str
    matched_event_ids: str | None = None
    soc_alert_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Saved Searches & History
# ---------------------------------------------------------------------------
class SavedSearchCreate(BaseModel):
    name: str
    description: str | None = None
    query_definition: dict[str, Any]
    is_public: bool = False


class SavedSearchUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    query_definition: dict[str, Any] | None = None
    is_public: bool | None = None


class SavedSearchResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    query_definition: str
    owner_id: int | None = None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchHistoryResponse(BaseModel):
    id: int
    user_id: int | None = None
    query_definition: str
    timestamp: datetime
    dataset_id: int | None = None
    result_count: int
    execution_time_ms: float

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Labs & Scenarios
# ---------------------------------------------------------------------------
class SIEMLabScenarioResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    difficulty: str
    dataset_id: int
    objectives: str
    expected_event_count: int
    hints: str | None = None
    recommended_query: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SIEMLabValidateRequest(BaseModel):
    executed_query: dict[str, Any]
    findings_notes: str | None = None
    identified_entity: str | None = None


class SIEMLabValidateResponse(BaseModel):
    success: bool
    score: int
    feedback: str
    criteria: dict[str, bool]


# ---------------------------------------------------------------------------
# Integrations
# ---------------------------------------------------------------------------
class StartHuntFromSiemRequest(BaseModel):
    event_id: str | None = None
    correlation_alert_id: int | None = None
    hypothesis_statement: str | None = None


class InvestigateInSocRequest(BaseModel):
    event_id: str | None = None
    correlation_alert_id: int | None = None
