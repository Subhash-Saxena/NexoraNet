"""Database models for Step 17 Incident Response Playbooks.

Structured playbooks guide analysts through NIST SP 800-61 / educational IR workflows.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel

if TYPE_CHECKING:
    from app.models.incident import Incident


class IncidentPlaybook(TimeStampedModel):
    """Standardized educational Incident Response Playbook."""

    __tablename__ = "incident_playbooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    playbook_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity_guidance: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    primary_tactic_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phases_definition: Mapped[str] = mapped_column(Text, nullable=False)
    checklist_json: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_actions_json: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    incidents: Mapped[list["Incident"]] = relationship("Incident", back_populates="playbook")

    def __repr__(self) -> str:
        return f"<IncidentPlaybook {self.playbook_id}: {self.title}>"
