from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import (
    AdminAuditAction,
    AssessmentRecommendationType,
    ContentStatus,
    PortfolioVisibility,
    SkillConfidence,
    StudentActivityType,
)

if TYPE_CHECKING:
    from app.models.user import User


class Skill(TimeStampedModel):
    """Authoritative cybersecurity and networking skill taxonomy node."""

    __tablename__ = "skills"

    skill_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    related_topics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    assessments: Mapped[list["SkillAssessment"]] = relationship(
        "SkillAssessment", back_populates="skill", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Skill id={self.id} code='{self.skill_code}' name='{self.name}'>"


class SkillAssessment(TimeStampedModel):
    """Calculated student proficiency and confidence estimation for a specific skill."""

    __tablename__ = "skill_assessments"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill_assessment"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exposure: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_activities: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recent_performance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    practical_activity_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence: Mapped[SkillConfidence] = mapped_column(
        Enum(SkillConfidence, native_enum=False, length=32),
        default=SkillConfidence.NOT_ENOUGH_DATA,
        nullable=False,
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    evidence_breakdown: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="skill_assessments")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="assessments")

    def __repr__(self) -> str:
        return (
            f"<SkillAssessment user={self.user_id} skill={self.skill_id} "
            f"accuracy={self.accuracy:.1f}% confidence={self.confidence}>"
        )


class LearningActivity(TimeStampedModel):
    """Unified chronological record of student actions across all educational systems."""

    __tablename__ = "learning_activities"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    activity_type: Mapped[StudentActivityType] = mapped_column(
        Enum(StudentActivityType, native_enum=False, length=64),
        nullable=False,
        index=True,
    )
    reference_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    points_earned: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="activities")

    def __repr__(self) -> str:
        return (
            f"<LearningActivity user={self.user_id} type='{self.activity_type}' "
            f"ref='{self.reference_id}' occurred='{self.occurred_at}'>"
        )


class StudentRecommendation(TimeStampedModel):
    """Actionable study recommendation with neutral pedagogical justification."""

    __tablename__ = "student_recommendations"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recommendation_type: Mapped[AssessmentRecommendationType] = mapped_column(
        Enum(AssessmentRecommendationType, native_enum=False, length=64),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    target_url: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), default="MEDIUM", nullable=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="recommendations")

    def __repr__(self) -> str:
        return (
            f"<StudentRecommendation user={self.user_id} "
            f"type='{self.recommendation_type}' title='{self.title[:30]}'>"
        )


class Achievement(TimeStampedModel):
    """Documented milestone achievement badge definition."""

    __tablename__ = "achievements"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    badge_icon: Mapped[str] = mapped_column(String(64), nullable=False)
    criteria_description: Mapped[str] = mapped_column(Text, nullable=False)
    required_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Achievement id={self.id} code='{self.code}' title='{self.title}'>"


class UserAchievement(TimeStampedModel):
    """User achievement unlock state and progress count."""

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    progress_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unlocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_achievements")
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements"
    )

    def __repr__(self) -> str:
        return (
            f"<UserAchievement user={self.user_id} achievement={self.achievement_id} "
            f"unlocked={self.is_unlocked}>"
        )


class Portfolio(TimeStampedModel):
    """Student educational portfolio showcasing authentic verified work."""

    __tablename__ = "portfolios"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    public_slug: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    visibility: Mapped[PortfolioVisibility] = mapped_column(
        Enum(PortfolioVisibility, native_enum=False, length=32),
        default=PortfolioVisibility.PRIVATE,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    learning_focus: Mapped[str | None] = mapped_column(String(128), nullable=True)
    social_links: Mapped[dict[str, str]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    show_stats: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_skills: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_certifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    no_index: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="portfolio")
    projects: Mapped[list["PortfolioProject"]] = relationship(
        "PortfolioProject", back_populates="portfolio", cascade="all, delete-orphan"
    )
    items: Mapped[list["PortfolioItem"]] = relationship(
        "PortfolioItem", back_populates="portfolio", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Portfolio user={self.user_id} slug='{self.public_slug}' visibility={self.visibility}>"


class PortfolioProject(TimeStampedModel):
    """Custom project entry added by the student to their portfolio."""

    __tablename__ = "portfolio_projects"

    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    learning_outcome: Mapped[str] = mapped_column(Text, nullable=False)
    repository_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    demo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    completed_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="projects")

    def __repr__(self) -> str:
        return f"<PortfolioProject id={self.id} title='{self.title}'>"


class PortfolioItem(TimeStampedModel):
    """Verified platform work item linked to student portfolio."""

    __tablename__ = "portfolio_items"

    portfolio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_type: Mapped[str] = mapped_column(String(64), nullable=False)
    reference_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_demonstrated: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="items")

    def __repr__(self) -> str:
        return f"<PortfolioItem id={self.id} type='{self.item_type}' title='{self.title}'>"


class AssessmentReport(TimeStampedModel):
    """Archival student learning evaluation report snapshot."""

    __tablename__ = "assessment_reports"

    report_uuid: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    learning_period: Mapped[str] = mapped_column(String(128), nullable=False)
    summary_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    disclaimer: Mapped[str] = mapped_column(
        Text,
        default="This report summarizes activity within NexoraNet and is not a professional certification or employment assessment.",
        nullable=False,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<AssessmentReport uuid='{self.report_uuid}' user={self.user_id}>"


class EducationalCertificate(TimeStampedModel):
    """Internal non-accredited course or module completion credential."""

    __tablename__ = "educational_certificates"

    certificate_uuid: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_or_module_title: Mapped[str] = mapped_column(String(255), nullable=False)
    course_or_module_slug: Mapped[str] = mapped_column(String(128), nullable=False)
    student_name: Mapped[str] = mapped_column(String(128), nullable=False)
    verification_code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    disclaimer: Mapped[str] = mapped_column(
        Text,
        default="NexoraNet Learning Completion - This is an internal educational completion verification and not an accredited professional or government certification.",
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<EducationalCertificate code='{self.verification_code}' student='{self.student_name}'>"


class AdminAuditLog(TimeStampedModel):
    """Immutable ledger of administrative changes and interventions."""

    __tablename__ = "admin_audit_logs"

    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor_username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[AdminAuditAction] = mapped_column(
        Enum(AdminAuditAction, native_enum=False, length=64),
        nullable=False,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<AdminAuditLog actor='{self.actor_username}' action={self.action} target='{self.target_id}'>"


class ContentVersion(TimeStampedModel):
    """Publication lifecycle and revision history tracking for educational content."""

    __tablename__ = "content_versions"

    content_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus, native_enum=False, length=32),
        default=ContentStatus.PUBLISHED,
        nullable=False,
    )
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return f"<ContentVersion {self.content_type}:{self.content_id} v{self.version_number} status={self.status}>"
