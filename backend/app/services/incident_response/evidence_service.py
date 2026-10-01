"""Unified Evidence Management & Chain of Custody Service for Step 17.

Handles cross-engine evidence aggregation (PCAP, Alerts, SIEM, Endpoint, Threat Intel),
SHA-256 integrity hash verification, and educational audit logging.
"""

import hashlib
import json
import random
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import EvidenceAuditAction, EvidenceRelevance
from app.models.incident import EvidenceAuditLog, Incident, IncidentEvidence


class EvidenceService:
    """Manages cross-engine evidence items and chain of custody tracking."""

    @classmethod
    def list_evidence(
        cls,
        db: Session,
        incident_id: int,
        evidence_type: str | None = None,
        source_engine: str | None = None,
    ) -> list[IncidentEvidence]:
        query = select(IncidentEvidence).where(IncidentEvidence.incident_id == incident_id).options(
            selectinload(IncidentEvidence.audit_logs)
        )
        if evidence_type:
            query = query.where(IncidentEvidence.evidence_type == evidence_type)
        if source_engine:
            query = query.where(IncidentEvidence.source_engine == source_engine)

        return list(db.execute(query.order_by(IncidentEvidence.collected_at.desc())).scalars().all())

    @classmethod
    def get_evidence(cls, db: Session, evidence_id_or_int: str | int) -> IncidentEvidence | None:
        query = select(IncidentEvidence).options(
            selectinload(IncidentEvidence.audit_logs)
        )
        if isinstance(evidence_id_or_int, int) or str(evidence_id_or_int).isdigit():
            query = query.where(IncidentEvidence.id == int(evidence_id_or_int))
        else:
            query = query.where(IncidentEvidence.evidence_id == str(evidence_id_or_int))

        return db.execute(query).scalar_one_or_none()

    @classmethod
    def add_evidence(
        cls,
        db: Session,
        incident_id: int,
        title: str,
        description: str,
        evidence_type: str,
        source_engine: str,
        source_id: str | None = None,
        source_ref: str | None = None,
        data_payload: str | dict | None = None,
        relevance: str = EvidenceRelevance.SUPPORTING,
        user_id: int | None = None,
    ) -> IncidentEvidence:
        incident = db.get(Incident, incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Serialized payload
        payload_str = json.dumps(data_payload) if isinstance(data_payload, dict) else (data_payload or "")

        # Compute deterministic SHA-256 integrity hash
        hash_val = hashlib.sha256(payload_str.encode("utf-8") if payload_str else f"{title}:{source_id}".encode()).hexdigest()

        # Generate evidence ID
        rand_suffix = random.randint(10000, 99999)
        evd_id = f"EVD-{datetime.now(timezone.utc).year}-{rand_suffix}"

        evidence = IncidentEvidence(
            evidence_id=evd_id,
            incident_id=incident.id,
            title=title,
            description=description,
            evidence_type=evidence_type,
            source_engine=source_engine,
            source_id=source_id,
            source_ref=source_ref,
            hash_sha256=hash_val,
            relevance=relevance,
            is_contained=False,
            collected_by_id=user_id,
            collected_at=datetime.now(timezone.utc),
            data_payload=payload_str,
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        # Log Chain of Custody record
        cls.log_audit(
            db=db,
            evidence_id=evidence.id,
            action=EvidenceAuditAction.ATTACHED,
            details=f"Evidence attached from {source_engine} with initial SHA-256 hash: {hash_val[:12]}...",
            user_id=user_id,
        )

        return evidence

    @classmethod
    def log_audit(
        cls,
        db: Session,
        evidence_id: int,
        action: str,
        details: str | None = None,
        user_id: int | None = None,
    ) -> EvidenceAuditLog:
        audit = EvidenceAuditLog(
            evidence_id=evidence_id,
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @classmethod
    def verify_evidence_hash(cls, db: Session, evidence_id: int, user_id: int | None = None) -> dict[str, Any]:
        """Verifies the integrity of the evidence payload against its stored hash."""
        evidence = db.get(IncidentEvidence, evidence_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")

        payload_bytes = (evidence.data_payload or "").encode("utf-8")
        current_hash = hashlib.sha256(payload_bytes if payload_bytes else f"{evidence.title}:{evidence.source_id}".encode()).hexdigest()
        is_valid = current_hash == evidence.hash_sha256

        cls.log_audit(
            db=db,
            evidence_id=evidence.id,
            action=EvidenceAuditAction.HASH_VERIFIED,
            details=f"Cryptographic verification {'PASSED' if is_valid else 'FAILED'}. Computed: {current_hash[:12]}...",
            user_id=user_id,
        )

        return {
            "evidence_id": evidence.evidence_id,
            "stored_hash": evidence.hash_sha256,
            "computed_hash": current_hash,
            "is_valid": is_valid,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def update_evidence(
        cls,
        db: Session,
        evidence_id: int,
        updates: dict[str, Any],
        user_id: int | None = None,
    ) -> IncidentEvidence | None:
        evidence = db.get(IncidentEvidence, evidence_id)
        if not evidence:
            return None

        for key in ("relevance", "is_contained", "description"):
            if key in updates:
                setattr(evidence, key, updates[key])

        cls.log_audit(
            db=db,
            evidence_id=evidence.id,
            action=EvidenceAuditAction.ANNOTATED,
            details=f"Evidence metadata updated: {', '.join(updates.keys())}",
            user_id=user_id,
        )

        db.commit()
        db.refresh(evidence)
        return evidence
