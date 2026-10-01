"""Hypothesis testing, evidence linking, findings documentation, and note keeping service."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import (
    HuntConfidence,
    HuntEvidenceRelevance,
    HuntHypothesisStatus,
)
from app.models.threat_hunting import (
    ThreatHuntEvidence,
    ThreatHuntFinding,
    ThreatHuntHypothesis,
    ThreatHuntNote,
)


class HuntInvestigationService:
    """Manages the scientific investigation workflow: Hypotheses -> Evidence -> Findings -> Notes."""

    # -------------------------------------------------------------------------
    # Hypotheses
    # -------------------------------------------------------------------------

    @classmethod
    def list_hypotheses(cls, db: Session, hunt_id: int) -> list[ThreatHuntHypothesis]:
        """List all hypotheses formulated for a hunt session."""
        stmt = (
            select(ThreatHuntHypothesis)
            .where(ThreatHuntHypothesis.hunt_id == hunt_id)
            .order_by(ThreatHuntHypothesis.created_at.asc())
        )
        return list(db.scalars(stmt).all())

    @classmethod
    def get_hypothesis(cls, db: Session, hypothesis_id: int) -> ThreatHuntHypothesis | None:
        """Fetch hypothesis by ID."""
        return db.get(ThreatHuntHypothesis, hypothesis_id)

    @classmethod
    def create_hypothesis(
        cls,
        db: Session,
        hunt_id: int,
        title: str,
        description: str,
        confidence: str = HuntConfidence.MEDIUM.value,
    ) -> ThreatHuntHypothesis:
        """Formulate a new analytical hypothesis."""
        hypothesis = ThreatHuntHypothesis(
            hunt_id=hunt_id,
            title=title,
            description=description,
            status=HuntHypothesisStatus.OPEN.value,
            confidence=confidence,
        )
        db.add(hypothesis)
        db.commit()
        db.refresh(hypothesis)
        return hypothesis

    @classmethod
    def update_hypothesis(
        cls,
        db: Session,
        hypothesis_id: int,
        status: str | None = None,
        confidence: str | None = None,
        analyst_reasoning: str | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> ThreatHuntHypothesis | None:
        """Update test state or analyst reasoning on a hypothesis."""
        hyp = db.get(ThreatHuntHypothesis, hypothesis_id)
        if not hyp:
            return None
        if status is not None:
            hyp.status = status
        if confidence is not None:
            hyp.confidence = confidence
        if analyst_reasoning is not None:
            hyp.analyst_reasoning = analyst_reasoning
        if title is not None:
            hyp.title = title
        if description is not None:
            hyp.description = description
        db.commit()
        db.refresh(hyp)
        return hyp

    @classmethod
    def delete_hypothesis(cls, db: Session, hypothesis_id: int) -> bool:
        """Remove a hypothesis."""
        hyp = db.get(ThreatHuntHypothesis, hypothesis_id)
        if not hyp:
            return False
        db.delete(hyp)
        db.commit()
        return True

    # -------------------------------------------------------------------------
    # Evidence
    # -------------------------------------------------------------------------

    @classmethod
    def list_evidence(
        cls,
        db: Session,
        hunt_id: int,
        hypothesis_id: int | None = None,
    ) -> list[ThreatHuntEvidence]:
        """List all evidence collected for a hunt, optionally scoped to a hypothesis."""
        stmt = select(ThreatHuntEvidence).where(ThreatHuntEvidence.hunt_id == hunt_id)
        if hypothesis_id is not None:
            stmt = stmt.where(ThreatHuntEvidence.hypothesis_id == hypothesis_id)
        stmt = stmt.order_by(ThreatHuntEvidence.created_at.desc())
        return list(db.scalars(stmt).all())

    @classmethod
    def add_evidence(
        cls,
        db: Session,
        hunt_id: int,
        evidence_type: str,
        source_id: str,
        description: str,
        hypothesis_id: int | None = None,
        relevance: str = HuntEvidenceRelevance.SUPPORTING.value,
        analyst_note: str | None = None,
        data_snapshot: dict[str, Any] | None = None,
    ) -> ThreatHuntEvidence:
        """Collect and bind evidence to a hunt and optional hypothesis."""
        evidence = ThreatHuntEvidence(
            hunt_id=hunt_id,
            hypothesis_id=hypothesis_id,
            evidence_type=evidence_type,
            source_id=source_id,
            description=description,
            relevance=relevance,
            analyst_note=analyst_note,
            data_snapshot=json.dumps(data_snapshot) if data_snapshot else None,
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    @classmethod
    def update_evidence(
        cls,
        db: Session,
        evidence_id: int,
        relevance: str | None = None,
        analyst_note: str | None = None,
        hypothesis_id: int | None = None,
    ) -> ThreatHuntEvidence | None:
        """Update relevance orientation or rationale for an evidence item."""
        ev = db.get(ThreatHuntEvidence, evidence_id)
        if not ev:
            return None
        if relevance is not None:
            ev.relevance = relevance
        if analyst_note is not None:
            ev.analyst_note = analyst_note
        if hypothesis_id is not None:
            ev.hypothesis_id = hypothesis_id
        db.commit()
        db.refresh(ev)
        return ev

    @classmethod
    def delete_evidence(cls, db: Session, evidence_id: int) -> bool:
        """Delete an evidence record."""
        ev = db.get(ThreatHuntEvidence, evidence_id)
        if not ev:
            return False
        db.delete(ev)
        db.commit()
        return True

    # -------------------------------------------------------------------------
    # Findings
    # -------------------------------------------------------------------------

    @classmethod
    def list_findings(cls, db: Session, hunt_id: int) -> list[ThreatHuntFinding]:
        """List findings documented during the hunt."""
        stmt = (
            select(ThreatHuntFinding)
            .where(ThreatHuntFinding.hunt_id == hunt_id)
            .order_by(ThreatHuntFinding.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    @classmethod
    def create_finding(
        cls,
        db: Session,
        hunt_id: int,
        title: str,
        description: str,
        finding_type: str,
        confidence: str = HuntConfidence.MEDIUM.value,
        evidence_count: int = 0,
        mitigation_recommendation: str | None = None,
    ) -> ThreatHuntFinding:
        """Record an analytical finding discovered through threat hunting."""
        finding = ThreatHuntFinding(
            hunt_id=hunt_id,
            title=title,
            description=description,
            finding_type=finding_type,
            confidence=confidence,
            evidence_count=evidence_count,
            mitigation_recommendation=mitigation_recommendation,
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        return finding

    @classmethod
    def delete_finding(cls, db: Session, finding_id: int) -> bool:
        """Remove a finding."""
        f = db.get(ThreatHuntFinding, finding_id)
        if not f:
            return False
        db.delete(f)
        db.commit()
        return True

    # -------------------------------------------------------------------------
    # Notes
    # -------------------------------------------------------------------------

    @classmethod
    def list_notes(cls, db: Session, hunt_id: int) -> list[ThreatHuntNote]:
        """List analyst journal notes for the hunt."""
        stmt = (
            select(ThreatHuntNote)
            .where(ThreatHuntNote.hunt_id == hunt_id)
            .order_by(ThreatHuntNote.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    @classmethod
    def add_note(
        cls,
        db: Session,
        hunt_id: int,
        user_id: int,
        author_name: str,
        content: str,
        related_event_id: str | None = None,
        related_alert_id: int | None = None,
        related_ioc_id: int | None = None,
        related_hypothesis_id: int | None = None,
    ) -> ThreatHuntNote:
        """Add an analyst note to the hunt journal."""
        note = ThreatHuntNote(
            hunt_id=hunt_id,
            user_id=user_id,
            author_name=author_name,
            content=content,
            related_event_id=related_event_id,
            related_alert_id=related_alert_id,
            related_ioc_id=related_ioc_id,
            related_hypothesis_id=related_hypothesis_id,
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @classmethod
    def delete_note(cls, db: Session, note_id: int) -> bool:
        """Delete a note."""
        n = db.get(ThreatHuntNote, note_id)
        if not n:
            return False
        db.delete(n)
        db.commit()
        return True
