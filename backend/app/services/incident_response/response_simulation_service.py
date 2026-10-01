"""Simulated Response Action Service for Step 17.

STRICT EDUCATIONAL SAFETY RULE:
All actions are strictly simulation-only. They never execute OS commands,
never modify host network interfaces, never alter firewalls, and never lock production accounts.
Every record enforces `simulation_only = True`.
"""

import random
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import (
    IncidentPhase,
    IncidentStatus,
    ResponseActionCategory,
    ResponseActionStatus,
    ResponseActionType,
)
from app.models.incident import Incident, IncidentTimelineEvent, ResponseAction


class ResponseSimulationService:
    """Manages the formulation, simulated execution, and reversion of IR defensive actions."""

    @classmethod
    def list_actions(
        cls,
        db: Session,
        incident_id: int,
        category: str | None = None,
        status: str | None = None,
    ) -> list[ResponseAction]:
        query = select(ResponseAction).where(ResponseAction.incident_id == incident_id)
        if category:
            query = query.where(ResponseAction.category == category)
        if status:
            query = query.where(ResponseAction.status == status)

        return list(db.execute(query.order_by(ResponseAction.created_at.desc())).scalars().all())

    @classmethod
    def get_action(cls, db: Session, action_id_or_int: str | int) -> ResponseAction | None:
        if isinstance(action_id_or_int, int) or str(action_id_or_int).isdigit():
            query = select(ResponseAction).where(ResponseAction.id == int(action_id_or_int))
        else:
            query = select(ResponseAction).where(ResponseAction.action_id == str(action_id_or_int))
        return db.execute(query).scalar_one_or_none()

    @classmethod
    def propose_action(
        cls,
        db: Session,
        incident_id: int,
        category: str,
        action_type: str,
        target_type: str,
        target_identifier: str,
        reason: str,
        risk_assessment: str | None = None,
        expected_impact: str | None = None,
        user_id: int | None = None,
    ) -> ResponseAction:
        incident = db.get(Incident, incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Generate action ID
        rand_num = random.randint(100, 999)
        act_id = f"ACT-{datetime.now(timezone.utc).year}-{rand_num}"

        action = ResponseAction(
            action_id=act_id,
            incident_id=incident.id,
            category=category,
            action_type=action_type,
            target_type=target_type,
            target_identifier=target_identifier,
            status=ResponseActionStatus.PROPOSED,
            simulation_only=True,  # STRICT INVARIANT
            reason=reason,
            risk_assessment=risk_assessment,
            expected_impact=expected_impact,
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        return action

    @classmethod
    def execute_action(cls, db: Session, action_id_or_int: str | int, user_id: int | None = None) -> ResponseAction:
        action = cls.get_action(db, action_id_or_int)
        if not action:
            raise ValueError(f"Action {action_id_or_int} not found")

        now = datetime.now(timezone.utc)
        outcome = cls._simulate_outcome(action.action_type, action.target_identifier)

        action.status = ResponseActionStatus.EXECUTED
        action.executed_at = now
        action.executed_by_id = user_id
        action.simulated_outcome = outcome

        # Add milestone timeline event
        db.add(IncidentTimelineEvent(
            incident_id=action.incident_id,
            timestamp=now,
            title=f"Response Action Executed: {action.action_type}",
            description=f"Simulated {action.category} performed on {action.target_identifier}. Outcome: {outcome}",
            event_category=action.category,
            source="ACTION",
            source_id=action.action_id,
            is_milestone=True,
            created_by_id=user_id,
        ))

        # Advance incident phase if appropriate
        incident = db.get(Incident, action.incident_id)
        if incident:
            if action.category == ResponseActionCategory.CONTAINMENT and incident.status in (IncidentStatus.NEW, IncidentStatus.TRIAGED, IncidentStatus.INVESTIGATING):
                incident.status = IncidentStatus.CONTAINMENT
                incident.phase = IncidentPhase.CONTAINMENT_ERADICATION_RECOVERY
                if not incident.contained_at:
                    incident.contained_at = now
            elif action.category == ResponseActionCategory.ERADICATION and incident.status == IncidentStatus.CONTAINMENT:
                incident.status = IncidentStatus.ERADICATION
                if not incident.eradicated_at:
                    incident.eradicated_at = now
            elif action.category == ResponseActionCategory.RECOVERY and incident.status == IncidentStatus.ERADICATION:
                incident.status = IncidentStatus.RECOVERY
                if not incident.recovered_at:
                    incident.recovered_at = now

        db.commit()
        db.refresh(action)
        return action

    @classmethod
    def revert_action(cls, db: Session, action_id_or_int: str | int, user_id: int | None = None) -> ResponseAction:
        action = cls.get_action(db, action_id_or_int)
        if not action:
            raise ValueError(f"Action {action_id_or_int} not found")

        now = datetime.now(timezone.utc)
        action.status = ResponseActionStatus.REVERTED
        action.reverted_at = now

        db.add(IncidentTimelineEvent(
            incident_id=action.incident_id,
            timestamp=now,
            title=f"Response Action Reverted: {action.action_type}",
            description=f"Action on {action.target_identifier} was safely reversed in simulation.",
            event_category=action.category,
            source="ACTION",
            source_id=action.action_id,
            is_milestone=False,
            created_by_id=user_id,
        ))

        db.commit()
        db.refresh(action)
        return action

    @classmethod
    def _simulate_outcome(cls, action_type: str, target: str) -> str:
        """Deterministic educational explanation of simulated outcome."""
        outcomes = {
            ResponseActionType.SIMULATE_HOST_ISOLATION: f"[SIMULATION] Host '{target}' isolated via virtual switch VLAN quarantine. Only SOC telemetry collector retains access.",
            ResponseActionType.SIMULATE_ACCOUNT_RESTRICTION: f"[SIMULATION] Account '{target}' locked in identity directory. Active Kerberos tickets and refresh tokens invalidated.",
            ResponseActionType.SIMULATE_NETWORK_BLOCK: f"[SIMULATION] Perimeter firewall drop rule enforced for '{target}' across all inbound/outbound egress interfaces.",
            ResponseActionType.SIMULATE_IOC_BLOCK: f"[SIMULATION] Indicator '{target}' added to enterprise DNS Sinkhole and Web Proxy blocklist.",
            ResponseActionType.SIMULATE_SESSION_REVOCATION: f"[SIMULATION] Active VPN and web SSO sessions terminated for '{target}'. Step-up MFA challenge required upon next login.",
            ResponseActionType.SIMULATE_REMOVE_INDICATOR: f"[SIMULATION] Malicious file / hash '{target}' quarantined across all monitored host endpoints via EDR agent.",
            ResponseActionType.SIMULATE_REMOVE_PERSISTENCE: f"[SIMULATION] Scheduled task / autostart registry key '{target}' successfully deleted.",
            ResponseActionType.SIMULATE_RESET_CREDENTIAL: f"[SIMULATION] Password reset enforced for '{target}'. Temporary random password generated and delivered out-of-band.",
            ResponseActionType.SIMULATE_CLEAN_HOST: f"[SIMULATION] Antivirus full-disk scan and memory scrubbing executed on '{target}'. Staged artifacts removed.",
            ResponseActionType.SIMULATE_RESTORE_HOST: f"[SIMULATION] Host '{target}' network access restored to production VLAN following integrity validation.",
            ResponseActionType.SIMULATE_RESTORE_SERVICE: f"[SIMULATION] Application daemon '{target}' restarted under enhanced health check monitoring.",
            ResponseActionType.SIMULATE_REENABLE_ACCOUNT: f"[SIMULATION] Account '{target}' re-enabled following identity verification and credentials rotation.",
            ResponseActionType.SIMULATE_RESTORE_NETWORK: f"[SIMULATION] Normal firewall forwarding resumed for '{target}'. Temporary block removed.",
        }
        return outcomes.get(action_type, f"[SIMULATION] Simulated action '{action_type}' completed successfully for target '{target}'.")
