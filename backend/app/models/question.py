from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampedModel
from app.models.enums import (
    CognitiveLevel,
    DifficultyLevel,
    QuestionStatus,
    QuestionType,
)

if TYPE_CHECKING:
    from app.models.curriculum import Topic
    from app.models.mock_test import MockTestQuestion, StudentAnswer

# Many-to-many association between questions and tags
question_tag_association = Table(
    "question_tags_association",
    Base.metadata,
    Column(
        "question_id",
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("question_tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class QuestionTag(TimeStampedModel):
    """Categorization tags for cross-topic and exam blueprint filtering."""

    __tablename__ = "question_tags"

    name: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )

    # Relationships
    questions: Mapped[list["Question"]] = relationship(
        "Question", secondary=question_tag_association, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<QuestionTag id={self.id} name='{self.name}'>"


class Question(TimeStampedModel):
    __tablename__ = "questions"

    code: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, native_enum=False, length=30),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("topics.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    cognitive_level: Mapped[CognitiveLevel] = mapped_column(
        Enum(CognitiveLevel, native_enum=False, length=20),
        default=CognitiveLevel.UNDERSTAND,
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    learning_objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    estimated_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus, native_enum=False, length=20),
        default=QuestionStatus.PUBLISHED,
        nullable=False,
        index=True,
    )

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="questions")
    options: Mapped[list["QuestionOption"]] = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.order_index",
    )
    tags: Mapped[list["QuestionTag"]] = relationship(
        "QuestionTag", secondary=question_tag_association, back_populates="questions"
    )
    mock_test_links: Mapped[list["MockTestQuestion"]] = relationship(
        "MockTestQuestion", back_populates="question"
    )
    student_answers: Mapped[list["StudentAnswer"]] = relationship(
        "StudentAnswer", back_populates="question"
    )

    def __repr__(self) -> str:
        return (
            f"<Question id={self.id} type={self.question_type} diff={self.difficulty}>"
        )


class QuestionOption(TimeStampedModel):
    """Selectable answer choice for choice-based questions."""

    __tablename__ = "question_options"

    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship
    question: Mapped["Question"] = relationship("Question", back_populates="options")

    def __repr__(self) -> str:
        return f"<QuestionOption id={self.id} question_id={self.question_id} is_correct={self.is_correct}>"
