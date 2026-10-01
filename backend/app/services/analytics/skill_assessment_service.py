"""Skill Assessment Service - Explainable, deterministic cybersecurity skill evaluation."""

from datetime import datetime, timezone
from typing import Any, ClassVar

from app.models.analytics import Skill, SkillAssessment
from app.models.challenge import Challenge, ChallengeAttempt
from app.models.enums import AttemptStatus, SkillConfidence
from app.models.mock_test import MockTestAttempt
from app.models.progress import LabAttempt
from app.models.soc_scenario import ScenarioAttempt
from app.models.user import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


class SkillAssessmentService:
    """Calculates explainable, deterministic student skill proficiencies with recency weighting."""

    CATEGORY_MAP: ClassVar[dict[str, list[str]]] = {
        "NETWORKING": ["PCAP_ANALYSIS", "NETWORK_DEFENSE", "PROTOCOL_FORENSICS"],
        "NETWORK_SECURITY": ["NETWORK_DEFENSE", "DETECTION_ENGINEERING", "FIREWALL"],
        "TCP_IP": ["PROTOCOL_FORENSICS", "PCAP_ANALYSIS"],
        "SUBNETTING": ["NETWORK_DEFENSE"],
        "DNS": ["PROTOCOL_FORENSICS", "THREAT_INTEL"],
        "DHCP": ["PROTOCOL_FORENSICS", "NETWORK_DEFENSE"],
        "HTTP_HTTPS": ["PROTOCOL_FORENSICS", "SIEM_ANALYSIS"],
        "TCP_UDP": ["PROTOCOL_FORENSICS", "PCAP_ANALYSIS"],
        "ROUTING": ["NETWORK_DEFENSE"],
        "SWITCHING": ["NETWORK_DEFENSE"],
        "VLAN": ["NETWORK_DEFENSE"],
        "FIREWALLS": ["NETWORK_DEFENSE", "SOAR_AUTOMATION"],
        "IDS_IPS": ["DETECTION_ENGINEERING", "NETWORK_DEFENSE"],
        "PACKET_ANALYSIS": ["PCAP_ANALYSIS", "PROTOCOL_FORENSICS"],
        "TRAFFIC_ANALYSIS": ["PCAP_ANALYSIS", "SIEM_ANALYSIS"],
        "SIEM": ["SIEM_ANALYSIS", "LOG_ANALYSIS"],
        "LOG_ANALYSIS": ["SIEM_ANALYSIS", "ENDPOINT_FORENSICS"],
        "SOC_TRIAGE": ["SOC_TRIAGE", "INCIDENT_RESPONSE"],
        "DETECTION_ENGINEERING": ["DETECTION_ENGINEERING"],
        "THREAT_INTELLIGENCE": ["THREAT_INTEL"],
        "IOC_ANALYSIS": ["THREAT_INTEL", "SIEM_ANALYSIS"],
        "THREAT_HUNTING": ["THREAT_HUNTING"],
        "ENDPOINT_SECURITY": ["ENDPOINT_FORENSICS"],
        "INCIDENT_RESPONSE": ["INCIDENT_RESPONSE"],
        "DIGITAL_FORENSICS": ["ENDPOINT_FORENSICS", "PCAP_ANALYSIS"],
        "MITRE_ATTACK": ["MITRE_ATTACK", "INCIDENT_RESPONSE"],
        "SOAR": ["SOAR_AUTOMATION"],
        "SECURITY_REASONING": ["INCIDENT_RESPONSE", "SOC_TRIAGE", "THREAT_HUNTING"],
    }

    @staticmethod
    def assess_all_skills(db: Session, user: User) -> list[dict[str, Any]]:
        """Assess all 28 skills for the given user, persisting/updating SkillAssessment rows."""
        skills = db.query(Skill).order_by(Skill.category, Skill.name).all()
        results = []

        for skill in skills:
            assessment = SkillAssessmentService.assess_single_skill(db, user, skill)
            results.append(assessment)

        return results

    @staticmethod
    def assess_single_skill(db: Session, user: User, skill: Skill) -> dict[str, Any]:
        """Calculates evidence, accuracy, recency weighting, and confidence for a specific skill."""
        now = datetime.now(timezone.utc)

        # 1. Mock Test Evidence
        test_attempts = (
            db.query(MockTestAttempt)
            .filter(
                MockTestAttempt.user_id == user.id,
                MockTestAttempt.status.in_([AttemptStatus.COMPLETED, AttemptStatus.SUBMITTED]),
            )
            .order_by(MockTestAttempt.submitted_at.desc())
            .limit(10)
            .all()
        )
        test_count = len(test_attempts)
        test_acc = (
            sum(t.percentage for t in test_attempts) / test_count if test_count > 0 else 0.0
        )

        # 2. Lab Evidence
        lab_attempts = (
            db.query(LabAttempt)
            .filter(LabAttempt.user_id == user.id)
            .order_by(LabAttempt.completed_at.desc())
            .limit(10)
            .all()
        )
        lab_count = len(lab_attempts)
        lab_acc = (
            sum(l.percentage for l in lab_attempts) / lab_count if lab_count > 0 else 0.0
        )

        # 3. Challenge Evidence
        relevant_cats = SkillAssessmentService.CATEGORY_MAP.get(skill.skill_code, [])
        chal_query = db.query(ChallengeAttempt).join(Challenge, Challenge.id == ChallengeAttempt.challenge_id)
        if relevant_cats:
            chal_query = chal_query.filter(Challenge.category.in_(relevant_cats))
        chal_attempts = (
            chal_query.filter(ChallengeAttempt.user_id == user.id)
            .order_by(ChallengeAttempt.created_at.desc())
            .limit(10)
            .all()
        )
        chal_count = len(chal_attempts)
        chal_solved = sum(1 for c in chal_attempts if c.solved)
        chal_acc = (chal_solved / chal_count * 100.0) if chal_count > 0 else 0.0

        # 4. SOC Scenario Evidence
        scenario_attempts = (
            db.query(ScenarioAttempt)
            .filter(ScenarioAttempt.user_id == user.id)
            .order_by(ScenarioAttempt.started_at.desc())
            .limit(5)
            .all()
        )
        scen_count = len(scenario_attempts)
        scen_acc = (
            sum(s.score for s in scenario_attempts) / scen_count if scen_count > 0 else 0.0
        )

        # Aggregate counts
        total_attempts = test_count + lab_count + chal_count + scen_count
        completed_activities = (
            sum(1 for t in test_attempts if t.percentage >= 60.0)
            + sum(1 for l in lab_attempts if l.percentage >= 60.0)
            + chal_solved
            + sum(1 for s in scenario_attempts if s.score >= 60.0)
        )
        practical_activities = lab_count + chal_count + scen_count

        # Recency Weighting: recent (50%) + historical (30%) + practical (20%)
        # Calculate recent evidence (last 3 attempts)
        recent_scores = []
        if test_attempts:
            recent_scores.extend([t.percentage for t in test_attempts[:2]])
        if lab_attempts:
            recent_scores.extend([l.percentage for l in lab_attempts[:2]])
        if chal_attempts:
            recent_scores.extend([100.0 if c.solved else 30.0 for c in chal_attempts[:2]])
        if scenario_attempts:
            recent_scores.extend([s.score for s in scenario_attempts[:2]])

        recent_performance = (
            sum(recent_scores) / len(recent_scores) if recent_scores else 0.0
        )
        historical_performance = (
            (test_acc * 0.4 + lab_acc * 0.3 + chal_acc * 0.3)
            if (test_count or lab_count or chal_count)
            else 0.0
        )
        practical_performance = (
            (lab_acc * 0.4 + chal_acc * 0.4 + scen_acc * 0.2)
            if practical_activities > 0
            else historical_performance
        )

        if total_attempts > 0:
            overall_accuracy = (
                0.5 * recent_performance
                + 0.3 * historical_performance
                + 0.2 * practical_performance
            )
            completion_rate = (completed_activities / total_attempts) * 100.0
        else:
            overall_accuracy = 0.0
            completion_rate = 0.0

        # Confidence Estimation
        if total_attempts == 0:
            confidence = SkillConfidence.NOT_ENOUGH_DATA
            confidence_reason = "No recorded activities yet for this skill area."
        elif total_attempts <= 2:
            confidence = SkillConfidence.LOW_CONFIDENCE
            confidence_reason = f"Low confidence based on {total_attempts} preliminary activity."
        elif total_attempts <= 5:
            confidence = SkillConfidence.MODERATE_CONFIDENCE
            confidence_reason = f"Moderate confidence based on {total_attempts} recent activities."
        else:
            confidence = SkillConfidence.HIGH_CONFIDENCE
            confidence_reason = f"High confidence based on {total_attempts} verified activities."

        evidence_breakdown = {
            "mock_tests": {
                "attempts": test_count,
                "accuracy": round(test_acc, 1),
            },
            "labs": {
                "attempts": lab_count,
                "accuracy": round(lab_acc, 1),
            },
            "challenges": {
                "attempts": chal_count,
                "solved": chal_solved,
                "accuracy": round(chal_acc, 1),
            },
            "soc_scenarios": {
                "attempts": scen_count,
                "accuracy": round(scen_acc, 1),
            },
        }

        # Educational Neutral Feedback Suggestion
        if overall_accuracy < 60.0 and total_attempts > 0:
            guidance = f"Recent results suggest additional practice with {skill.name.lower()} may be beneficial."
        elif overall_accuracy >= 80.0:
            guidance = f"Demonstrated solid competency across {skill.name.lower()} checkpoints."
        elif total_attempts > 0:
            guidance = f"Developing competency in {skill.name.lower()}; continued hands-on drills recommended."
        else:
            guidance = f"Begin exploring lessons and introductory labs in {skill.name.lower()}."

        # Persist or update database record
        persisted = (
            db.query(SkillAssessment)
            .filter(
                SkillAssessment.user_id == user.id,
                SkillAssessment.skill_id == skill.id,
            )
            .first()
        )
        if not persisted:
            persisted = SkillAssessment(
                user_id=user.id,
                skill_id=skill.id,
                exposure=len(skill.related_topics),
                attempts=total_attempts,
                completed_activities=completed_activities,
                accuracy=round(overall_accuracy, 1),
                completion_rate=round(completion_rate, 1),
                recent_performance=round(recent_performance, 1),
                practical_activity_count=practical_activities,
                confidence=confidence,
                last_activity_at=now if total_attempts > 0 else None,
                evidence_breakdown=evidence_breakdown,
            )
            db.add(persisted)
        else:
            persisted.exposure = len(skill.related_topics)
            persisted.attempts = total_attempts
            persisted.completed_activities = completed_activities
            persisted.accuracy = round(overall_accuracy, 1)
            persisted.completion_rate = round(completion_rate, 1)
            persisted.recent_performance = round(recent_performance, 1)
            persisted.practical_activity_count = practical_activities
            persisted.confidence = confidence
            persisted.evidence_breakdown = evidence_breakdown
            if total_attempts > 0:
                persisted.last_activity_at = now

        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()

        return {
            "skill_id": skill.id,
            "skill_code": skill.skill_code,
            "name": skill.name,
            "category": skill.category,
            "description": skill.description,
            "related_topics": skill.related_topics,
            "attempts": total_attempts,
            "completed_activities": completed_activities,
            "practical_activities": practical_activities,
            "accuracy": round(overall_accuracy, 1),
            "completion_rate": round(completion_rate, 1),
            "recent_performance": round(recent_performance, 1),
            "confidence": confidence.value if hasattr(confidence, "value") else str(confidence),
            "confidence_reason": confidence_reason,
            "evidence_breakdown": evidence_breakdown,
            "educational_guidance": guidance,
            "last_activity_at": persisted.last_activity_at.isoformat() if persisted.last_activity_at else None,
        }
