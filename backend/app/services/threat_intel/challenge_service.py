"""Challenge Service for Threat Intelligence & IOC Investigation training."""

import json
from datetime import datetime, timezone

from app.models.threat_intel import ThreatIntelChallenge, ThreatIntelChallengeAttempt
from app.models.user import User
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class ChallengeService:
    """Manages threat intelligence hands-on challenges and rubric-based evaluation."""

    @classmethod
    def list_challenges(cls, db: Session) -> list[ThreatIntelChallenge]:
        """Retrieve all available threat intel educational challenges."""
        return db.query(ThreatIntelChallenge).order_by(ThreatIntelChallenge.id.asc()).all()

    @classmethod
    def get_challenge_by_slug(cls, db: Session, slug: str) -> ThreatIntelChallenge:
        """Retrieve challenge detail by unique URL slug."""
        challenge = db.query(ThreatIntelChallenge).filter(ThreatIntelChallenge.slug == slug).first()
        if not challenge:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found.")
        return challenge

    @classmethod
    def evaluate_attempt(
        cls,
        db: Session,
        slug: str,
        user: User,
        selected_classification: str,
        hypothesis_text: str,
        evidence_notes: str,
        conclusion: str,
    ) -> ThreatIntelChallengeAttempt:
        """Evaluate student submission using a 5-dimension pedagogical rubric (20 points each).

        Rubric Dimensions:
        1. IOC Identification & Classification Match (20 pts)
        2. Evidence Review & Observation Rigor (20 pts)
        3. Threat Intelligence Interpretation (20 pts)
        4. Correlation & Relationship Context (20 pts)
        5. Defensible SOC Conclusion (20 pts)
        """
        challenge = cls.get_challenge_by_slug(db, slug)

        score = 0.0
        rubric_breakdown = {}

        # 1. Classification Match (20 pts)
        target_cls = challenge.expected_classification.upper()
        student_cls = selected_classification.upper().strip()

        if student_cls == target_cls:
            cls_score = 20.0
            cls_feedback = f"Correctly classified as {target_cls}."
        elif target_cls == "MALICIOUS" and student_cls == "SUSPICIOUS":
            cls_score = 14.0
            cls_feedback = "Accurately identified suspicious indicators, though definitive intelligence confirms malicious."
        elif target_cls == "BENIGN" and student_cls == "FALSE_POSITIVE":
            cls_score = 18.0
            cls_feedback = "Identified as non-malicious false positive."
        elif target_cls == "SUSPICIOUS" and student_cls == "MALICIOUS":
            cls_score = 10.0
            cls_feedback = "Aggressive classification without verified malicious intent; evidence points to suspicious activity."
        else:
            cls_score = 4.0
            cls_feedback = f"Mismatched classification. Expected {target_cls}, but selected {student_cls}."

        score += cls_score
        rubric_breakdown["ioc_classification"] = {
            "score": cls_score,
            "max": 20.0,
            "feedback": cls_feedback,
        }

        # 2. Evidence Review & Observation Rigor (20 pts)
        # Checks if student notes reference observed telemetry, ports, counts, or packet details
        evidence_lower = evidence_notes.lower()
        ev_keywords = ["port", "traffic", "packet", "flow", "alert", "dns", "http", "tls", "query", "payload", "request"]
        ev_hits = sum(1 for kw in ev_keywords if kw in evidence_lower)

        if len(evidence_notes.strip()) < 20:
            ev_score = 4.0
            ev_feedback = "Evidence notes are too brief. Document observed network telemetry and sensor data."
        elif ev_hits >= 3:
            ev_score = 20.0
            ev_feedback = "Comprehensive evidence review referencing multiple network artifacts and observation details."
        elif ev_hits >= 1:
            ev_score = 14.0
            ev_feedback = "Satisfactory evidence notes referencing observed telemetry."
        else:
            ev_score = 8.0
            ev_feedback = "Evidence documented, but lacks specific network artifact references (ports, queries, alerts)."

        score += ev_score
        rubric_breakdown["evidence_review"] = {
            "score": ev_score,
            "max": 20.0,
            "feedback": ev_feedback,
        }

        # 3. Threat Intelligence Interpretation (20 pts)
        # Checks hypothesis for sound reasoning (confidence, sources, reputation)
        hyp_lower = hypothesis_text.lower()
        intel_keywords = ["source", "reputation", "confidence", "threat", "intel", "synthetic", "feed", "reliability", "known"]
        intel_hits = sum(1 for kw in intel_keywords if kw in hyp_lower)

        if len(hypothesis_text.strip()) < 20:
            intel_score = 4.0
            intel_feedback = "Hypothesis is too short. Formulate a testable investigative hypothesis."
        elif intel_hits >= 2:
            intel_score = 20.0
            intel_feedback = "Strong analytical hypothesis incorporating threat intelligence confidence and reputation."
        elif intel_hits >= 1:
            intel_score = 14.0
            intel_feedback = "Good hypothesis touching on threat intelligence context."
        else:
            intel_score = 8.0
            intel_feedback = "Hypothesis stated, but does not explicitly reflect threat intelligence reliability or source confidence."

        score += intel_score
        rubric_breakdown["threat_intel_interpretation"] = {
            "score": intel_score,
            "max": 20.0,
            "feedback": intel_feedback,
        }

        # 4. Correlation & Relationship Context (20 pts)
        # Evaluates correlation across endpoints, domains, IPs, or captures
        all_text = f"{hypothesis_text} {evidence_notes} {conclusion}".lower()
        corr_keywords = ["correlat", "resolv", "connect", "associated", "relationship", "domain", "ip", "c2", "beacon", "host"]
        corr_hits = sum(1 for kw in corr_keywords if kw in all_text)

        if corr_hits >= 3:
            corr_score = 20.0
            corr_feedback = "Demonstrates multi-entity correlation linking indicators across network nodes and alerts."
        elif corr_hits >= 1:
            corr_score = 14.0
            corr_feedback = "Adequate correlation with related artifacts."
        else:
            corr_score = 8.0
            corr_feedback = "Limited entity correlation. Remember to analyze indicator relationships (e.g. domain -> IP resolution)."

        score += corr_score
        rubric_breakdown["correlation_context"] = {
            "score": corr_score,
            "max": 20.0,
            "feedback": corr_feedback,
        }

        # 5. Defensible SOC Conclusion & Action Plan (20 pts)
        # Evaluates final conclusion clarity and defensive recommendation
        conc_lower = conclusion.lower()
        action_keywords = ["block", "monitor", "watchlist", "close", "escalat", "recommend", "contain", "false positive", "benign"]
        action_hits = sum(1 for kw in action_keywords if kw in conc_lower)

        if len(conclusion.strip()) < 20:
            conc_score = 4.0
            conc_feedback = "Conclusion lacks actionable defensive next steps."
        elif action_hits >= 2:
            conc_score = 20.0
            conc_feedback = "Clear, defensible SOC conclusion with justified remediation or triage recommendations."
        elif action_hits >= 1:
            conc_score = 14.0
            conc_feedback = "Appropriate conclusion with a sensible defensive posture."
        else:
            conc_score = 8.0
            conc_feedback = "Conclusion provided, but lacks clear recommendations (e.g., add to watchlist, tune rule, escalate)."

        score += conc_score
        rubric_breakdown["soc_conclusion"] = {
            "score": conc_score,
            "max": 20.0,
            "feedback": conc_feedback,
        }

        passed = score >= 70.0

        feedback_obj = {
            "total_score": round(score, 1),
            "max_score": 100.0,
            "passed": passed,
            "passing_threshold": 70.0,
            "breakdown": rubric_breakdown,
            "educational_takeaway": (
                "Remember: An IOC is evidence, not absolute proof of compromise. Always corroborate threat intelligence "
                "with internal telemetry, check for potential false positives, and account for source confidence."
            ),
        }

        attempt = ThreatIntelChallengeAttempt(
            challenge_id=challenge.id,
            user_id=user.id,
            selected_classification=student_cls,
            hypothesis_text=hypothesis_text,
            evidence_notes=evidence_notes,
            conclusion=conclusion,
            score=round(score, 1),
            passed=passed,
            feedback=json.dumps(feedback_obj),
            created_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    @classmethod
    def get_user_attempts(cls, db: Session, user_id: int, challenge_id: int | None = None) -> list[ThreatIntelChallengeAttempt]:
        """Retrieve past attempts submitted by the user."""
        query = db.query(ThreatIntelChallengeAttempt).filter(ThreatIntelChallengeAttempt.user_id == user_id)
        if challenge_id:
            query = query.filter(ThreatIntelChallengeAttempt.challenge_id == challenge_id)
        return query.order_by(ThreatIntelChallengeAttempt.created_at.desc()).all()


challenge_service = ChallengeService()
