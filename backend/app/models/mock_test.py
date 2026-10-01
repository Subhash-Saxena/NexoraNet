from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
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
    AttemptStatus,
    CognitiveLevel,
    DifficultyLevel,
    MockTestStatus,
    MockTestType,
    QuestionType,
)

if TYPE_CHECKING:
    from app.models.curriculum import Topic
    from app.models.question import Question
    from app.models.user import User


class MockTest(TimeStampedModel):
    """Timed mock examination containing pre-configured question sets."""

    __tablename__ = "mock_tests"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_type: Mapped[MockTestType] = mapped_column(
        Enum(MockTestType, native_enum=False, length=20),
        default=MockTestType.MIXED,
        nullable=False,
        index=True,
    )
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
        index=True,
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    passing_percentage: Mapped[float] = mapped_column(
        Float, default=70.0, nullable=False
    )
    status: Mapped[MockTestStatus] = mapped_column(
        Enum(MockTestStatus, native_enum=False, length=20),
        default=MockTestStatus.PUBLISHED,
        nullable=False,
        index=True,
    )
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    code: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )
    blueprint_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("test_blueprints.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    prerequisites: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    blueprint: Mapped["TestBlueprint | None"] = relationship(
        "TestBlueprint", backref="mock_tests"
    )
    test_questions: Mapped[list["MockTestQuestion"]] = relationship(
        "MockTestQuestion",
        back_populates="mock_test",
        cascade="all, delete-orphan",
        order_by="MockTestQuestion.order_index",
    )
    attempts: Mapped[list["MockTestAttempt"]] = relationship(
        "MockTestAttempt", back_populates="mock_test", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MockTest id={self.id} title='{self.title}'>"


class MockTestQuestion(TimeStampedModel):
    """Link entity mapping questions into specific mock tests with point values."""

    __tablename__ = "mock_test_questions"
    __table_args__ = (
        UniqueConstraint("mock_test_id", "question_id", name="uq_mock_test_question"),
    )

    mock_test_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    mock_test: Mapped["MockTest"] = relationship(
        "MockTest", back_populates="test_questions"
    )
    question: Mapped["Question"] = relationship(
        "Question", back_populates="mock_test_links"
    )

    def __repr__(self) -> str:
        return f"<MockTestQuestion test_id={self.mock_test_id} q_id={self.question_id}>"


class TestBlueprint(TimeStampedModel):
    """Specification matrix for dynamic and algorithmic exam generation."""

    __tablename__ = "test_blueprints"
    __test__ = False

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
    )

    # Relationships
    topics: Mapped[list["TestBlueprintTopic"]] = relationship(
        "TestBlueprintTopic",
        back_populates="blueprint",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<TestBlueprint id={self.id} title='{self.title}'>"


class TestBlueprintTopic(TimeStampedModel):
    """Topic distribution rule within a test blueprint."""

    __tablename__ = "test_blueprint_topics"
    __test__ = False

    blueprint_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_blueprints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    difficulty: Mapped[DifficultyLevel | None] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        nullable=True,
    )
    question_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    question_type: Mapped[QuestionType | None] = mapped_column(
        Enum(QuestionType, native_enum=False, length=30),
        nullable=True,
    )
    cognitive_level: Mapped[CognitiveLevel | None] = mapped_column(
        Enum(CognitiveLevel, native_enum=False, length=20),
        nullable=True,
    )

    # Relationships
    blueprint: Mapped["TestBlueprint"] = relationship(
        "TestBlueprint", back_populates="topics"
    )
    topic: Mapped["Topic"] = relationship("Topic", back_populates="blueprint_topics")

    def __repr__(self) -> str:
        return f"<TestBlueprintTopic bp_id={self.blueprint_id} topic_id={self.topic_id} count={self.question_count}>"


class MockTestAttempt(TimeStampedModel):
    """Student examination sitting session."""

    __tablename__ = "mock_test_attempts"

    mock_test_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus, native_enum=False, length=20),
        default=AttemptStatus.IN_PROGRESS,
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    mock_test: Mapped["MockTest"] = relationship("MockTest", back_populates="attempts")
    user: Mapped["User"] = relationship("User", back_populates="attempts")
    student_answers: Mapped[list["StudentAnswer"]] = relationship(
        "StudentAnswer", back_populates="attempt", cascade="all, delete-orphan"
    )
    result: Mapped["TestResult | None"] = relationship(
        "TestResult",
        back_populates="attempt",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<MockTestAttempt id={self.id} user_id={self.user_id} status={self.status}>"


class StudentAnswer(TimeStampedModel):
    """Individual question response recorded during an exam attempt."""

    __tablename__ = "student_answers"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id", "question_id", name="uq_attempt_question_answer"
        ),
    )

    attempt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_test_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    answer_data: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # JSON or selected option ID
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_marked_for_review: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    attempt: Mapped["MockTestAttempt"] = relationship(
        "MockTestAttempt", back_populates="student_answers"
    )
    question: Mapped["Question"] = relationship(
        "Question", back_populates="student_answers"
    )

    def __repr__(self) -> str:
        return f"<StudentAnswer attempt={self.attempt_id} q={self.question_id} correct={self.is_correct}>"


class TestResult(TimeStampedModel):
    """Comprehensive performance report generated upon exam submission."""

    __tablename__ = "test_results"
    __test__ = False

    attempt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_test_attempts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    correct_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    incorrect_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unanswered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_points: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    earned_points: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    passing_percentage: Mapped[float] = mapped_column(
        Float, default=70.0, nullable=False
    )
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationship
    attempt: Mapped["MockTestAttempt"] = relationship(
        "MockTestAttempt", back_populates="result"
    )

    def __repr__(self) -> str:
        return f"<TestResult attempt_id={self.attempt_id} score={self.score} pct={self.percentage}%>"
