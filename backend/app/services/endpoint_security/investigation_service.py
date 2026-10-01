"""Investigation lifecycle, hypothesis management, evidence collection, and scoring service."""

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.endpoint_security import (
    EndpointConclusion,
    EndpointEvidence,
    EndpointFinding,
    EndpointHost,
    EndpointHypothesis,
    EndpointInvestigation,
)


class InvestigationService:
    """Manages student host investigations with IDOR safety and training rubric evaluation."""

    @staticmethod
    def list_investigations(
        db: Session,
        user_id: int | None = None,
        host_id: int | None = None,
        status: str | None = None,
        priority: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[EndpointInvestigation], int]:
        """List investigations with optional host/user/status filters."""
        stmt = (
            select(EndpointInvestigation)
            .options(
                joinedload(EndpointInvestigation.host),
                joinedload(EndpointInvestigation.conclusion),
            )
        )
        if user_id:
            stmt = stmt.where(EndpointInvestigation.user_id == user_id)
        if host_id:
            stmt = stmt.where(EndpointInvestigation.host_id == host_id)
        if status:
            stmt = stmt.where(EndpointInvestigation.status == status.upper())
        if priority:
            stmt = stmt.where(EndpointInvestigation.priority == priority.upper())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        stmt = stmt.order_by(EndpointInvestigation.created_at.desc()).offset(skip).limit(limit)
        return list(db.scalars(stmt).unique().all()), total

    @staticmethod
    def create_investigation(
        db: Session,
        user_id: int,
        host_id: int,
        title: str,
        description: str,
        priority: str = "P2",
        scenario_slug: str | None = None,
    ) -> EndpointInvestigation:
        """Create a new endpoint investigation case."""
        host = db.get(EndpointHost, host_id)
        if not host:
            raise ValueError(f"Host with id {host_id} does not exist.")

        # Generate stable ID
        now = datetime.now(timezone.utc)
        year = now.year
        count = db.scalar(select(func.count(EndpointInvestigation.id))) or 0
        stable_id = f"EINV-{year}-{count + 1:04d}"

        inv = EndpointInvestigation(
            stable_id=stable_id,
            host_id=host_id,
            user_id=user_id,
            title=title.strip(),
            description=description.strip(),
            priority=priority.upper(),
            status="OPEN",
            scenario_slug=scenario_slug,
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def get_investigation(
        db: Session, investigation_id: int, user_id: int | None = None
    ) -> EndpointInvestigation | None:
        """Fetch investigation and verify owner permissions (IDOR protection)."""
        stmt = (
            select(EndpointInvestigation)
            .options(
                joinedload(EndpointInvestigation.host),
                joinedload(EndpointInvestigation.hypotheses),
                joinedload(EndpointInvestigation.evidence),
                joinedload(EndpointInvestigation.findings),
                joinedload(EndpointInvestigation.conclusion),
            )
            .where(EndpointInvestigation.id == investigation_id)
        )
        if user_id is not None:
            stmt = stmt.where(EndpointInvestigation.user_id == user_id)

        return db.scalars(stmt).unique().first()

    @staticmethod
    def update_investigation(
        db: Session,
        investigation_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> EndpointInvestigation | None:
        """Update core metadata of an ongoing investigation."""
        inv = InvestigationService.get_investigation(db, investigation_id, user_id)
        if not inv:
            return None

        if title is not None:
            inv.title = title.strip()
        if description is not None:
            inv.description = description.strip()
        if status is not None:
            inv.status = status.upper()
        if priority is not None:
            inv.priority = priority.upper()

        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def add_hypothesis(
        db: Session,
        investigation_id: int,
        user_id: int,
        statement: str,
        status: str = "OPEN",
        confidence: str = "MEDIUM",
        analyst_notes: str | None = None,
    ) -> EndpointHypothesis:
        """Register an analyst hypothesis in an investigation."""
        inv = InvestigationService.get_investigation(db, investigation_id, user_id)
        if not inv:
            raise ValueError(f"Investigation {investigation_id} not found or access denied.")

        hypothesis = EndpointHypothesis(
            investigation_id=investigation_id,
            statement=statement.strip(),
            status=status.upper(),
            confidence=confidence.upper(),
            analyst_notes=analyst_notes.strip() if analyst_notes else None,
        )
        db.add(hypothesis)

        # Transition investigation to INVESTIGATING if currently OPEN
        if inv.status == "OPEN":
            inv.status = "INVESTIGATING"

        db.commit()
        db.refresh(hypothesis)
        return hypothesis

    @staticmethod
    def update_hypothesis(
        db: Session,
        hypothesis_id: int,
        user_id: int,
        status: str | None = None,
        confidence: str | None = None,
        analyst_notes: str | None = None,
    ) -> EndpointHypothesis | None:
        """Update test state and confidence of a working hypothesis."""
        hyp_stmt = (
            select(EndpointHypothesis)
            .join(EndpointInvestigation)
            .where(
                EndpointHypothesis.id == hypothesis_id,
                EndpointInvestigation.user_id == user_id,
            )
        )
        hyp = db.scalars(hyp_stmt).first()
        if not hyp:
            return None

        if status is not None:
            hyp.status = status.upper()
        if confidence is not None:
            hyp.confidence = confidence.upper()
        if analyst_notes is not None:
            hyp.analyst_notes = analyst_notes.strip()

        db.commit()
        db.refresh(hyp)
        return hyp

    @staticmethod
    def add_evidence(
        db: Session,
        investigation_id: int,
        user_id: int,
        title: str,
        description: str,
        evidence_type: str = "EVENT",
        relevance: str = "SUPPORTING",
        event_id: int | None = None,
        hypothesis_id: int | None = None,
        artifact_data: dict[str, Any] | None = None,
    ) -> EndpointEvidence:
        """Attach verified event or artifact evidence to an investigation."""
        inv = InvestigationService.get_investigation(db, investigation_id, user_id)
        if not inv:
            raise ValueError(f"Investigation {investigation_id} not found or access denied.")

        evidence = EndpointEvidence(
            investigation_id=investigation_id,
            hypothesis_id=hypothesis_id,
            event_id=event_id,
            evidence_type=evidence_type.upper(),
            title=title.strip(),
            description=description.strip(),
            relevance=relevance.upper(),
            artifact_data_json=json.dumps(artifact_data) if artifact_data else None,
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    @staticmethod
    def add_finding(
        db: Session,
        investigation_id: int,
        user_id: int,
        title: str,
        narrative: str,
        mitre_attack_id: str | None = None,
        severity: str = "MEDIUM",
    ) -> EndpointFinding:
        """Document an analytical milestone finding."""
        inv = InvestigationService.get_investigation(db, investigation_id, user_id)
        if not inv:
            raise ValueError(f"Investigation {investigation_id} not found or access denied.")

        finding = EndpointFinding(
            investigation_id=investigation_id,
            title=title.strip(),
            narrative=narrative.strip(),
            mitre_attack_id=mitre_attack_id.strip() if mitre_attack_id else None,
            severity=severity.upper(),
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        return finding

    @staticmethod
    def submit_conclusion(
        db: Session,
        investigation_id: int,
        user_id: int,
        summary: str,
        verdict: str,
        lessons_learned: str | None = None,
    ) -> EndpointConclusion:
        """Conclude investigation, evaluate rubric score, and award Training Score."""
        inv = InvestigationService.get_investigation(db, investigation_id, user_id)
        if not inv:
            raise ValueError(f"Investigation {investigation_id} not found or access denied.")

        # Compute Training Score (0-100 rubric)
        # 1. Evidence Selection (25 pts): at least 2 pieces of evidence collected
        evidence_count = len(inv.evidence)
        evidence_score = min(25, evidence_count * 10)

        # 2. Hypothesis Formulation (25 pts): at least 1 hypothesis formed and tested
        hyp_count = len(inv.hypotheses)
        tested_hyp = sum(1 for h in inv.hypotheses if h.status != "OPEN")
        hypothesis_score = min(25, (hyp_count * 10) + (tested_hyp * 15))

        # 3. Findings Narrative (25 pts): at least 1 documented analytical finding
        findings_count = len(inv.findings)
        findings_score = min(25, findings_count * 15)

        # 4. Conclusion & Lessons Learned Quality (25 pts): thorough explanation (>50 characters)
        summary_quality = 15 if len(summary.strip()) >= 40 else 5
        lessons_quality = 10 if lessons_learned and len(lessons_learned.strip()) >= 20 else 5
        conclusion_score = summary_quality + lessons_quality

        total_training_score = min(100, evidence_score + hypothesis_score + findings_score + conclusion_score)

        breakdown = {
            "evidence_selection": {"score": evidence_score, "max": 25},
            "hypothesis_testing": {"score": hypothesis_score, "max": 25},
            "findings_documentation": {"score": findings_score, "max": 25},
            "conclusion_quality": {"score": conclusion_score, "max": 25},
            "total_score": total_training_score,
            "disclaimer": "This is an educational Training Score evaluating investigative methodology on synthetic data.",
        }

        # Check existing conclusion or create new
        conc = inv.conclusion
        if not conc:
            conc = EndpointConclusion(
                investigation_id=investigation_id,
                summary=summary.strip(),
                verdict=verdict.upper(),
                training_score=total_training_score,
                score_breakdown_json=json.dumps(breakdown),
                lessons_learned=lessons_learned.strip() if lessons_learned else None,
            )
            db.add(conc)
        else:
            conc.summary = summary.strip()
            conc.verdict = verdict.upper()
            conc.training_score = total_training_score
            conc.score_breakdown_json = json.dumps(breakdown)
            conc.lessons_learned = lessons_learned.strip() if lessons_learned else None

        # Finalize investigation
        inv.status = "COMPLETED"
        inv.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(conc)
        return conc
