from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import AttemptStatus, ProgressStatus

if TYPE_CHECKING:
    from app.models.curriculum import Lesson, Topic
    from app.models.lab import Lab, LabQuestion, LabStep
    from app.models.user import User


class LessonProgress(TimeStampedModel):
    """User completion status for individual lessons."""

    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus, native_enum=False, length=20),
        default=ProgressStatus.NOT_STARTED,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="lesson_progress")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress_records")

    def __repr__(self) -> str:
        return f"<LessonProgress user={self.user_id} lesson={self.lesson_id} status={self.status}>"


class LessonBookmark(TimeStampedModel):
    """User bookmarked lessons for quick access and revision."""

    __tablename__ = "lesson_bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_bookmark"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookmarks")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="bookmarks")

    def __repr__(self) -> str:
        return f"<LessonBookmark user={self.user_id} lesson={self.lesson_id}>"


class LabAttempt(TimeStampedModel):
    """Student run record inside a hands-on lab sandbox."""

    __tablename__ = "lab_attempts"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lab_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus, native_enum=False, length=20),
        default=AttemptStatus.IN_PROGRESS,
        nullable=False,
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_points: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="lab_attempts")
    lab: Mapped["Lab"] = relationship("Lab", back_populates="attempts")
    step_submissions: Mapped[list["LabStepSubmission"]] = relationship(
        "LabStepSubmission", back_populates="attempt", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<LabAttempt id={self.id} user={self.user_id} lab={self.lab_id} status={self.status} score={self.score}>"
        )


class LabStepSubmission(TimeStampedModel):
    """Student step validation submission and evaluation record."""

    __tablename__ = "lab_step_submissions"

    attempt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lab_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lab_steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("lab_questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    submitted_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    points_earned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    attempt: Mapped["LabAttempt"] = relationship(
        "LabAttempt", back_populates="step_submissions"
    )
    step: Mapped["LabStep"] = relationship("LabStep", back_populates="submissions")
    question: Mapped["LabQuestion | None"] = relationship(
        "LabQuestion", back_populates="submissions"
    )

    def __repr__(self) -> str:
        return (
            f"<LabStepSubmission attempt={self.attempt_id} step={self.step_id} correct={self.is_correct}>"
        )


class TopicProgress(TimeStampedModel):
    """Aggregated competency and completion score per topic for a student."""

    __tablename__ = "topic_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_user_topic_progress"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus, native_enum=False, length=20),
        default=ProgressStatus.NOT_STARTED,
        nullable=False,
    )
    completion_percentage: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="topic_progress")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="progress_records")

    def __repr__(self) -> str:
        return f"<TopicProgress user={self.user_id} topic={self.topic_id} mastery={self.mastery_score}%>"
