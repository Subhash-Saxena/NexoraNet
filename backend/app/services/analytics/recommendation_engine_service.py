"""Recommendation Engine Service - Actionable study suggestions with explainable educational rationale."""

from typing import Any

from app.models.analytics import Skill, SkillAssessment, StudentRecommendation
from app.models.challenge import ChallengeAttempt
from app.models.curriculum import Lesson
from app.models.enums import AssessmentRecommendationType
from app.models.progress import LessonProgress
from app.models.user import User
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


class RecommendationEngineService:
    """Generates neutral, pedagogical study guidance grounded in actual student telemetry."""

    @staticmethod
    def get_recommendations(db: Session, user: User, limit: int = 6) -> list[dict[str, Any]]:
        """Retrieve active recommendations, generating dynamic suggestions if needed."""
        existing = (
            db.query(StudentRecommendation)
            .filter(
                StudentRecommendation.user_id == user.id,
                StudentRecommendation.is_dismissed.is_(False),
            )
            .order_by(StudentRecommendation.created_at.desc())
            .limit(limit)
            .all()
        )

        if not existing:
            RecommendationEngineService._generate_recommendations_for_user(db, user)
            existing = (
                db.query(StudentRecommendation)
                .filter(
                    StudentRecommendation.user_id == user.id,
                    StudentRecommendation.is_dismissed.is_(False),
                )
                .order_by(StudentRecommendation.created_at.desc())
                .limit(limit)
                .all()
            )

        return [
            {
                "id": r.id,
                "recommendation_type": r.recommendation_type.value if hasattr(r.recommendation_type, "value") else str(r.recommendation_type),
                "title": r.title,
                "rationale": r.rationale,
                "target_url": r.target_url,
                "priority": r.priority,
                "is_dismissed": r.is_dismissed,
                "created_at": r.created_at.isoformat(),
            }
            for r in existing
        ]

    @staticmethod
    def dismiss_recommendation(db: Session, user: User, recommendation_id: int) -> bool:
        """Mark a recommendation as dismissed by the student."""
        rec = (
            db.query(StudentRecommendation)
            .filter(
                StudentRecommendation.id == recommendation_id,
                StudentRecommendation.user_id == user.id,
            )
            .first()
        )
        if not rec:
            return False
        rec.is_dismissed = True
        db.commit()
        return True

    @staticmethod
    def _generate_recommendations_for_user(db: Session, user: User) -> None:
        """Synthesize explainable recommendations from student skill and attempt telemetry."""
        # 1. Check for lowest performing skills with attempts
        low_skills = (
            db.query(SkillAssessment)
            .filter(
                SkillAssessment.user_id == user.id,
                SkillAssessment.attempts > 0,
                SkillAssessment.accuracy < 70.0,
            )
            .order_by(SkillAssessment.accuracy.asc())
            .limit(2)
            .all()
        )

        for sa in low_skills:
            skill = db.query(Skill).filter(Skill.id == sa.skill_id).first()
            if not skill:
                continue
            if skill.skill_code == "SUBNETTING":
                rec = StudentRecommendation(
                    user_id=user.id,
                    recommendation_type=AssessmentRecommendationType.PRACTICE_SUBNETTING,
                    title="Targeted IPv4 Subnetting Practice",
                    rationale="Recent results suggest additional practice with CIDR prefix masks and host boundary calculations may be beneficial.",
                    target_url="/labs/subnetting-vlsm-design",
                    priority="HIGH",
                )
                db.add(rec)
            elif skill.skill_code in ("PACKET_ANALYSIS", "TCP_IP"):
                rec = StudentRecommendation(
                    user_id=user.id,
                    recommendation_type=AssessmentRecommendationType.REVIEW_PACKET_ANALYSIS,
                    title="Deep Packet Inspection Walkthrough",
                    rationale=f"Review protocol handshakes and packet stream reassembly to reinforce {skill.name.lower()}.",
                    target_url="/packet-analysis",
                    priority="MEDIUM",
                )
                db.add(rec)
            else:
                rec = StudentRecommendation(
                    user_id=user.id,
                    recommendation_type=AssessmentRecommendationType.PRACTICE_LAB,
                    title=f"Practice Lab: {skill.name}",
                    rationale=f"Recent results indicate engaging with hands-on practice in {skill.name.lower()} will reinforce core principles.",
                    target_url="/labs",
                    priority="MEDIUM",
                )
                db.add(rec)

        # 2. Check for challenge opportunities
        solved_count = (
            db.query(ChallengeAttempt)
            .filter(ChallengeAttempt.user_id == user.id, ChallengeAttempt.solved.is_(True))
            .count()
        )
        if solved_count < 3:
            rec = StudentRecommendation(
                user_id=user.id,
                recommendation_type=AssessmentRecommendationType.ATTEMPT_CHALLENGE,
                title="Beginner Defensive CTF Challenge",
                rationale="Apply packet forensics and host triage skills in a safe, synthetic challenge environment.",
                target_url="/challenges",
                priority="MEDIUM",
            )
            db.add(rec)

        # 3. Check for incomplete lessons
        next_lesson = (
            db.query(Lesson)
            .outerjoin(
                LessonProgress,
                (LessonProgress.lesson_id == Lesson.id) & (LessonProgress.user_id == user.id),
            )
            .filter(LessonProgress.id.is_(None))
            .order_by(Lesson.order_index)
            .first()
        )
        if next_lesson:
            rec = StudentRecommendation(
                user_id=user.id,
                recommendation_type=AssessmentRecommendationType.REVIEW_LESSON,
                title=f"Curriculum Lesson: {next_lesson.title}",
                rationale=f"Continue your structured learning sequence by covering {next_lesson.title}.",
                target_url=f"/learning/lessons/{next_lesson.slug}",
                priority="LOW",
            )
            db.add(rec)

        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
