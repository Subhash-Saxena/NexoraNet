"""Database models for Step 12 SOC Dashboard, Investigations, Cases, and Triage.

Includes Investigation, InvestigationAlert, InvestigationEvidence, InvestigationHypothesis,
InvestigationFinding, InvestigationNote, Case, CaseAlert, CaseInvestigation, CaseNote,
SocAuditLog, SocNotification, SocChallenge, and SocChallengeAttempt.
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
    from app.models.detection import DetectionAlert
    from app.models.incident import Incident
    from app.models.pcap import Capture
    from app.models.user import User


class Investigation(TimeStampedModel):
    """A structured SOC investigation grouping alerts, hypotheses, evidence, and conclusions."""

    __tablename__ = "investigations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    investigation_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(10), default="P3", nullable=False, index=True)
    classification: Mapped[str] = mapped_column(String(30), default="UNREVIEWED", nullable=False, index=True)
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])
    assigned_to: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to_id])
    alerts: Mapped[list["InvestigationAlert"]] = relationship(
        "InvestigationAlert", back_populates="investigation", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["InvestigationEvidence"]] = relationship(
        "InvestigationEvidence", back_populates="investigation", cascade="all, delete-orphan"
    )
    hypotheses: Mapped[list["InvestigationHypothesis"]] = relationship(
        "InvestigationHypothesis", back_populates="investigation", cascade="all, delete-orphan"
    )
    findings: Mapped[list["InvestigationFinding"]] = relationship(
        "InvestigationFinding", back_populates="investigation", cascade="all, delete-orphan"
    )
    notes: Mapped[list["InvestigationNote"]] = relationship(
        "InvestigationNote", back_populates="investigation", cascade="all, delete-orphan", order_by="InvestigationNote.created_at.desc()"
    )
    case_investigations: Mapped[list["CaseInvestigation"]] = relationship(
        "CaseInvestigation", back_populates="investigation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Investigation {self.investigation_id}: {self.title} [{self.status}]>"


class InvestigationAlert(Base):
    """Association between an investigation and a detection alert."""

    __tablename__ = "investigation_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relationship_type: Mapped[str] = mapped_column(String(30), default="PRIMARY", nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="alerts")
    alert: Mapped["DetectionAlert"] = relationship("DetectionAlert")

    def __repr__(self) -> str:
        return f"<InvestigationAlert inv={self.investigation_id} alert={self.alert_id} role={self.relationship_type}>"


class InvestigationEvidence(Base):
    """Granular evidence item referenced in an investigation without duplicating raw PCAP bytes."""

    __tablename__ = "investigation_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capture_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="SET NULL"), nullable=True, index=True
    )
    packet_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON payload
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="evidence")
    capture: Mapped["Capture | None"] = relationship("Capture")

    def __repr__(self) -> str:
        return f"<InvestigationEvidence id={self.id} inv={self.investigation_id} type={self.evidence_type}>"


class InvestigationHypothesis(TimeStampedModel):
    """An analytical hypothesis formulated by a student during triage."""

    __tablename__ = "investigation_hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hypothesis_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="UNTESTED", nullable=False, index=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    supporting_evidence_ids: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # JSON list
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="hypotheses")
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<InvestigationHypothesis id={self.id} inv={self.investigation_id} status={self.status}>"


class InvestigationFinding(TimeStampedModel):
    """A substantiated finding established from validated evidence in an investigation."""

    __tablename__ = "investigation_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="findings")
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self) -> str:
        return f"<InvestigationFinding id={self.id} inv={self.investigation_id} title={self.title}>"


class InvestigationNote(TimeStampedModel):
    """Analyst log entries and journal notes attached to an investigation."""

    __tablename__ = "investigation_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="notes")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<InvestigationNote id={self.id} inv={self.investigation_id}>"


class Case(TimeStampedModel):
    """Higher-level case container grouping multiple investigations, alerts, and executive findings."""

    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    case_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(10), default="P3", nullable=False, index=True)
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    created_by: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])
    assigned_to: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to_id])
    alerts: Mapped[list["CaseAlert"]] = relationship(
        "CaseAlert", back_populates="case", cascade="all, delete-orphan"
    )
    investigations: Mapped[list["CaseInvestigation"]] = relationship(
        "CaseInvestigation", back_populates="case", cascade="all, delete-orphan"
    )
    notes: Mapped[list["CaseNote"]] = relationship(
        "CaseNote", back_populates="case", cascade="all, delete-orphan", order_by="CaseNote.created_at.desc()"
    )
    incidents: Mapped[list["Incident"]] = relationship(
        "Incident", back_populates="case"
    )

    def __repr__(self) -> str:
        return f"<Case {self.case_id}: {self.title} [{self.status}]>"


class CaseAlert(Base):
    """Direct association between a case and a detection alert."""

    __tablename__ = "case_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("detection_alerts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="alerts")
    alert: Mapped["DetectionAlert"] = relationship("DetectionAlert")

    def __repr__(self) -> str:
        return f"<CaseAlert case={self.case_id} alert={self.alert_id}>"


class CaseInvestigation(Base):
    """Association between a case and an investigation."""

    __tablename__ = "case_investigations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    investigation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="investigations")
    investigation: Mapped["Investigation"] = relationship("Investigation", back_populates="case_investigations")

    def __repr__(self) -> str:
        return f"<CaseInvestigation case={self.case_id} inv={self.investigation_id}>"


class CaseNote(TimeStampedModel):
    """Analyst log entries and executive notes attached to a case."""

    __tablename__ = "case_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="notes")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<CaseNote id={self.id} case={self.case_id}>"


class SocAuditLog(Base):
    """Append-only audit trail recording analyst actions across the SOC platform."""

    __tablename__ = "soc_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    actor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    object_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    object_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON payload
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<SocAuditLog id={self.id} actor={self.actor_name} action={self.action} on={self.object_type}:{self.object_id}>"


class SocNotification(Base):
    """In-app alert and update notifications for the SOC analyst."""

    __tablename__ = "soc_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<SocNotification id={self.id} type={self.notification_type} read={self.is_read}>"


class SocChallenge(TimeStampedModel):
    """Educational hands-on SOC investigation scenario."""

    __tablename__ = "soc_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    capture_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="SET NULL"), nullable=True, index=True
    )
    difficulty: Mapped[str] = mapped_column(String(30), default="INTERMEDIATE", nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    expected_observations: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # JSON list
    rubric_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)  # JSON scoring rubric

    # Relationships
    capture: Mapped["Capture | None"] = relationship("Capture")
    attempts: Mapped[list["SocChallengeAttempt"]] = relationship(
        "SocChallengeAttempt", back_populates="challenge", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SocChallenge {self.slug}: {self.title}>"


class SocChallengeAttempt(TimeStampedModel):
    """Student submission and evaluation for a SOC challenge scenario."""

    __tablename__ = "soc_challenge_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("soc_challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    investigation_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("investigations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(30), default="IN_PROGRESS", nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    score_breakdown: Mapped[str] = mapped_column(Text, default="{}", nullable=False)  # JSON
    feedback: Mapped[str] = mapped_column(Text, default="[]", nullable=False)  # JSON
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    challenge: Mapped["SocChallenge"] = relationship("SocChallenge", back_populates="attempts")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    investigation: Mapped["Investigation | None"] = relationship("Investigation")

    def __repr__(self) -> str:
        return f"<SocChallengeAttempt id={self.id} chal={self.challenge_id} score={self.score}>"
