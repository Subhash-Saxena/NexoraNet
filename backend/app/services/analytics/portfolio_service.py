"""Portfolio Service - Student cybersecurity showcase with strict privacy and security boundaries."""

import re
import uuid
from typing import Any
from urllib.parse import urlparse

from app.models.analytics import (
    EducationalCertificate,
    Portfolio,
    PortfolioProject,
    SkillAssessment,
)
from app.models.enums import PortfolioVisibility
from app.models.user import User
from sqlalchemy.orm import Session


class PortfolioService:
    """Manages student portfolios, custom projects, visibility tiers, and public exports."""

    SAFE_URL_PATTERN = re.compile(r"^https?://[a-zA-Z0-9\-\.]+(\.[a-zA-Z]{2,})?(/.*)?$")

    @staticmethod
    def validate_url(url: str | None) -> str | None:
        """Validate that URL uses http/https scheme and is safe from javascript/data injection."""
        if not url:
            return None
        cleaned = url.strip()
        parsed = urlparse(cleaned)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Project and social URLs must strictly use 'http' or 'https' protocol.")
        if not PortfolioService.SAFE_URL_PATTERN.match(cleaned):
            raise ValueError("Invalid URL format.")
        return cleaned

    @staticmethod
    def sanitize_text(text: str | None) -> str | None:
        """Simple HTML escaping for user-supplied portfolio text."""
        if not text:
            return text
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    @staticmethod
    def get_or_create_portfolio(db: Session, user: User) -> Portfolio:
        """Retrieve student portfolio, initializing with PRIVATE visibility if not present."""
        portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
        if not portfolio:
            random_slug = f"p-{uuid.uuid4().hex[:12]}"
            portfolio = Portfolio(
                user_id=user.id,
                public_slug=random_slug,
                visibility=PortfolioVisibility.PRIVATE,
                display_name=user.display_name or user.username,
                bio="Cybersecurity Cadet at NexoraNet. Specializing in network defense, packet analysis, and SOC operations.",
                learning_focus="Network Defense & Incident Response",
                social_links={},
                show_stats=True,
                show_skills=True,
                show_certifications=True,
                no_index=True,
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
        return portfolio

    @staticmethod
    def update_portfolio(db: Session, user: User, payload: dict[str, Any]) -> Portfolio:
        """Update portfolio profile, privacy controls, and visibility settings."""
        portfolio = PortfolioService.get_or_create_portfolio(db, user)

        if payload.get("display_name"):
            portfolio.display_name = PortfolioService.sanitize_text(payload["display_name"])[:128]
        if "bio" in payload:
            portfolio.bio = PortfolioService.sanitize_text(payload["bio"])
        if "learning_focus" in payload:
            portfolio.learning_focus = PortfolioService.sanitize_text(payload["learning_focus"])
        if "visibility" in payload:
            vis_val = payload["visibility"].upper()
            if vis_val in PortfolioVisibility.__members__:
                portfolio.visibility = PortfolioVisibility(vis_val)
        if "show_stats" in payload:
            portfolio.show_stats = bool(payload["show_stats"])
        if "show_skills" in payload:
            portfolio.show_skills = bool(payload["show_skills"])
        if "show_certifications" in payload:
            portfolio.show_certifications = bool(payload["show_certifications"])
        if "no_index" in payload:
            portfolio.no_index = bool(payload["no_index"])

        if "social_links" in payload and isinstance(payload["social_links"], dict):
            validated_links = {}
            for k, v in payload["social_links"].items():
                if v and isinstance(v, str):
                    clean_url = PortfolioService.validate_url(v)
                    if clean_url:
                        validated_links[k] = clean_url
            portfolio.social_links = validated_links

        db.commit()
        db.refresh(portfolio)
        return portfolio

    @staticmethod
    def add_project(db: Session, user: User, project_data: dict[str, Any]) -> PortfolioProject:
        """Add custom student project to portfolio with strict URL validation and text sanitization."""
        portfolio = PortfolioService.get_or_create_portfolio(db, user)

        repo_url = PortfolioService.validate_url(project_data.get("repository_url"))
        demo_url = PortfolioService.validate_url(project_data.get("demo_url"))

        project = PortfolioProject(
            portfolio_id=portfolio.id,
            title=PortfolioService.sanitize_text(project_data["title"])[:128],
            description=PortfolioService.sanitize_text(project_data["description"]),
            technologies=project_data.get("technologies", []),
            skills=project_data.get("skills", []),
            learning_outcome=PortfolioService.sanitize_text(project_data.get("learning_outcome", "")),
            repository_url=repo_url,
            demo_url=demo_url,
            completed_date=project_data.get("completed_date"),
            is_featured=bool(project_data.get("is_featured", True)),
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update_project(
        db: Session, user: User, project_id: int, project_data: dict[str, Any]
    ) -> PortfolioProject:
        """Update existing portfolio project with IDOR ownership verification."""
        portfolio = PortfolioService.get_or_create_portfolio(db, user)
        project = (
            db.query(PortfolioProject)
            .filter(
                PortfolioProject.id == project_id,
                PortfolioProject.portfolio_id == portfolio.id,
            )
            .first()
        )
        if not project:
            raise ValueError("Project not found or not owned by user.")

        if project_data.get("title"):
            project.title = PortfolioService.sanitize_text(project_data["title"])[:128]
        if project_data.get("description"):
            project.description = PortfolioService.sanitize_text(project_data["description"])
        if "learning_outcome" in project_data:
            project.learning_outcome = PortfolioService.sanitize_text(project_data["learning_outcome"])
        if "technologies" in project_data:
            project.technologies = project_data["technologies"]
        if "skills" in project_data:
            project.skills = project_data["skills"]
        if "repository_url" in project_data:
            project.repository_url = PortfolioService.validate_url(project_data["repository_url"])
        if "demo_url" in project_data:
            project.demo_url = PortfolioService.validate_url(project_data["demo_url"])
        if "completed_date" in project_data:
            project.completed_date = project_data["completed_date"]
        if "is_featured" in project_data:
            project.is_featured = bool(project_data["is_featured"])

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, user: User, project_id: int) -> bool:
        """Delete portfolio project with IDOR ownership check."""
        portfolio = PortfolioService.get_or_create_portfolio(db, user)
        project = (
            db.query(PortfolioProject)
            .filter(
                PortfolioProject.id == project_id,
                PortfolioProject.portfolio_id == portfolio.id,
            )
            .first()
        )
        if not project:
            return False
        db.delete(project)
        db.commit()
        return True

    @staticmethod
    def get_public_portfolio(db: Session, public_slug: str) -> dict[str, Any]:
        """
        Retrieve sanitized public portfolio view.
        Strictly strips email, internal IDs, flag answers, private notes, and internal metadata.
        Raises ValueError if portfolio is PRIVATE or not found.
        """
        portfolio = db.query(Portfolio).filter(Portfolio.public_slug == public_slug).first()
        if not portfolio:
            raise ValueError("Portfolio not found.")
        if portfolio.visibility == PortfolioVisibility.PRIVATE:
            raise ValueError("This portfolio is configured as private by the learner.")

        projects = (
            db.query(PortfolioProject)
            .filter(PortfolioProject.portfolio_id == portfolio.id)
            .order_by(PortfolioProject.is_featured.desc(), PortfolioProject.created_at.desc())
            .all()
        )

        # Verified platform skills (only if allowed)
        skills_showcase = []
        if portfolio.show_skills:
            assessments = (
                db.query(SkillAssessment)
                .filter(SkillAssessment.user_id == portfolio.user_id, SkillAssessment.attempts > 0)
                .all()
            )
            skills_showcase = [
                {
                    "skill_name": sa.skill.name if sa.skill else "Cybersecurity Practice",
                    "category": sa.skill.category if sa.skill else "GENERAL",
                    "accuracy": sa.accuracy,
                    "confidence": sa.confidence.value if hasattr(sa.confidence, "value") else str(sa.confidence),
                }
                for sa in assessments
            ]

        # Verified educational certificates (only if allowed)
        certificates_showcase = []
        if portfolio.show_certifications:
            certs = (
                db.query(EducationalCertificate)
                .filter(EducationalCertificate.user_id == portfolio.user_id)
                .all()
            )
            certificates_showcase = [
                {
                    "title": c.course_or_module_title,
                    "issued_at": c.issued_at.strftime("%B %Y"),
                    "verification_code": c.verification_code,
                    "disclaimer": c.disclaimer,
                }
                for c in certs
            ]

        return {
            "public_slug": portfolio.public_slug,
            "display_name": portfolio.display_name,
            "bio": portfolio.bio,
            "learning_focus": portfolio.learning_focus,
            "social_links": portfolio.social_links,
            "visibility": portfolio.visibility.value,
            "no_index": portfolio.no_index,
            "projects": [
                {
                    "title": p.title,
                    "description": p.description,
                    "technologies": p.technologies,
                    "skills": p.skills,
                    "learning_outcome": p.learning_outcome,
                    "repository_url": p.repository_url,
                    "demo_url": p.demo_url,
                    "completed_date": p.completed_date,
                    "is_featured": p.is_featured,
                }
                for p in projects
            ],
            "skills_evidence": skills_showcase,
            "certificates": certificates_showcase,
            "disclaimer": "This portfolio showcases verified educational simulation achievements completed on NexoraNet.",
        }

    @staticmethod
    def export_portfolio_json(db: Session, user: User) -> dict[str, Any]:
        """Export portfolio data as clean, portable structured JSON without internal secrets."""
        portfolio = PortfolioService.get_or_create_portfolio(db, user)
        public_data = PortfolioService.get_public_portfolio(db, portfolio.public_slug)
        return {
            "export_version": "1.0",
            "platform": "NexoraNet Cybersecurity Lab",
            "tagline": "Learn. Simulate. Analyze. Defend.",
            "learner_profile": {
                "display_name": portfolio.display_name,
                "learning_focus": portfolio.learning_focus,
                "bio": portfolio.bio,
                "social_links": portfolio.social_links,
            },
            "projects": public_data["projects"],
            "skills": public_data["skills_evidence"],
            "certificates": public_data["certificates"],
            "disclaimer": public_data["disclaimer"],
        }
