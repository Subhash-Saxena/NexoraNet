"""Pydantic request and response schemas for PCAP packet inspection and analysis."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    CaptureStatus,
    ObservationSeverity,
    ObservationType,
    TcpHandshakeState,
)


class CaptureSummaryResponse(BaseModel):
    """Macro summary of an uploaded or sample packet capture file."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    filename: str
    file_size: int
    format: str
    packet_count: int
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration: float
    status: CaptureStatus | str
    error_message: str | None = None
    is_sample: bool
    sample_category: str | None = None
    description: str | None = None
    created_at: datetime


class CaptureDetailResponse(CaptureSummaryResponse):
    """Deep details including summary telemetry and safety notices."""

    summary_metadata: dict[str, Any] | None = None
    safety_disclaimer: str = (
        "NexoraNet analyzes packet captures offline. It does not transmit, replay, or execute captured network traffic."
    )
    privacy_disclaimer: str = (
        "Packet captures may contain sensitive network information. Only analyze captures you are authorized to use."
    )

    @field_validator("summary_metadata", mode="before")
    @classmethod
    def parse_summary_metadata(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return v


class ParsedPacketSummary(BaseModel):
    """Condensed packet summary for performant virtualized table rendering."""

    model_config = ConfigDict(from_attributes=True)

    packet_number: int
    timestamp: float
    relative_time: float
    captured_length: int
    protocol: str
    source_mac: str | None = None
    destination_mac: str | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    source_port: int | None = None
    destination_port: int | None = None
    info: str


class ParsedPacketDetail(ParsedPacketSummary):
    """Deep inspection of frame layers and decoded protocol header trees."""

    original_length: int
    transport_protocol: str | None = None
    application_protocol: str | None = None
    tcp_flags: list[str] = Field(default_factory=list)
    tcp_seq: int | None = None
    tcp_ack: int | None = None
    layers: list[str] = Field(default_factory=list)
    layer_details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tcp_flags", "layers", mode="before")
    @classmethod
    def parse_json_list(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return []
        return v or []

    @field_validator("layer_details", mode="before")
    @classmethod
    def parse_layer_details(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return {}
        return v or {}


class PacketListResponse(BaseModel):
    """Paginated packet list matching filter criteria."""

    capture_id: int
    total_matched: int
    page: int
    page_size: int
    total_pages: int
    filter_applied: str | None = None
    packets: list[ParsedPacketSummary]


class FlowLadderItem(BaseModel):
    """Sequence diagram step in a conversation ladder."""

    step: int
    relative_time: float
    source: str = ""
    destination: str = ""
    protocol: str = ""
    info: str = ""
    tcp_flags: list[str] = Field(default_factory=list)


class ConversationItem(BaseModel):
    """5-tuple network conversation flow with state and metrics."""

    id: str
    client_endpoint: str
    server_endpoint: str
    protocol: str
    packet_count: int
    byte_count: int = 0
    total_bytes: int = 0
    start_time: float
    duration: float
    handshake_state: TcpHandshakeState | str = TcpHandshakeState.UNKNOWN
    ladder: list[FlowLadderItem] = Field(default_factory=list)


class EndpointItem(BaseModel):
    """Unique IP or MAC address communicating in the capture."""

    ip: str
    mac: str | None = None
    packets_sent: int = 0
    packets_received: int = 0
    total_packets: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    total_bytes: int = 0
    protocols: list[str] = Field(default_factory=list)
    first_seen: float = 0.0
    last_seen: float = 0.0


class PortItem(BaseModel):
    """L4 Transport port distribution."""

    port: int
    protocol: str
    service_hint: str
    packet_count: int
    byte_count: int
    client_count: int = 0
    server_count: int = 0


class TimelineBucket(BaseModel):
    """Time-series histogram bucket for traffic density."""

    bucket_index: int
    start_offset_seconds: float = 0.0
    end_offset_seconds: float = 0.0
    packet_count: int = 0
    byte_count: int = 0
    protocols: dict[str, int] = Field(default_factory=dict)


TimelineBucketItem = TimelineBucket


class CaptureStatisticsResponse(BaseModel):
    """Aggregated capture analytics and overview telemetry."""

    capture_id: int
    total_packets: int
    total_bytes: int
    duration_seconds: float
    packets_per_second: float = 0.0
    bytes_per_second: float = 0.0
    avg_packet_rate_pps: float | None = None
    avg_bit_rate_bps: float | None = None
    unique_ips: int
    unique_macs: int
    unique_ports: int
    protocol_distribution: dict[str, int] = Field(default_factory=dict)
    top_protocols: list[dict[str, Any]] = Field(default_factory=list)
    top_talkers: list[dict[str, Any]] = Field(default_factory=list)


class ObservationResponse(BaseModel):
    """Rule-based pedagogical pattern observation detected in traffic."""

    id: str
    type: ObservationType | str
    severity: ObservationSeverity | str
    title: str
    description: str
    why_it_matters: str
    cyber_relevance: str
    evidence_packets: list[int]


class BookmarkCreateRequest(BaseModel):
    """Request payload to bookmark an interesting packet."""

    packet_number: int
    note: str | None = None
    tags: list[str] = Field(default_factory=list)


class BookmarkResponse(BaseModel):
    """Stored packet bookmark."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    capture_id: int
    packet_number: int
    note: str | None = None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return []
        return v or []


class NoteCreateRequest(BaseModel):
    """Request payload to attach a note to a packet or finding."""

    target_type: str = "general"
    target_id: str | None = None
    title: str | None = None
    content: str


class NoteResponse(BaseModel):
    """Stored analyst note."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    capture_id: int
    target_type: str
    target_id: str | None = None
    title: str | None = None
    content: str
    created_at: datetime


class FindingCreateRequest(BaseModel):
    """Request payload to record an investigation finding."""

    title: str
    description: str
    severity: ObservationSeverity | str = ObservationSeverity.INFO
    evidence_packets: list[int] = Field(default_factory=list)
    source_endpoint: str | None = None
    destination_endpoint: str | None = None
    hypothesis: str | None = None
    conclusion: str | None = None


class FindingResponse(BaseModel):
    """Stored student investigation finding."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    capture_id: int
    title: str
    description: str
    severity: str
    evidence_packets: list[int] = Field(default_factory=list)
    source_endpoint: str | None = None
    destination_endpoint: str | None = None
    hypothesis: str | None = None
    conclusion: str | None = None
    created_at: datetime

    @field_validator("evidence_packets", mode="before")
    @classmethod
    def parse_evidence_packets(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError, ValueError):
                return []
        return v or []


class InvestigationReportResponse(BaseModel):
    """Consolidated SOC investigation summary report."""

    capture: CaptureSummaryResponse
    statistics: CaptureStatisticsResponse
    top_endpoints: list[EndpointItem]
    conversations: list[ConversationItem]
    observations: list[ObservationResponse]
    bookmarks: list[BookmarkResponse]
    notes: list[NoteResponse]
    findings: list[FindingResponse]
    disclaimer: str = (
        "Educational Report: Generated offline by NexoraNet. Observations indicate noteworthy traffic patterns, not confirmed attacks."
    )
