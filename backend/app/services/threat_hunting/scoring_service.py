"""Educational scoring rubric and assessment evaluator for threat hunting investigations."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.threat_hunting import ThreatHunt


class HuntScoringService:
    """Evaluates student analytical rigor across 5 core threat hunting dimensions (100 pts total)."""

    @classmethod
    def evaluate_hunt(cls, db: Session, hunt: ThreatHunt) -> dict[str, Any]:
        """Compute educational rubric score and generate actionable learning feedback."""
        # 1. Evidence Quality & Breadth (max 20)
        evidence_list = hunt.evidence or []
        ev_score = 0
        ev_feedback = []
        if len(evidence_list) >= 4:
            ev_score += 12
        elif len(evidence_list) >= 2:
            ev_score += 8
        elif len(evidence_list) == 1:
            ev_score += 4
        else:
            ev_feedback.append("No evidence collected. A sound hunt relies on corroborated telemetry artifacts.")

        relevances = {e.relevance for e in evidence_list}
        if "SUPPORTING" in relevances and ("CONTRADICTING" in relevances or "CONTEXT" in relevances):
            ev_score += 4
        elif "SUPPORTING" in relevances:
            ev_score += 2

        with_notes = sum(1 for e in evidence_list if e.analyst_note and len(e.analyst_note.strip()) > 5)
        if with_notes >= 2:
            ev_score += 4
        elif with_notes >= 1:
            ev_score += 2

        ev_score = min(ev_score, 20)
        if ev_score >= 16:
            ev_feedback.append("Excellent evidence curation with strong contextual annotations.")
        elif ev_score >= 10:
            ev_feedback.append("Sufficient evidence collected; consider adding notes to every artifact.")

        # 2. Correlation & Pivoting (max 20)
        queries = []
        if hunt.query_history:
            try:
                queries = json.loads(hunt.query_history)
            except (json.JSONDecodeError, TypeError, ValueError):
                queries = []

        pivot_score = 0
        pivot_feedback = []
        if len(queries) >= 5:
            pivot_score += 12
        elif len(queries) >= 3:
            pivot_score += 8
        elif len(queries) >= 1:
            pivot_score += 4
        else:
            pivot_feedback.append("Zero query executions logged. Effective hunters iteratively refine filters.")

        if hunt.initial_pivot_value:
            pivot_score += 4

        # Diversity of query fields
        query_text = " ".join([q.get("query", "") for q in queries])
        field_hits = sum(1 for f in ["source_ip", "destination_ip", "domain", "protocol", "port"] if f in query_text.lower())
        if field_hits >= 3:
            pivot_score += 4
        elif field_hits >= 1:
            pivot_score += 2

        pivot_score = min(pivot_score, 20)
        if pivot_score >= 16:
            pivot_feedback.append("Thorough pivot investigation across network and host telemetry dimensions.")
        elif pivot_score >= 10:
            pivot_feedback.append("Good query exploration; try pivoting between IPs and domains more deeply.")

        # 3. Hypothesis Testing (max 20)
        hypotheses = hunt.hypotheses or []
        hyp_score = 0
        hyp_feedback = []
        if len(hypotheses) >= 2:
            hyp_score += 8
        elif len(hypotheses) == 1:
            hyp_score += 5
        else:
            hyp_feedback.append("No hypotheses formulated. Threat hunting begins with a falsifiable hypothesis.")

        resolved = [h for h in hypotheses if h.status in ("SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE")]
        if len(resolved) >= 2:
            hyp_score += 8
        elif len(resolved) >= 1:
            hyp_score += 5

        reasoned = [h for h in hypotheses if h.analyst_reasoning and len(h.analyst_reasoning.strip()) > 10]
        if len(reasoned) >= 1:
            hyp_score += 4

        hyp_score = min(hyp_score, 20)
        if hyp_score >= 16:
            hyp_feedback.append("Rigorous scientific hypothesis validation with explicit testing outcomes.")
        elif hyp_score >= 10:
            hyp_feedback.append("Hypotheses tested; remember to document analyst reasoning before closing.")

        # 4. Documentation & Findings (max 20)
        findings = hunt.findings or []
        notes = hunt.notes or []
        doc_score = 0
        doc_feedback = []
        if len(findings) >= 2:
            doc_score += 8
        elif len(findings) == 1:
            doc_score += 5
        else:
            doc_feedback.append("No formal findings logged. Document discoveries to feed SOC detection engineering.")

        findings_with_recs = [f for f in findings if f.mitigation_recommendation and len(f.mitigation_recommendation.strip()) > 10]
        if findings_with_recs:
            doc_score += 4

        if len(notes) >= 3:
            doc_score += 8
        elif len(notes) >= 1:
            doc_score += 4
        else:
            doc_feedback.append("Sparse analyst journal notes. Real-time documentation prevents cognitive bias.")

        doc_score = min(doc_score, 20)
        if doc_score >= 16:
            doc_feedback.append("Comprehensive findings and detailed journal entries.")
        elif doc_score >= 10:
            doc_feedback.append("Acceptable documentation; include defensive recommendations in findings.")

        # 5. Conclusion Soundness (max 20)
        conc_score = 0
        conc_feedback = []
        if hunt.conclusion_disposition:
            conc_score += 6
        else:
            conc_feedback.append("No final conclusion disposition specified.")

        if hunt.conclusion:
            c_len = len(hunt.conclusion.strip())
            if c_len >= 120:
                conc_score += 14
            elif c_len >= 50:
                conc_score += 8
            elif c_len > 10:
                conc_score += 4
            else:
                conc_feedback.append("Conclusion text is brief. Provide clear justification of results.")
        else:
            conc_feedback.append("Missing final conclusion narrative.")

        conc_score = min(conc_score, 20)
        if conc_score >= 16:
            conc_feedback.append("Defensible analytical conclusion backed by structured justification.")
        elif conc_score >= 10:
            conc_feedback.append("Solid conclusion; elaborate on impact and next steps.")

        total_score = ev_score + pivot_score + hyp_score + doc_score + conc_score

        if total_score >= 90:
            grade = "A"
        elif total_score >= 80:
            grade = "B"
        elif total_score >= 70:
            grade = "C"
        elif total_score >= 60:
            grade = "D"
        else:
            grade = "F"

        breakdown = {
            "evidence_quality": {"score": ev_score, "max": 20, "feedback": ev_feedback},
            "correlation_and_pivoting": {"score": pivot_score, "max": 20, "feedback": pivot_feedback},
            "hypothesis_testing": {"score": hyp_score, "max": 20, "feedback": hyp_feedback},
            "documentation_and_findings": {"score": doc_score, "max": 20, "feedback": doc_feedback},
            "conclusion_soundness": {"score": conc_score, "max": 20, "feedback": conc_feedback},
        }

        hunt.score = float(total_score)
        hunt.score_breakdown = json.dumps(breakdown)
        db.commit()

        return {
            "hunt_id": hunt.hunt_id,
            "total_score": total_score,
            "max_score": 100,
            "grade": grade,
            "breakdown": breakdown,
        }
