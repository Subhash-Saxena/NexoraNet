"""Educational SOC Challenge & Scenario Grading Service."""

import json
from datetime import datetime, timezone

from app.models.enums import TriageClassification
from app.models.soc import Investigation, SocChallenge, SocChallengeAttempt
from app.models.user import User
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class ChallengeService:
    """Manages educational SOC challenge scenarios and qualitative evaluations."""

    @classmethod
    def evaluate_submission(
        cls,
        db: Session,
        actor: User,
        challenge_id: int,
        investigation_id: int,
        identified_evidence: list[str],
        observations: str,
        hypothesis: str,
        classification: TriageClassification,
        conclusion: str,
    ) -> SocChallengeAttempt:
        """Evaluate student submission against scenario rubric and provide educational feedback."""
        challenge = db.query(SocChallenge).filter(SocChallenge.id == challenge_id).first()
        if not challenge:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge scenario not found.")

        investigation = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not investigation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found.")

        rubric = json.loads(challenge.rubric_json) if challenge.rubric_json else {}
        expected_obs = json.loads(challenge.expected_observations) if challenge.expected_observations else []
        target_classifications = rubric.get("valid_classifications", ["SUSPICIOUS", "BENIGN", "FALSE_POSITIVE"])

        # 1. Evidence Identification Score (20 pts)
        ev_score = 0.0
        if identified_evidence and len(identified_evidence) >= 1:
            ev_score = min(20.0, len(identified_evidence) * 10.0)

        # 2. Correct Observation Score (20 pts)
        obs_score = 0.0
        obs_lower = observations.lower()
        if expected_obs:
            matched_keywords = sum(1 for kw in expected_obs if kw.lower() in obs_lower)
            obs_score = min(20.0, (matched_keywords / len(expected_obs)) * 20.0)
            if obs_score < 10.0 and len(observations.strip()) > 30:
                obs_score = 12.0  # Effort credit
        else:
            obs_score = 20.0 if len(observations.strip()) > 20 else 10.0

        # 3. Investigation Process Score (20 pts)
        # Assesses if student investigated hypotheses, added notes, or checked evidence
        proc_score = 0.0
        if investigation.hypotheses:
            proc_score += 10.0
        if investigation.notes:
            proc_score += 5.0
        if len(hypothesis.strip()) > 15:
            proc_score += 5.0
        proc_score = min(20.0, proc_score)

        # 4. Classification Score (20 pts)
        class_val = classification.value if hasattr(classification, "value") else str(classification)
        class_score = 20.0 if class_val in target_classifications else 8.0

        # 5. Conclusion Quality Score (20 pts)
        conc_score = 0.0
        if len(conclusion.strip()) >= 50:
            conc_score = 20.0
        elif len(conclusion.strip()) >= 20:
            conc_score = 12.0
        else:
            conc_score = 5.0

        total_score = round(ev_score + obs_score + proc_score + class_score + conc_score, 1)

        breakdown = {
            "evidence_identification": ev_score,
            "observation_quality": obs_score,
            "investigation_process": proc_score,
            "classification_accuracy": class_score,
            "conclusion_thoroughness": conc_score,
        }

        # Educational Feedback Construction
        what_you_did_well = []
        if ev_score >= 15:
            what_you_did_well.append("Identified concrete packet evidence and artifacts.")
        if obs_score >= 15:
            what_you_did_well.append("Accurately observed key network protocol behaviors.")
        if proc_score >= 15:
            what_you_did_well.append("Followed structured SOC workflow by formulating testable hypotheses.")
        if class_score >= 15:
            what_you_did_well.append(f"Arrived at a defensible classification ({class_val}).")
        if not what_you_did_well:
            what_you_did_well.append("Completed the forensic investigation workflow from alert to conclusion.")

        # Suggested Curriculum Review
        suggested_review = []
        if challenge.scenario_type == "TCP":
            suggested_review.append({
                "topic": "TCP Three-Way Handshake & Flags",
                "route": "/learning/lessons/tcp-handshake-fundamentals",
                "reason": "Review TCP control flags and connection termination mechanics.",
            })
        elif challenge.scenario_type == "DNS":
            suggested_review.append({
                "topic": "DNS Architecture & Resolution",
                "route": "/learning/lessons/dns-resolution-process",
                "reason": "Deepen understanding of NXDOMAIN response codes and query patterns.",
            })
        elif challenge.scenario_type == "ARP":
            suggested_review.append({
                "topic": "ARP & Layer 2 Resolution",
                "route": "/learning/lessons/arp-protocol-analysis",
                "reason": "Examine how Layer 2 binding conflicts and gratuitous ARPs operate.",
            })
        else:
            suggested_review.append({
                "topic": "Defensive Packet Analysis Methodology",
                "route": "/packet-analysis",
                "reason": "Practice analyzing 5-tuple conversations and packet timelines.",
            })

        feedback_data = {
            "what_you_did_well": what_you_did_well,
            "evidence_identified": identified_evidence,
            "investigation_steps_completed": [
                "Inspect Alert Telemetry",
                "Formulate Testable Hypothesis",
                "Review Corroborating Evidence",
                "Document Forensic Conclusion",
            ],
            "suggested_review": suggested_review,
        }

        attempt = SocChallengeAttempt(
            challenge_id=challenge.id,
            user_id=actor.id,
            investigation_id=investigation.id,
            status="COMPLETED",
            score=total_score,
            score_breakdown=json.dumps(breakdown),
            feedback=json.dumps(feedback_data),
            submitted_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt


challenge_service = ChallengeService()
