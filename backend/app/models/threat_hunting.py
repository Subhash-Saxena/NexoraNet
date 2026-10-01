"""Database models for Step 14 Threat Hunting & Investigation Workspace.

Includes HuntDataset, HuntEvent, ThreatHunt, ThreatHuntHypothesis,
ThreatHuntEvidence, ThreatHuntFinding, and ThreatHuntNote.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import (
    HuntConfidence,
    HuntDatasetType,
    HuntDifficulty,
    HuntEventType,
    HuntEvidenceRelevance,
    HuntEvidenceType,
    HuntFindingType,
    HuntHypothesisStatus,
    HuntStatus,
)

if TYPE_CHECKING:
    from app.models.detection import DetectionAlert
    from app.models.pcap import Capture
    from app.models.soc import InvestigationAlert
    from app.models.threat_intel import Indicator
    from app.models.user import User


class HuntDataset(TimeStampedModel):
    """Educational security telemetry dataset available for threat hunting."""

    __tablename__ = "hunt_datasets"

    dataset_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_type: Mapped[str] = mapped_column(
        String(50), default=HuntDatasetType.PCAP.value, nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    event_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="READY", nullable=False, index=True)
    time_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    events: Mapped[list["HuntEvent"]] = relationship(
        "HuntEvent", back_populates="dataset", cascade="all, delete-orphan"
    )
    hunts: Mapped[list["ThreatHunt"]] = relationship("ThreatHunt", back_populates="dataset")


class HuntEvent(TimeStampedModel):
    """Normalized security telemetry event queryable in threat hunting campaigns."""

    __tablename__ = "hunt_events"

    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("hunt_datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50), default=HuntEventType.NETWORK_CONNECTION.value, nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    protocol: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    ioc_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("indicators.id", ondelete="SET NULL"), nullable=True, index=True
    )
    alert_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("detection_alerts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    soc_alert_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("investigation_alerts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pcap_capture_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pcap_packet_number: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    payload_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    dataset: Mapped["HuntDataset"] = relationship("HuntDataset", back_populates="events")
    indicator: Mapped["Indicator | None"] = relationship("Indicator", foreign_keys=[ioc_id])
    alert: Mapped["DetectionAlert | None"] = relationship("DetectionAlert", foreign_keys=[alert_id])
    soc_alert: Mapped["InvestigationAlert | None"] = relationship("InvestigationAlert", foreign_keys=[soc_alert_id])
    pcap_capture: Mapped["Capture | None"] = relationship("Capture", foreign_keys=[pcap_capture_id])


class ThreatHunt(TimeStampedModel):
    """Structured threat hunting session with analytical hypotheses and evidence."""

    __tablename__ = "threat_hunts"

    hunt_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default=HuntStatus.DRAFT.value, nullable=False, index=True
    )
    difficulty: Mapped[str] = mapped_column(
        String(20), default=HuntDifficulty.BEGINNER.value, nullable=False, index=True
    )
    dataset_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("hunt_datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_slug: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    initial_pivot_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    initial_pivot_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    query_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    conclusion_disposition: Mapped[str | None] = mapped_column(String(30), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_breakdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    dataset: Mapped["HuntDataset | None"] = relationship("HuntDataset", back_populates="hunts")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    hypotheses: Mapped[list["ThreatHuntHypothesis"]] = relationship(
        "ThreatHuntHypothesis", back_populates="hunt", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["ThreatHuntEvidence"]] = relationship(
        "ThreatHuntEvidence", back_populates="hunt", cascade="all, delete-orphan"
    )
    findings: Mapped[list["ThreatHuntFinding"]] = relationship(
        "ThreatHuntFinding", back_populates="hunt", cascade="all, delete-orphan"
    )
    notes: Mapped[list["ThreatHuntNote"]] = relationship(
        "ThreatHuntNote", back_populates="hunt", cascade="all, delete-orphan"
    )


class ThreatHuntHypothesis(TimeStampedModel):
    """An analytical hypothesis tested during a threat hunting investigation."""

    __tablename__ = "threat_hunt_hypotheses"

    hunt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("threat_hunts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default=HuntHypothesisStatus.OPEN.value, nullable=False, index=True
    )
    confidence: Mapped[str] = mapped_column(
        String(20), default=HuntConfidence.MEDIUM.value, nullable=False
    )
    analyst_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    hunt: Mapped["ThreatHunt"] = relationship("ThreatHunt", back_populates="hypotheses")
    evidence: Mapped[list["ThreatHuntEvidence"]] = relationship(
        "ThreatHuntEvidence", back_populates="hypothesis"
    )


class ThreatHuntEvidence(TimeStampedModel):
    """Collected artifact corroborating or contradicting a hunt hypothesis."""

    __tablename__ = "threat_hunt_evidence"

    hunt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("threat_hunts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hypothesis_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("threat_hunt_hypotheses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    evidence_type: Mapped[str] = mapped_column(
        String(30), default=HuntEvidenceType.EVENT.value, nullable=False, index=True
    )
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    relevance: Mapped[str] = mapped_column(
        String(20), default=HuntEvidenceRelevance.SUPPORTING.value, nullable=False, index=True
    )
    analyst_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    hunt: Mapped["ThreatHunt"] = relationship("ThreatHunt", back_populates="evidence")
    hypothesis: Mapped["ThreatHuntHypothesis | None"] = relationship(
        "ThreatHuntHypothesis", back_populates="evidence"
    )


class ThreatHuntFinding(TimeStampedModel):
    """Significant security pattern, detection gap, or anomalous behavior discovered."""

    __tablename__ = "threat_hunt_findings"

    hunt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("threat_hunts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    finding_type: Mapped[str] = mapped_column(
        String(30), default=HuntFindingType.OBSERVATION.value, nullable=False, index=True
    )
    confidence: Mapped[str] = mapped_column(
        String(20), default=HuntConfidence.MEDIUM.value, nullable=False
    )
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mitigation_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    hunt: Mapped["ThreatHunt"] = relationship("ThreatHunt", back_populates="findings")


class ThreatHuntNote(TimeStampedModel):
    """Analyst work journal and pivot observations during an active threat hunt."""

    __tablename__ = "threat_hunt_notes"

    hunt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("threat_hunts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    related_alert_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    related_ioc_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    related_hypothesis_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Relationships
    hunt: Mapped["ThreatHunt"] = relationship("ThreatHunt", back_populates="notes")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
