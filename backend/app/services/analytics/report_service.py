"""Report Service - Generates archival assessment reports and educational completion certificates."""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.analytics import (
    AssessmentReport,
    EducationalCertificate,
)
from app.models.user import User
from app.services.analytics.recommendation_engine_service import (
    RecommendationEngineService,
)
from app.services.analytics.skill_assessment_service import SkillAssessmentService
from app.services.analytics.student_analytics_service import StudentAnalyticsService
from sqlalchemy.orm import Session


class ReportService:
    """Produces explainable student assessment reports and internal completion credentials."""

    REPORT_DISCLAIMER = (
        "This report summarizes activity within NexoraNet and is not a professional certification "
        "or employment assessment."
    )

    CERT_DISCLAIMER = (
        "NexoraNet Learning Completion — This is an internal educational completion verification "
        "and not an accredited professional or government certification."
    )

    @staticmethod
    def generate_assessment_report(db: Session, user: User) -> dict[str, Any]:
        """Generate a complete, explainable learning assessment report and persist as an archival record."""
        now = datetime.now(timezone.utc)
        report_uuid = f"rep-{uuid.uuid4().hex[:12]}"

        # Gather real telemetry
        overview = StudentAnalyticsService.get_overview(db, user)
        progress = StudentAnalyticsService.get_learning_progress(db, user)
        skills = SkillAssessmentService.assess_all_skills(db, user)
        recommendations = RecommendationEngineService.get_recommendations(db, user, limit=4)

        # Knowledge evidence summary
        knowledge_evidence = {
            "tests_attempted": overview["tests_attempted"],
            "tests_completed": overview["tests_completed"],
            "overall_curriculum_percentage": progress["overall_completion_percentage"],
            "lessons_finished": overview["lessons_completed"],
        }

        # Practical evidence summary
        practical_evidence = {
            "labs_completed": overview["labs_completed"],
            "challenges_solved": overview["challenges_solved"],
            "challenge_points": overview["total_challenge_points"],
            "soc_scenarios_completed": overview["soc_scenarios_completed"],
            "incidents_investigated": overview["incidents_investigated"],
            "pcap_investigations": overview["pcap_investigations_completed"],
            "siem_investigations": overview["siem_investigations_completed"],
            "endpoint_investigations": overview["endpoint_investigations_completed"],
        }

        # Top skills evidence
        active_skills = [s for s in skills if s["attempts"] > 0][:8]
        if not active_skills:
            active_skills = skills[:6]

        summary_data = {
            "student_name": user.display_name or user.username,
            "current_level": user.current_level,
            "total_learning_time_minutes": overview["total_learning_time_minutes"],
            "learning_period": f"Enrolled through {now.strftime('%B %d, %Y')}",
            "knowledge_evidence": knowledge_evidence,
            "practical_evidence": practical_evidence,
            "skills_overview": active_skills,
            "recommended_next_steps": recommendations,
        }

        report = AssessmentReport(
            report_uuid=report_uuid,
            user_id=user.id,
            title=f"Student Learning Assessment Report — {user.display_name or user.username}",
            learning_period=f"Through {now.strftime('%B %Y')}",
            summary_json=summary_data,
            disclaimer=ReportService.REPORT_DISCLAIMER,
            generated_at=now,
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "report_uuid": report.report_uuid,
            "title": report.title,
            "generated_at": report.generated_at.isoformat(),
            "disclaimer": report.disclaimer,
            "summary": summary_data,
        }

    @staticmethod
    def get_latest_assessment_report(db: Session, user: User) -> dict[str, Any]:
        """Retrieve most recent assessment report or generate one if none exists."""
        report = (
            db.query(AssessmentReport)
            .filter(AssessmentReport.user_id == user.id)
            .order_by(AssessmentReport.generated_at.desc())
            .first()
        )
        if not report:
            return ReportService.generate_assessment_report(db, user)

        return {
            "report_uuid": report.report_uuid,
            "title": report.title,
            "generated_at": report.generated_at.isoformat(),
            "disclaimer": report.disclaimer,
            "summary": report.summary_json,
        }

    @staticmethod
    def get_report_by_uuid(db: Session, user: User, report_uuid: str) -> dict[str, Any]:
        """Fetch specific report ensuring IDOR ownership verification."""
        report = (
            db.query(AssessmentReport)
            .filter(
                AssessmentReport.report_uuid == report_uuid,
                AssessmentReport.user_id == user.id,
            )
            .first()
        )
        if not report:
            raise ValueError("Assessment report not found or access unauthorized.")

        return {
            "report_uuid": report.report_uuid,
            "title": report.title,
            "generated_at": report.generated_at.isoformat(),
            "disclaimer": report.disclaimer,
            "summary": report.summary_json,
        }

    @staticmethod
    def issue_certificate_if_eligible(
        db: Session, user: User, course_or_module_title: str, course_or_module_slug: str
    ) -> EducationalCertificate:
        """Issue internal educational completion certificate."""
        existing = (
            db.query(EducationalCertificate)
            .filter(
                EducationalCertificate.user_id == user.id,
                EducationalCertificate.course_or_module_slug == course_or_module_slug,
            )
            .first()
        )
        if existing:
            return existing

        now = datetime.now(timezone.utc)
        cert_uuid = f"cert-{uuid.uuid4().hex[:12]}"
        code = f"NX-{uuid.uuid4().hex[:8].upper()}"

        cert = EducationalCertificate(
            certificate_uuid=cert_uuid,
            user_id=user.id,
            course_or_module_title=course_or_module_title,
            course_or_module_slug=course_or_module_slug,
            student_name=user.display_name or user.username,
            verification_code=code,
            issued_at=now,
            disclaimer=ReportService.CERT_DISCLAIMER,
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return cert

    @staticmethod
    def verify_certificate(db: Session, verification_code: str) -> dict[str, Any]:
        """Public read-only verification of internal learning completion certificates."""
        cert = (
            db.query(EducationalCertificate)
            .filter(EducationalCertificate.verification_code == verification_code)
            .first()
        )
        if not cert:
            raise ValueError("Certificate verification code not found or invalid.")

        return {
            "verification_code": cert.verification_code,
            "student_name": cert.student_name,
            "course_or_module_title": cert.course_or_module_title,
            "issued_at": cert.issued_at.strftime("%B %d, %Y"),
            "disclaimer": cert.disclaimer,
            "is_valid": True,
        }
