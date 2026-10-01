from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import ContentType, DifficultyLevel

if TYPE_CHECKING:
    from app.models.lab import Lab
    from app.models.mock_test import TestBlueprintTopic
    from app.models.progress import LessonBookmark, LessonProgress, TopicProgress
    from app.models.question import Question


class Course(TimeStampedModel):
    """Top-level learning curriculum track."""

    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
    )
    estimated_hours: Mapped[int] = mapped_column(Integer, default=40, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    modules: Mapped[list["Module"]] = relationship(
        "Module",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Module.order_index",
    )

    def __repr__(self) -> str:
        return f"<Course id={self.id} title='{self.title}'>"


class Module(TimeStampedModel):
    """Curriculum grouping within a course."""

    __tablename__ = "modules"
    __table_args__ = (
        UniqueConstraint("course_id", "slug", name="uq_module_course_slug"),
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="modules")
    topics: Mapped[list["Topic"]] = relationship(
        "Topic",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Topic.order_index",
    )

    def __repr__(self) -> str:
        return f"<Module id={self.id} title='{self.title}'>"


topic_prerequisites = Table(
    "topic_prerequisites",
    TimeStampedModel.metadata,
    Column(
        "topic_id",
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "prerequisite_id",
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Topic(TimeStampedModel):
    """Core domain concept entity reusable across lessons, questions, labs, and analytics."""

    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("module_id", "slug", name="uq_topic_module_slug"),
    )

    module_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
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
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    learning_objectives: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_relevance: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="topics")
    prerequisites: Mapped[list["Topic"]] = relationship(
        "Topic",
        secondary=topic_prerequisites,
        primaryjoin="Topic.id == topic_prerequisites.c.topic_id",
        secondaryjoin="Topic.id == topic_prerequisites.c.prerequisite_id",
        backref="unlocked_topics",
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="Lesson.order_index",
    )
    questions: Mapped[list["Question"]] = relationship(
        "Question", back_populates="topic"
    )
    labs: Mapped[list["Lab"]] = relationship("Lab", back_populates="topic")
    blueprint_topics: Mapped[list["TestBlueprintTopic"]] = relationship(
        "TestBlueprintTopic", back_populates="topic"
    )
    progress_records: Mapped[list["TopicProgress"]] = relationship(
        "TopicProgress", back_populates="topic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Topic id={self.id} title='{self.title}'>"


class Lesson(TimeStampedModel):
    """Atomic instructional unit within a topic."""

    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("topic_id", "slug", name="uq_lesson_topic_slug"),
    )

    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[ContentType] = mapped_column(
        Enum(ContentType, native_enum=False, length=20),
        default=ContentType.LESSON,
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False, length=20),
        default=DifficultyLevel.BEGINNER,
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="lessons")
    progress_records: Mapped[list["LessonProgress"]] = relationship(
        "LessonProgress", back_populates="lesson", cascade="all, delete-orphan"
    )
    bookmarks: Mapped[list["LessonBookmark"]] = relationship(
        "LessonBookmark", back_populates="lesson", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lesson id={self.id} title='{self.title}'>"
