"""Database models for Step 16 Endpoint Security & Host Investigation Engine.

Includes EndpointHost, EndpointEvent, EndpointInvestigation, EndpointHypothesis,
EndpointEvidence, EndpointFinding, EndpointConclusion, and EndpointScenario.
All models support strictly synthetic offline educational host telemetry.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import (
    EndpointArchitecture,
    EndpointEnvironment,
    EndpointEventCategory,
    EndpointEventType,
    EndpointInvestigationPriority,
    EndpointInvestigationStatus,
    EndpointPlatform,
    EndpointRiskLevel,
    EndpointStatus,
    EndpointVerdict,
    EvidenceRelevance,
    HypothesisStatus,
    ThreatConfidence,
)

if TYPE_CHECKING:
    from app.models.user import User


class EndpointHost(TimeStampedModel):
    """Synthetic host/workstation representation for offline endpoint investigation training."""

    __tablename__ = "endpoint_hosts"

    stable_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(
        String(64), default=EndpointPlatform.WINDOWS.value, nullable=False, index=True
    )
    platform_version: Mapped[str] = mapped_column(String(128), nullable=False)
    architecture: Mapped[str] = mapped_column(
        String(32), default=EndpointArchitecture.X64.value, nullable=False
    )
    environment: Mapped[str] = mapped_column(
        String(64), default=EndpointEnvironment.WORKSTATION.value, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), default=EndpointStatus.ONLINE.value, nullable=False, index=True
    )
    risk_level: Mapped[str] = mapped_column(
        String(32), default=EndpointRiskLevel.LOW.value, nullable=False, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(32), nullable=True)
    os_build: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    events: Mapped[list["EndpointEvent"]] = relationship(
        "EndpointEvent", back_populates="host", cascade="all, delete-orphan"
    )
    investigations: Mapped[list["EndpointInvestigation"]] = relationship(
        "EndpointInvestigation", back_populates="host", cascade="all, delete-orphan"
    )


class EndpointEvent(TimeStampedModel):
    """Normalized synthetic endpoint activity event (Process, Auth, Network, File, Registry/Task)."""

    __tablename__ = "endpoint_events"

    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    host_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("endpoint_hosts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(64), default=EndpointEventType.PROCESS_START.value, nullable=False, index=True
    )
    event_category: Mapped[str] = mapped_column(
        String(64), default=EndpointEventCategory.PROCESS.value, nullable=False, index=True
    )

    # Subject / Identity
    username: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    # Process Telemetry
    process_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    process_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    parent_process_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    parent_process_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    command_summary: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    integrity_level: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # File System Telemetry
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    file_action: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Network & DNS Telemetry
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    protocol: Mapped[str | None] = mapped_column(String(32), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    dns_query_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    dns_response: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Service & Persistence Telemetry
    service_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    service_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service_action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    persistence_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Authentication & Privilege Details
    auth_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    auth_failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(32), default="INFO", nullable=False, index=True)
    raw_event_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    host: Mapped["EndpointHost"] = relationship("EndpointHost", back_populates="events")
    evidence: Mapped[list["EndpointEvidence"]] = relationship(
        "EndpointEvidence", back_populates="event"
    )


class EndpointInvestigation(TimeStampedModel):
    """Structured analytical host investigation case conducted by a student."""

    __tablename__ = "endpoint_investigations"

    stable_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    host_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("endpoint_hosts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=EndpointInvestigationStatus.OPEN.value, nullable=False, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(16), default=EndpointInvestigationPriority.P2.value, nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_slug: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    host: Mapped["EndpointHost"] = relationship("EndpointHost", back_populates="investigations")
    user: Mapped["User"] = relationship("User")
    hypotheses: Mapped[list["EndpointHypothesis"]] = relationship(
        "EndpointHypothesis", back_populates="investigation", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["EndpointEvidence"]] = relationship(
        "EndpointEvidence", back_populates="investigation", cascade="all, delete-orphan"
    )
    findings: Mapped[list["EndpointFinding"]] = relationship(
        "EndpointFinding", back_populates="investigation", cascade="all, delete-orphan"
    )
    conclusion: Mapped["EndpointConclusion | None"] = relationship(
        "EndpointConclusion", back_populates="investigation", uselist=False, cascade="all, delete-orphan"
    )


class EndpointHypothesis(TimeStampedModel):
    """Analyst working hypothesis regarding activity observed on the endpoint."""

    __tablename__ = "endpoint_hypotheses"

    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("endpoint_investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=HypothesisStatus.OPEN.value, nullable=False, index=True
    )
    confidence: Mapped[str] = mapped_column(
        String(32), default=ThreatConfidence.MEDIUM.value, nullable=False
    )
    analyst_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    investigation: Mapped["EndpointInvestigation"] = relationship(
        "EndpointInvestigation", back_populates="hypotheses"
    )
    evidence: Mapped[list["EndpointEvidence"]] = relationship(
        "EndpointEvidence", back_populates="hypothesis"
    )


class EndpointEvidence(TimeStampedModel):
    """Artifact, event, or observation linked to an investigation and optional hypothesis."""

    __tablename__ = "endpoint_evidence"

    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("endpoint_investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hypothesis_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("endpoint_hypotheses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    event_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("endpoint_events.id", ondelete="SET NULL"), nullable=True, index=True
    )
    evidence_type: Mapped[str] = mapped_column(
        String(64), default="EVENT", nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    relevance: Mapped[str] = mapped_column(
        String(32), default=EvidenceRelevance.SUPPORTING.value, nullable=False, index=True
    )
    artifact_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    investigation: Mapped["EndpointInvestigation"] = relationship(
        "EndpointInvestigation", back_populates="evidence"
    )
    hypothesis: Mapped["EndpointHypothesis | None"] = relationship(
        "EndpointHypothesis", back_populates="evidence"
    )
    event: Mapped["EndpointEvent | None"] = relationship(
        "EndpointEvent", back_populates="evidence"
    )


class EndpointFinding(TimeStampedModel):
    """Structured analytical finding or milestone documented during host investigation."""

    __tablename__ = "endpoint_findings"

    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("endpoint_investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    mitre_attack_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    severity: Mapped[str] = mapped_column(String(32), default="MEDIUM", nullable=False)

    # Relationships
    investigation: Mapped["EndpointInvestigation"] = relationship(
        "EndpointInvestigation", back_populates="findings"
    )


class EndpointConclusion(TimeStampedModel):
    """Final analytical summary and score for a completed educational endpoint investigation."""

    __tablename__ = "endpoint_conclusions"

    investigation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("endpoint_investigations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[str] = mapped_column(
        String(64), default=EndpointVerdict.BENIGN_ANOMALY.value, nullable=False, index=True
    )
    training_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score_breakdown_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    investigation: Mapped["EndpointInvestigation"] = relationship(
        "EndpointInvestigation", back_populates="conclusion"
    )


class EndpointScenario(TimeStampedModel):
    """Guided endpoint investigation practice scenario."""

    __tablename__ = "endpoint_scenarios"

    scenario_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(32), default="BEGINNER", nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    target_host_stable_id: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    background: Mapped[str] = mapped_column(Text, nullable=False)
    objectives_json: Mapped[str] = mapped_column(Text, nullable=False)
    hints_json: Mapped[str] = mapped_column(Text, nullable=False)
    solution_rubric_json: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
