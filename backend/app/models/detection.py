"""Database models for the Step 11 Network Detection Engine.

Includes DetectionRule, DetectionRun, DetectionAlert, AlertEvidence,
AlertNote, and AlertStatusHistory.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampedModel

if TYPE_CHECKING:
    from app.models.pcap import Capture, ParsedPacket
    from app.models.simulator import SimulatorScenario
    from app.models.user import User


class DetectionRule(TimeStampedModel):
    """Detection rule definition evaluated by the deterministic detection engine."""

    __tablename__ = "detection_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    rule_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    confidence_default: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ENABLED", nullable=False, index=True)
    logic_type: Mapped[str] = mapped_column(String(50), default="THRESHOLD", nullable=False)
    conditions: Mapped[str] = mapped_column(Text, default="{}", nullable=False)  # JSON declarative condition spec
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_window_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mitre_attack_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mitre_technique: Mapped[str | None] = mapped_column(String(100), nullable=True)
    explanation_template: Mapped[str] = mapped_column(Text, nullable=False)
    investigation_guide: Mapped[str] = mapped_column(Text, nullable=False)  # JSON or text instructions
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    author_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    author: Mapped["User | None"] = relationship("User", foreign_keys=[author_id])
    alerts: Mapped[list["DetectionAlert"]] = relationship(
        "DetectionAlert", back_populates="rule", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DetectionRule {self.rule_id}: {self.name} [{self.status}]>"


class DetectionRun(TimeStampedModel):
    """Record of an offline detection analysis execution over a PCAP or simulation session."""

    __tablename__ = "detection_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_type: Mapped[str] = mapped_column(String(30), default="PCAP", nullable=False, index=True)
    capture_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="CASCADE"), nullable=True, index=True
    )
    simulation_scenario_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("simulator_scenarios.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(30), default="QUEUED", nullable=False, index=True)
    rules_evaluated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rules_matched: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    alerts_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON summary dict

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    capture: Mapped["Capture | None"] = relationship("Capture", foreign_keys=[capture_id])
    simulation_scenario: Mapped["SimulatorScenario | None"] = relationship(
        "SimulatorScenario", foreign_keys=[simulation_scenario_id]
    )
    alerts: Mapped[list["DetectionAlert"]] = relationship(
        "DetectionAlert", back_populates="run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DetectionRun id={self.id} source={self.source_type} status={self.status} alerts={self.alerts_generated}>"


class DetectionAlert(TimeStampedModel):
    """Detection alert generated by a rule match with deduplication and rich context."""

    __tablename__ = "detection_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    run_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    capture_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="CASCADE"), nullable=True, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    confidence: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="NEW", nullable=False, index=True)
    classification: Mapped[str] = mapped_column(String(30), default="UNREVIEWED", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(10), default="P3", nullable=False, index=True)
    assigned_to_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    destination_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(30), nullable=True)
    first_seen_timestamp: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_seen_timestamp: Mapped[float | None] = mapped_column(Float, nullable=True)
    packet_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    dedup_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    mitre_attack_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mitre_technique: Mapped[str | None] = mapped_column(String(100), nullable=True)
    investigation_steps: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # JSON list

    # Relationships
    run: Mapped["DetectionRun"] = relationship("DetectionRun", back_populates="alerts")
    rule: Mapped["DetectionRule"] = relationship("DetectionRule", back_populates="alerts")
    capture: Mapped["Capture | None"] = relationship("Capture", foreign_keys=[capture_id])
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    assigned_to: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to_id])
    evidence: Mapped[list["AlertEvidence"]] = relationship(
        "AlertEvidence", back_populates="alert", cascade="all, delete-orphan"
    )
    notes: Mapped[list["AlertNote"]] = relationship(
        "AlertNote", back_populates="alert", cascade="all, delete-orphan", order_by="AlertNote.created_at.desc()"
    )
    status_history: Mapped[list["AlertStatusHistory"]] = relationship(
        "AlertStatusHistory", back_populates="alert", cascade="all, delete-orphan", order_by="AlertStatusHistory.created_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<DetectionAlert id={self.id} rule_id={self.rule_id} severity={self.severity} status={self.status}>"


class AlertEvidence(Base):
    """Concrete evidence reference (packet, flow, event, metric) attached to an alert."""

    __tablename__ = "alert_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    packet_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("parsed_packets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    packet_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    alert: Mapped["DetectionAlert"] = relationship("DetectionAlert", back_populates="evidence")
    packet: Mapped["ParsedPacket | None"] = relationship("ParsedPacket", foreign_keys=[packet_id])

    def __repr__(self) -> str:
        return f"<AlertEvidence id={self.id} alert_id={self.alert_id} type={self.evidence_type}>"


class AlertNote(TimeStampedModel):
    """Analyst investigation notes and observations for an alert."""

    __tablename__ = "alert_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    alert: Mapped["DetectionAlert"] = relationship("DetectionAlert", back_populates="notes")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AlertNote id={self.id} alert_id={self.alert_id}>"


class AlertStatusHistory(Base):
    """Audit log of alert workflow status transitions (NEW -> INVESTIGATING -> CLOSED, etc.)."""

    __tablename__ = "alert_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    previous_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    alert: Mapped["DetectionAlert"] = relationship("DetectionAlert", back_populates="status_history")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AlertStatusHistory id={self.id} alert_id={self.alert_id} {self.previous_status}->{self.new_status}>"
