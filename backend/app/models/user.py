from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.analytics import (
        LearningActivity,
        Portfolio,
        SkillAssessment,
        StudentRecommendation,
        UserAchievement,
    )
    from app.models.mock_test import MockTestAttempt
    from app.models.progress import (
        LabAttempt,
        LessonBookmark,
        LessonProgress,
        TopicProgress,
    )


class User(TimeStampedModel):
    """User account entity for students, instructors, and administrators."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_level: Mapped[str] = mapped_column(
        String(32), default="Cadet Defend-I", nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20),
        default=UserRole.STUDENT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    attempts: Mapped[list["MockTestAttempt"]] = relationship(
        "MockTestAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    lesson_progress: Mapped[list["LessonProgress"]] = relationship(
        "LessonProgress", back_populates="user", cascade="all, delete-orphan"
    )
    bookmarks: Mapped[list["LessonBookmark"]] = relationship(
        "LessonBookmark", back_populates="user", cascade="all, delete-orphan"
    )
    lab_attempts: Mapped[list["LabAttempt"]] = relationship(
        "LabAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    topic_progress: Mapped[list["TopicProgress"]] = relationship(
        "TopicProgress", back_populates="user", cascade="all, delete-orphan"
    )
    portfolio: Mapped["Portfolio | None"] = relationship(
        "Portfolio", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )
    skill_assessments: Mapped[list["SkillAssessment"]] = relationship(
        "SkillAssessment", back_populates="user", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["StudentRecommendation"]] = relationship(
        "StudentRecommendation", back_populates="user", cascade="all, delete-orphan"
    )
    activities: Mapped[list["LearningActivity"]] = relationship(
        "LearningActivity", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' role='{self.role}'>"
