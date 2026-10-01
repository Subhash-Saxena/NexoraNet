"""Database models for Step 17 Incident Response and Case Management.

Includes Incident, IncidentAlert, IncidentEvidence, EvidenceAuditLog,
IncidentTimelineEvent, IncidentHypothesis, IncidentFinding, ResponseAction, and IncidentNote.
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

from app.db.base import Base, TimeStampedModel

if TYPE_CHECKING:
    from app.models.detection import DetectionAlert
    from app.models.mitre import IncidentTechniqueMapping
    from app.models.playbook import IncidentPlaybook
    from app.models.soc import Case
    from app.models.user import User


class Incident(TimeStampedModel):
    """Core educational incident tracking an end-to-end incident response lifecycle."""

    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    incident_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    incident_type: Mapped[str] = mapped_column(String(50), default="NETWORK_INTRUSION", nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(10), default="P2", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="NEW", nullable=False, index=True)
    phase: Mapped[str] = mapped_column(String(40), default="DETECTION_ANALYSIS", nullable=False, index=True)
    classification: Mapped[str] = mapped_column(String(30), default="UNDETERMINED", nullable=False, index=True)
    case_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    playbook_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("incident_playbooks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    lead_analyst: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    contained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    eradicated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recovered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)
    simulation_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    case: Mapped["Case | None"] = relationship("Case", foreign_keys=[case_id])
    assigned_to: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to_id])
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])
    playbook: Mapped["IncidentPlaybook | None"] = relationship("IncidentPlaybook", back_populates="incidents")
    alerts: Mapped[list["IncidentAlert"]] = relationship(
        "IncidentAlert", back_populates="incident", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["IncidentEvidence"]] = relationship(
        "IncidentEvidence", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentEvidence.collected_at.desc()"
    )
    timeline_events: Mapped[list["IncidentTimelineEvent"]] = relationship(
        "IncidentTimelineEvent", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentTimelineEvent.timestamp.asc()"
    )
    hypotheses: Mapped[list["IncidentHypothesis"]] = relationship(
        "IncidentHypothesis", back_populates="incident", cascade="all, delete-orphan"
    )
    findings: Mapped[list["IncidentFinding"]] = relationship(
        "IncidentFinding", back_populates="incident", cascade="all, delete-orphan"
    )
    response_actions: Mapped[list["ResponseAction"]] = relationship(
        "ResponseAction", back_populates="incident", cascade="all, delete-orphan"
    )
    technique_mappings: Mapped[list["IncidentTechniqueMapping"]] = relationship(
        "IncidentTechniqueMapping", back_populates="incident", cascade="all, delete-orphan"
    )
    notes: Mapped[list["IncidentNote"]] = relationship(
        "IncidentNote", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentNote.created_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<Incident {self.incident_id}: {self.title} [{self.status}]>"


class IncidentAlert(Base):
    """Association connecting a detection alert to an incident."""

    __tablename__ = "incident_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(30), default="PRIMARY", nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="alerts")
    alert: Mapped["DetectionAlert"] = relationship("DetectionAlert")

    def __repr__(self) -> str:
        return f"<IncidentAlert inc={self.incident_id} alert={self.alert_id}>"


class IncidentEvidence(TimeStampedModel):
    """Unified cross-engine evidence item linked to an Incident."""

    __tablename__ = "incident_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    evidence_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_engine: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    relevance: Mapped[str] = mapped_column(String(30), default="SUPPORTING", nullable=False)
    is_contained: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    collected_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    data_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="evidence")
    collected_by: Mapped["User | None"] = relationship("User", foreign_keys=[collected_by_id])
    audit_logs: Mapped[list["EvidenceAuditLog"]] = relationship(
        "EvidenceAuditLog", back_populates="evidence", cascade="all, delete-orphan", order_by="EvidenceAuditLog.timestamp.desc()"
    )

    def __repr__(self) -> str:
        return f"<IncidentEvidence {self.evidence_id}: {self.title}>"


class EvidenceAuditLog(Base):
    """Educational chain of custody audit trail tracking each touch on an evidence item."""

    __tablename__ = "evidence_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    evidence_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incident_evidence.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    evidence: Mapped["IncidentEvidence"] = relationship("IncidentEvidence", back_populates="audit_logs")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<EvidenceAuditLog evd={self.evidence_id} action={self.action}>"


class IncidentTimelineEvent(TimeStampedModel):
    """Chronological event entry in an incident timeline."""

    __tablename__ = "incident_timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mitre_technique_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    is_milestone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="timeline_events")
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<IncidentTimelineEvent {self.timestamp}: {self.title}>"


class IncidentHypothesis(TimeStampedModel):
    """Hypothesis formulated during incident analysis and tested against collected evidence."""

    __tablename__ = "incident_hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    hypothesis_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PROPOSED", nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    concluded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="hypotheses")
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<IncidentHypothesis inc={self.incident_id} [{self.status}]>"


class IncidentFinding(TimeStampedModel):
    """Validated factual finding established from confirmed evidence."""

    __tablename__ = "incident_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    finding_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    confidence: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    affected_systems: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_accounts: Mapped[str | None] = mapped_column(Text, nullable=True)
    indicators_observed: Mapped[str | None] = mapped_column(Text, nullable=True)
    mitre_technique: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mitre_tactic: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="findings")
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<IncidentFinding inc={self.incident_id}: {self.title}>"


class ResponseAction(TimeStampedModel):
    """Safe, synthetic response action (containment, eradication, recovery).

    STRICT SAFETY RULE: simulation_only is always True. This never affects production systems.
    """

    __tablename__ = "incident_response_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    action_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PROPOSED", nullable=False)
    simulation_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    risk_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    simulated_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    executed_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reverted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="response_actions")
    executed_by: Mapped["User | None"] = relationship("User", foreign_keys=[executed_by_id])

    def __repr__(self) -> str:
        return f"<ResponseAction {self.action_id}: {self.action_type} [{self.status}]>"


class IncidentNote(Base):
    """Analyst work log entry attached to an incident."""

    __tablename__ = "incident_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="notes")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<IncidentNote inc={self.incident_id} id={self.id}>"
