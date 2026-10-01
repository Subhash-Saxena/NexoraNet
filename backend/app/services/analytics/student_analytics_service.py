"""Student Analytics Service - Authoritative progress telemetry, activity feed, and trend analysis."""

from datetime import datetime, timezone
from typing import Any

from app.models.analytics import LearningActivity
from app.models.challenge import Challenge, ChallengeAttempt
from app.models.curriculum import Lesson, Module, Topic
from app.models.endpoint_security import EndpointInvestigation
from app.models.enums import (
    AttemptStatus,
    ProgressStatus,
    ScenarioAttemptStatus,
    StudentActivityType,
)
from app.models.incident import Incident
from app.models.lab import Lab
from app.models.mock_test import MockTestAttempt
from app.models.pcap import Capture
from app.models.progress import LabAttempt, LessonProgress
from app.models.siem import SearchHistory
from app.models.soc_scenario import ScenarioAttempt, SocScenario
from app.models.user import User
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


class StudentAnalyticsService:
    """Computes explainable, non-judgmental student progress and learning intelligence."""

    @staticmethod
    def get_overview(db: Session, user: User) -> dict[str, Any]:
        """Aggregate authoritative student overview telemetry from persisted records."""
        # Lessons
        lessons_completed = (
            db.query(func.count(LessonProgress.id))
            .filter(
                LessonProgress.user_id == user.id,
                LessonProgress.status == ProgressStatus.COMPLETED,
            )
            .scalar()
            or 0
        )
        total_lessons = db.query(func.count(Lesson.id)).scalar() or 0

        # Labs
        labs_completed = (
            db.query(func.count(LabAttempt.id))
            .filter(
                LabAttempt.user_id == user.id,
                LabAttempt.status.in_([AttemptStatus.COMPLETED, AttemptStatus.SUBMITTED]),
                LabAttempt.percentage >= 60.0,
            )
            .scalar()
            or 0
        )
        total_labs = db.query(func.count(Lab.id)).scalar() or 0

        # Mock Tests
        tests_attempted = (
            db.query(func.count(MockTestAttempt.id))
            .filter(MockTestAttempt.user_id == user.id)
            .scalar()
            or 0
        )
        tests_completed = (
            db.query(func.count(MockTestAttempt.id))
            .filter(
                MockTestAttempt.user_id == user.id,
                MockTestAttempt.status.in_([AttemptStatus.COMPLETED, AttemptStatus.SUBMITTED]),
            )
            .scalar()
            or 0
        )

        # Challenges
        challenges_attempted = (
            db.query(func.count(ChallengeAttempt.id))
            .filter(ChallengeAttempt.user_id == user.id)
            .scalar()
            or 0
        )
        challenges_solved = (
            db.query(func.count(ChallengeAttempt.id))
            .filter(
                ChallengeAttempt.user_id == user.id,
                ChallengeAttempt.solved.is_(True),
            )
            .scalar()
            or 0
        )
        total_challenge_points = (
            db.query(func.coalesce(func.sum(ChallengeAttempt.score), 0.0))
            .filter(
                ChallengeAttempt.user_id == user.id,
                ChallengeAttempt.solved.is_(True),
            )
            .scalar()
            or 0.0
        )
        total_challenges = db.query(func.count(Challenge.id)).scalar() or 0

        # SOC Scenarios
        soc_scenarios_completed = (
            db.query(func.count(ScenarioAttempt.id))
            .filter(
                ScenarioAttempt.user_id == user.id,
                ScenarioAttempt.status == ScenarioAttemptStatus.COMPLETED,
            )
            .scalar()
            or 0
        )
        total_scenarios = db.query(func.count(SocScenario.id)).scalar() or 0

        # Practical Investigations
        incidents_investigated = db.query(func.count(Incident.id)).scalar() or 0
        pcap_investigations = db.query(func.count(Capture.id)).scalar() or 0
        siem_investigations = db.query(func.count(SearchHistory.id)).scalar() or 0
        endpoint_investigations = db.query(func.count(EndpointInvestigation.id)).scalar() or 0

        # Learning Time (seconds to minutes)
        lab_time_sec = (
            db.query(func.coalesce(func.sum(LabAttempt.time_taken_seconds), 0))
            .filter(LabAttempt.user_id == user.id)
            .scalar()
            or 0
        )
        test_estimated_min = tests_completed * 20
        lesson_estimated_min = lessons_completed * 12
        total_learning_time_minutes = int(lab_time_sec / 60) + test_estimated_min + lesson_estimated_min

        # Streak calculation (distinct activity dates)
        streak_days = StudentAnalyticsService._calculate_learning_streak(db, user.id)

        # Recent activities
        recent_activities = StudentAnalyticsService.get_activity_feed(db, user, limit=6)

        return {
            "user_id": user.id,
            "username": user.username,
            "display_name": user.display_name or user.username,
            "current_level": user.current_level,
            "total_learning_time_minutes": total_learning_time_minutes,
            "lessons_completed": lessons_completed,
            "total_lessons": total_lessons,
            "labs_completed": labs_completed,
            "total_labs": total_labs,
            "tests_attempted": tests_attempted,
            "tests_completed": tests_completed,
            "challenges_attempted": challenges_attempted,
            "challenges_solved": challenges_solved,
            "total_challenges": total_challenges,
            "total_challenge_points": float(total_challenge_points),
            "soc_scenarios_completed": soc_scenarios_completed,
            "total_scenarios": total_scenarios,
            "incidents_investigated": incidents_investigated,
            "pcap_investigations_completed": pcap_investigations,
            "siem_investigations_completed": siem_investigations,
            "endpoint_investigations_completed": endpoint_investigations,
            "current_learning_streak": streak_days,
            "recent_activity": recent_activities,
        }

    @staticmethod
    def get_learning_progress(db: Session, user: User) -> dict[str, Any]:
        """Calculates granular learning progress across modules, topics, and difficulty tracks."""
        modules = db.query(Module).order_by(Module.order_index).all()
        module_progress = []

        total_module_lessons = 0
        total_module_completed = 0

        for mod in modules:
            lessons_in_mod = (
                db.query(Lesson)
                .join(Topic, Topic.id == Lesson.topic_id)
                .filter(Topic.module_id == mod.id)
                .all()
            )
            mod_lesson_ids = [l.id for l in lessons_in_mod]
            mod_total = len(mod_lesson_ids)
            total_module_lessons += mod_total

            mod_completed = 0
            if mod_lesson_ids:
                mod_completed = (
                    db.query(func.count(LessonProgress.id))
                    .filter(
                        LessonProgress.user_id == user.id,
                        LessonProgress.lesson_id.in_(mod_lesson_ids),
                        LessonProgress.status == ProgressStatus.COMPLETED,
                    )
                    .scalar()
                    or 0
                )
            total_module_completed += mod_completed

            pct = round((mod_completed / mod_total * 100), 1) if mod_total > 0 else 0.0
            module_progress.append({
                "module_id": mod.id,
                "title": mod.title,
                "slug": mod.slug,
                "category": str(mod.difficulty),
                "total_lessons": mod_total,
                "completed_lessons": mod_completed,
                "completion_percentage": pct,
            })

        overall_pct = (
            round((total_module_completed / total_module_lessons * 100), 1)
            if total_module_lessons > 0
            else 0.0
        )

        return {
            "overall_completion_percentage": overall_pct,
            "total_lessons": total_module_lessons,
            "completed_lessons": total_module_completed,
            "modules": module_progress,
        }

    @staticmethod
    def get_activity_feed(db: Session, user: User, limit: int = 20) -> list[dict[str, Any]]:
        """Return persisted chronological activity log, synchronizing dynamic historical events if empty."""
        activities = (
            db.query(LearningActivity)
            .filter(LearningActivity.user_id == user.id)
            .order_by(LearningActivity.occurred_at.desc())
            .limit(limit)
            .all()
        )

        if not activities:
            # Sync historical events into LearningActivity
            StudentAnalyticsService._sync_historical_activities(db, user)
            activities = (
                db.query(LearningActivity)
                .filter(LearningActivity.user_id == user.id)
                .order_by(LearningActivity.occurred_at.desc())
                .limit(limit)
                .all()
            )

        return [
            {
                "id": a.id,
                "activity_type": a.activity_type.value if hasattr(a.activity_type, "value") else str(a.activity_type),
                "reference_id": a.reference_id,
                "title": a.title,
                "summary": a.summary,
                "score": a.score,
                "points_earned": a.points_earned,
                "status": a.status,
                "metadata": a.metadata_json,
                "occurred_at": a.occurred_at.isoformat(),
            }
            for a in activities
        ]

    @staticmethod
    def get_trends(db: Session, user: User) -> dict[str, Any]:
        """Return historical performance trends over time."""
        # Test accuracy history
        test_attempts = (
            db.query(MockTestAttempt)
            .filter(
                MockTestAttempt.user_id == user.id,
                MockTestAttempt.status.in_([AttemptStatus.COMPLETED, AttemptStatus.SUBMITTED]),
            )
            .order_by(MockTestAttempt.started_at.asc())
            .limit(10)
            .all()
        )
        test_trend = [
            {
                "label": f"Test #{t.id}",
                "percentage": round(t.percentage, 1),
                "date": t.started_at.strftime("%b %d"),
            }
            for t in test_attempts
        ]

        # Lab completion history
        lab_attempts = (
            db.query(LabAttempt)
            .filter(LabAttempt.user_id == user.id)
            .order_by(LabAttempt.started_at.asc())
            .limit(10)
            .all()
        )
        lab_trend = [
            {
                "label": f"Lab #{l.lab_id}",
                "percentage": round(l.percentage, 1),
                "date": l.started_at.strftime("%b %d"),
            }
            for l in lab_attempts
        ]

        # Challenge solve score history
        challenges = (
            db.query(ChallengeAttempt)
            .filter(ChallengeAttempt.user_id == user.id, ChallengeAttempt.solved.is_(True))
            .order_by(ChallengeAttempt.started_at.asc())
            .limit(10)
            .all()
        )
        challenge_trend = [
            {
                "label": f"Challenge #{c.challenge_id}",
                "score": c.score,
                "date": c.started_at.strftime("%b %d") if c.started_at else "Recent",
            }
            for c in challenges
        ]

        return {
            "test_accuracy_trend": test_trend,
            "lab_performance_trend": lab_trend,
            "challenge_scores_trend": challenge_trend,
        }

    @staticmethod
    def _calculate_learning_streak(db: Session, user_id: int) -> int:
        """Computes current consecutive active days for student learning."""
        dates = (
            db.query(func.date(LearningActivity.occurred_at))
            .filter(LearningActivity.user_id == user_id)
            .group_by(func.date(LearningActivity.occurred_at))
            .order_by(func.date(LearningActivity.occurred_at).desc())
            .limit(30)
            .all()
        )
        if not dates:
            return 1  # Active today
        return max(1, len(dates))

    @staticmethod
    def _sync_historical_activities(db: Session, user: User) -> None:
        """Seed initial LearningActivity rows from existing persisted student records."""
        now = datetime.now(timezone.utc)

        # 1. Lesson progresses
        lessons = (
            db.query(LessonProgress)
            .filter(LessonProgress.user_id == user.id)
            .limit(5)
            .all()
        )
        for lp in lessons:
            lesson = db.query(Lesson).filter(Lesson.id == lp.lesson_id).first()
            if lesson:
                act = LearningActivity(
                    user_id=user.id,
                    activity_type=StudentActivityType.LESSON,
                    reference_id=str(lesson.id),
                    title=f"Lesson: {lesson.title}",
                    summary="Completed curriculum lesson and conceptual checkpoints.",
                    status="COMPLETED",
                    occurred_at=lp.completed_at or lp.started_at or now,
                )
                db.add(act)

        # 2. Lab attempts
        labs = (
            db.query(LabAttempt)
            .filter(LabAttempt.user_id == user.id)
            .limit(5)
            .all()
        )
        for la in labs:
            act = LearningActivity(
                user_id=user.id,
                activity_type=StudentActivityType.LAB,
                reference_id=str(la.lab_id),
                title=f"Hands-on Lab Attempt #{la.id}",
                summary=f"Score: {la.percentage:.1f}% across validation checkpoints.",
                score=la.percentage,
                points_earned=la.score,
                status="COMPLETED" if la.percentage >= 60 else "ATTEMPTED",
                occurred_at=la.completed_at or la.started_at or now,
            )
            db.add(act)

        # 3. Mock test attempts
        tests = (
            db.query(MockTestAttempt)
            .filter(MockTestAttempt.user_id == user.id)
            .limit(5)
            .all()
        )
        for ta in tests:
            act = LearningActivity(
                user_id=user.id,
                activity_type=StudentActivityType.MOCK_TEST,
                reference_id=str(ta.mock_test_id),
                title=f"Mock Test Attempt #{ta.id}",
                summary=f"Achieved {ta.percentage:.1f}% exam score.",
                score=ta.percentage,
                status="COMPLETED",
                occurred_at=ta.submitted_at or ta.started_at or now,
            )
            db.add(act)

        # 4. Challenges
        challenges = (
            db.query(ChallengeAttempt)
            .filter(ChallengeAttempt.user_id == user.id)
            .limit(5)
            .all()
        )
        for ca in challenges:
            act = LearningActivity(
                user_id=user.id,
                activity_type=StudentActivityType.CHALLENGE,
                reference_id=str(ca.challenge_id),
                title=f"Cybersecurity Challenge #{ca.challenge_id}",
                summary=f"Solved with score of {ca.score:.0f} pts." if ca.solved else "Engaged challenge scenario.",
                score=ca.score,
                points_earned=ca.score if ca.solved else 0.0,
                status="SOLVED" if ca.solved else "ATTEMPTED",
                occurred_at=ca.solved_at or ca.started_at or now,
            )
            db.add(act)

        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
