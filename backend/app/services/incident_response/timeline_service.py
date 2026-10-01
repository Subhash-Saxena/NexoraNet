"""Multi-Source Timeline Aggregation Service for Step 17.

Constructs unified chronological timelines across alerts, host events, SIEM,
and analyst triage milestones.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentTimelineEvent


class TimelineService:
    """Manages incident chronological event timelines and milestone tagging."""

    @classmethod
    def list_events(
        cls,
        db: Session,
        incident_id: int,
        category: str | None = None,
        is_milestone: bool | None = None,
    ) -> list[IncidentTimelineEvent]:
        query = select(IncidentTimelineEvent).where(IncidentTimelineEvent.incident_id == incident_id)
        if category:
            query = query.where(IncidentTimelineEvent.event_category == category)
        if is_milestone is not None:
            query = query.where(IncidentTimelineEvent.is_milestone == is_milestone)

        return list(db.execute(query.order_by(IncidentTimelineEvent.timestamp.asc())).scalars().all())

    @classmethod
    def add_event(
        cls,
        db: Session,
        incident_id: int,
        timestamp: datetime,
        title: str,
        description: str,
        event_category: str = "OBSERVATION",
        source: str = "ANALYST",
        source_id: str | None = None,
        mitre_technique_id: str | None = None,
        is_milestone: bool = False,
        user_id: int | None = None,
    ) -> IncidentTimelineEvent:
        incident = db.get(Incident, incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        event = IncidentTimelineEvent(
            incident_id=incident.id,
            timestamp=timestamp,
            title=title,
            description=description,
            event_category=event_category,
            source=source,
            source_id=source_id,
            mitre_technique_id=mitre_technique_id,
            is_milestone=is_milestone,
            created_by_id=user_id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @classmethod
    def sync_timeline_from_sources(cls, db: Session, incident_id: int) -> int:
        """Pulls linked alerts, evidence, and response actions into the chronological timeline."""
        incident = db.get(Incident, incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        existing_sources = {
            (ev.source, ev.source_id) for ev in incident.timeline_events if ev.source_id
        }
        added_count = 0

        # Sync from Response Actions
        for action in incident.response_actions:
            if action.executed_at and ("ACTION", action.action_id) not in existing_sources:
                db.add(IncidentTimelineEvent(
                    incident_id=incident.id,
                    timestamp=action.executed_at,
                    title=f"Simulated Action Executed: {action.action_type}",
                    description=f"{action.category} action performed on {action.target_identifier}. Outcome: {action.simulated_outcome or 'Success'}",
                    event_category=action.category,
                    source="ACTION",
                    source_id=action.action_id,
                    is_milestone=True,
                ))
                added_count += 1

        db.commit()
        return added_count
