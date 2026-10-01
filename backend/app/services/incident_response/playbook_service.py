"""Incident Response Playbook Service for Step 17.

Handles retrieval, step progress, and attachment of standardized playbooks to incidents.
"""


from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.playbook import IncidentPlaybook


class PlaybookService:
    """Manages IR Playbooks and incident playbook guidance."""

    @classmethod
    def list_playbooks(
        cls,
        db: Session,
        category: str | None = None,
        search: str | None = None,
    ) -> list[IncidentPlaybook]:
        query = select(IncidentPlaybook).where(IncidentPlaybook.is_active == True)
        if category:
            query = query.where(IncidentPlaybook.category == category)
        if search:
            search_fmt = f"%{search}%"
            query = query.where(
                or_(
                    IncidentPlaybook.playbook_id.ilike(search_fmt),
                    IncidentPlaybook.title.ilike(search_fmt),
                    IncidentPlaybook.description.ilike(search_fmt),
                )
            )

        return list(db.execute(query.order_by(IncidentPlaybook.category.asc(), IncidentPlaybook.title.asc())).scalars().all())

    @classmethod
    def get_playbook(cls, db: Session, playbook_id_or_int: str | int) -> IncidentPlaybook | None:
        if isinstance(playbook_id_or_int, int) or str(playbook_id_or_int).isdigit():
            query = select(IncidentPlaybook).where(IncidentPlaybook.id == int(playbook_id_or_int))
        else:
            query = select(IncidentPlaybook).where(IncidentPlaybook.playbook_id == str(playbook_id_or_int))
        return db.execute(query).scalar_one_or_none()

    @classmethod
    def attach_playbook(cls, db: Session, incident_id: int, playbook_id_or_code: str | int) -> Incident:
        incident = db.get(Incident, incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        playbook = cls.get_playbook(db, playbook_id_or_code)
        if not playbook:
            raise ValueError(f"Playbook {playbook_id_or_code} not found")

        incident.playbook_id = playbook.id
        db.commit()
        db.refresh(incident)
        return incident
