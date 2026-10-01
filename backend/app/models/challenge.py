"""SQLAlchemy models for Step 19 CTF / Challenge & Advanced Cybersecurity Training Engine.

Supports secure flags, multi-stage investigations, progressive hints,
safe synthetic evidence attachments, and tracks.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import (
    ChallengeAttemptStatus,
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeType,
)


class Challenge(TimeStampedModel):
    """Core synthetic educational cybersecurity CTF challenge entity."""

    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    challenge_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ChallengeCategory] = mapped_column(
        Enum(ChallengeCategory, native_enum=False, length=64),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[ChallengeDifficulty] = mapped_column(
        Enum(ChallengeDifficulty, native_enum=False, length=32),
        nullable=False,
        index=True,
    )
    challenge_type: Mapped[ChallengeType] = mapped_column(
        Enum(ChallengeType, native_enum=False, length=64),
        default=ChallengeType.FLAG_CHALLENGE,
        nullable=False,
    )
    points: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    scenario: Mapped[str] = mapped_column(Text, nullable=False)
    learning_objectives: Mapped[str] = mapped_column(
        Text, default="[]", nullable=False
    )
    prerequisites: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    environment_description: Mapped[str] = mapped_column(Text, nullable=False)
    tasks_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    skills_tested_json: Mapped[str] = mapped_column(
        Text, default="[]", nullable=False
    )
    related_lesson_slug: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    related_lab_slug: Mapped[str | None] = mapped_column(String(128), nullable=True)
    related_mitre_technique: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )

    # Flag verification security: salted hash, format preview, validation mechanics
    flag_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    flag_salt: Mapped[str] = mapped_column(String(64), nullable=False)
    flag_format: Mapped[str] = mapped_column(
        String(64), default="FLAG{...}", nullable=False
    )
    validation_type: Mapped[str] = mapped_column(
        String(32), default="EXACT", nullable=False
    )

    # Solution & Educational Review
    solution_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    common_mistakes: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_multi_stage: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    simulation_only: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Relationships
    stages: Mapped[list["ChallengeStage"]] = relationship(
        "ChallengeStage",
        back_populates="challenge",
        cascade="all, delete-orphan",
        order_by="ChallengeStage.stage_order",
    )
    hints: Mapped[list["ChallengeHint"]] = relationship(
        "ChallengeHint",
        back_populates="challenge",
        cascade="all, delete-orphan",
        order_by="ChallengeHint.hint_number",
    )
    evidence: Mapped[list["ChallengeEvidence"]] = relationship(
        "ChallengeEvidence",
        back_populates="challenge",
        cascade="all, delete-orphan",
        order_by="ChallengeEvidence.order_index",
    )
    attempts: Mapped[list["ChallengeAttempt"]] = relationship(
        "ChallengeAttempt",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )


class ChallengeStage(TimeStampedModel):
    """Progressive step within a multi-stage investigation challenge."""

    __tablename__ = "challenge_stages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tasks_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    flag_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    flag_salt: Mapped[str] = mapped_column(String(64), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    is_terminal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="stages")


class ChallengeHint(TimeStampedModel):
    """Progressive hint with transparent score penalties."""

    __tablename__ = "challenge_hints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hint_number: Mapped[int] = mapped_column(Integer, nullable=False)
    hint_text: Mapped[str] = mapped_column(Text, nullable=False)
    penalty_percent: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    penalty_points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Relationships
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="hints")


class ChallengeEvidence(TimeStampedModel):
    """Read-only synthetic forensic/telemetry artifact attached to a challenge."""

    __tablename__ = "challenge_evidence"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    content_json: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="evidence")


class ChallengeAttempt(TimeStampedModel):
    """State tracking for a student's challenge attempt and progress."""

    __tablename__ = "challenge_attempts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    attempt_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[ChallengeAttemptStatus] = mapped_column(
        Enum(ChallengeAttemptStatus, native_enum=False, length=32),
        default=ChallengeAttemptStatus.IN_PROGRESS,
        nullable=False,
    )
    current_stage_order: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    stage_progress_json: Mapped[str] = mapped_column(
        Text, default="{}", nullable=False
    )
    hints_unlocked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hints_penalty: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    solved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revealed_solution: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Relationships
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="attempts")
    submissions: Mapped[list["ChallengeSubmission"]] = relationship(
        "ChallengeSubmission",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class ChallengeSubmission(TimeStampedModel):
    """Log of student flag / answer submissions for audit and anti-enumeration."""

    __tablename__ = "challenge_submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("challenge_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    submitted_flag: Mapped[str] = mapped_column(String(255), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    points_awarded: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    feedback: Mapped[str] = mapped_column(String(255), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    attempt: Mapped["ChallengeAttempt"] = relationship(
        "ChallengeAttempt", back_populates="submissions"
    )


class ChallengeTrack(TimeStampedModel):
    """Structured challenge curriculum track (e.g. Network Defender, SOC Analyst)."""

    __tablename__ = "challenge_tracks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    track_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[str] = mapped_column(String(128), nullable=False)
    difficulty: Mapped[ChallengeDifficulty] = mapped_column(
        Enum(ChallengeDifficulty, native_enum=False, length=32),
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    badge_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    items: Mapped[list["ChallengeTrackItem"]] = relationship(
        "ChallengeTrackItem",
        back_populates="track",
        cascade="all, delete-orphan",
        order_by="ChallengeTrackItem.order_index",
    )


class ChallengeTrackItem(TimeStampedModel):
    """Junction mapping challenges in sequence to a specific track."""

    __tablename__ = "challenge_track_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    track_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenge_tracks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    challenge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    track: Mapped["ChallengeTrack"] = relationship("ChallengeTrack", back_populates="items")
    challenge: Mapped["Challenge"] = relationship("Challenge")
