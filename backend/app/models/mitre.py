"""Database models for MITRE ATT&CK Framework integration (Step 17).

Provides versioned MITRE Enterprise tactics, techniques, and mapping relationships
to educational incidents and investigations.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampedModel

if TYPE_CHECKING:
    from app.models.incident import Incident
    from app.models.user import User


class AttackTactic(TimeStampedModel):
    """MITRE ATT&CK Enterprise Tactic (e.g., Initial Access, Execution, Persistence)."""

    __tablename__ = "attack_tactics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    tactic_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    external_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    techniques: Mapped[list["AttackTechnique"]] = relationship(
        "AttackTechnique", back_populates="tactic", cascade="all, delete-orphan", order_by="AttackTechnique.technique_id"
    )

    def __repr__(self) -> str:
        return f"<AttackTactic {self.tactic_id}: {self.name}>"


class AttackTechnique(TimeStampedModel):
    """MITRE ATT&CK Enterprise Technique or Sub-technique (e.g., T1059, T1059.001)."""

    __tablename__ = "attack_techniques"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    technique_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    tactic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attack_tactics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    detection_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    mitigation_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_subtechnique: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_technique_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    platforms: Mapped[str | None] = mapped_column(String(200), nullable=True)
    data_sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    tactic: Mapped["AttackTactic"] = relationship("AttackTactic", back_populates="techniques")
    incident_mappings: Mapped[list["IncidentTechniqueMapping"]] = relationship(
        "IncidentTechniqueMapping", back_populates="technique", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AttackTechnique {self.technique_id}: {self.name}>"


class IncidentTechniqueMapping(Base):
    """Associates an Incident with a verified or hypothesized MITRE ATT&CK technique."""

    __tablename__ = "incident_technique_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    technique_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("attack_techniques.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mapping_confidence: Mapped[str] = mapped_column(String(30), default="OBSERVED_EVIDENCE", nullable=False)
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    phase: Mapped[str | None] = mapped_column(String(30), nullable=True)
    mapped_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    mapped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    incident: Mapped["Incident"] = relationship("Incident", back_populates="technique_mappings")
    technique: Mapped["AttackTechnique"] = relationship("AttackTechnique", back_populates="incident_mappings")
    mapped_by: Mapped["User | None"] = relationship("User", foreign_keys=[mapped_by_id])

    def __repr__(self) -> str:
        return f"<IncidentTechniqueMapping inc={self.incident_id} tech={self.technique_id}>"
