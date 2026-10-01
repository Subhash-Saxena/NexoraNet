from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import DifficultyLevel, LabStatus, QuestionType

if TYPE_CHECKING:
    from app.models.curriculum import Topic
    from app.models.progress import LabAttempt, LabStepSubmission


class Lab(TimeStampedModel):
    """Hands-on technical lab exercise configuration."""

    __tablename__ = "labs"
    __table_args__ = (UniqueConstraint("topic_id", "slug", name="uq_lab_topic_slug"),)

    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
        index=True,
    )
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    objectives: Mapped[str | None] = mapped_column(Text, nullable=True)
    prerequisites: Mapped[str | None] = mapped_column(Text, nullable=True)
    environment_type: Mapped[str] = mapped_column(
        String(64), default="LOCAL_SYSTEM", nullable=False
    )
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LabStatus] = mapped_column(
        Enum(LabStatus, native_enum=False, length=20),
        default=LabStatus.PUBLISHED,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="labs")
    steps: Mapped[list["LabStep"]] = relationship(
        "LabStep",
        back_populates="lab",
        cascade="all, delete-orphan",
        order_by="LabStep.step_number",
    )
    questions: Mapped[list["LabQuestion"]] = relationship(
        "LabQuestion",
        back_populates="lab",
        cascade="all, delete-orphan",
        order_by="LabQuestion.order_index",
    )
    attempts: Mapped[list["LabAttempt"]] = relationship(
        "LabAttempt", back_populates="lab", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lab id={self.id} title='{self.title}'>"


class LabStep(TimeStampedModel):
    """Step-by-step procedural instruction in a hands-on lab."""

    __tablename__ = "lab_steps"
    __table_args__ = (
        UniqueConstraint("lab_id", "step_number", name="uq_lab_step_number"),
    )

    lab_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_observation: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_type: Mapped[str] = mapped_column(
        String(64), default="manual", nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    lab: Mapped["Lab"] = relationship("Lab", back_populates="steps")
    questions: Mapped[list["LabQuestion"]] = relationship(
        "LabQuestion",
        back_populates="step",
        cascade="all, delete-orphan",
        order_by="LabQuestion.order_index",
    )
    submissions: Mapped[list["LabStepSubmission"]] = relationship(
        "LabStepSubmission",
        back_populates="step",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LabStep id={self.id} lab_id={self.lab_id} step={self.step_number}>"


class LabQuestion(TimeStampedModel):
    """Verification checkpoint question within a lab."""

    __tablename__ = "lab_questions"

    lab_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lab_steps.id", ondelete="SET NULL"), nullable=True, index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, native_enum=False, length=30),
        default=QuestionType.SINGLE_CHOICE,
        nullable=False,
    )
    answer_data: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    lab: Mapped["Lab"] = relationship("Lab", back_populates="questions")
    step: Mapped["LabStep | None"] = relationship("LabStep", back_populates="questions")
    submissions: Mapped[list["LabStepSubmission"]] = relationship(
        "LabStepSubmission",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LabQuestion id={self.id} lab_id={self.lab_id}>"
