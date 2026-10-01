"""Pydantic schemas for NexoraNet Hands-on Networking Lab Engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AttemptStatus, DifficultyLevel, LabStatus


class LabQuestionBrief(BaseModel):
    """Sanitized student-facing lab question."""

    id: int
    step_id: int | None = None
    question_text: str
    question_type: str
    points: int
    order_index: int
    safe_input_config: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class LabStepSubmissionBrief(BaseModel):
    """Brief summary of a previous step submission."""

    id: int
    step_id: int
    submitted_answer: str
    is_correct: bool
    points_earned: float
    hint_used: bool
    feedback: str | None = None
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabStepDetail(BaseModel):
    """Full detail of a lab step with student shielding."""

    id: int
    step_number: int
    title: str
    description: str | None = None
    instructions: str
    hint: str | None = None
    expected_observation: str | None = None
    validation_type: str
    points: int
    is_required: bool
    safe_input_config: dict[str, Any] = Field(default_factory=dict)
    questions: list[LabQuestionBrief] = Field(default_factory=list)
    is_completed: bool = False
    points_earned: float = 0.0
    latest_submission: LabStepSubmissionBrief | None = None

    model_config = ConfigDict(from_attributes=True)


class LabBriefResponse(BaseModel):
    """Summary item for lab catalogs and recommendations."""

    id: int
    topic_id: int
    topic_title: str
    topic_slug: str
    title: str
    slug: str
    description: str | None = None
    difficulty: DifficultyLevel
    estimated_minutes: int
    environment_type: str
    status: LabStatus
    is_published: bool
    total_steps: int = 0
    total_points: int = 0
    user_status: str = "NOT_STARTED"
    latest_score_percentage: float | None = None

    model_config = ConfigDict(from_attributes=True)


class LabDetailResponse(BaseModel):
    """Comprehensive lab payload for execution workspace."""

    id: int
    topic_id: int
    topic_title: str
    topic_slug: str
    title: str
    slug: str
    description: str | None = None
    difficulty: DifficultyLevel
    estimated_minutes: int
    environment_type: str
    instructions: str | None = None
    objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    status: LabStatus
    is_published: bool
    total_steps: int
    total_points: int
    steps: list[LabStepDetail]
    active_attempt_id: int | None = None
    active_attempt_status: str | None = None
    active_attempt_score: float = 0.0
    active_attempt_percentage: float = 0.0
    active_attempt_time_taken: int | None = None
    attempt_number: int = 1

    model_config = ConfigDict(from_attributes=True)


class StepSubmitRequest(BaseModel):
    """Payload sent by student to evaluate a lab step."""

    submitted_answer: Any
    hint_used: bool = False


class StepSubmitResponse(BaseModel):
    """Evaluation feedback and updated attempt score."""

    step_id: int
    attempt_id: int
    is_correct: bool
    points_earned: float
    max_points: float
    feedback: str
    explanation: str | None = None
    attempt_score: float
    attempt_total_points: float
    attempt_percentage: float
    is_lab_completed: bool


class LabAttemptBrief(BaseModel):
    """Overview of student attempt for lab history listing."""

    id: int
    lab_id: int
    lab_title: str
    lab_slug: str
    lab_difficulty: str
    lab_environment: str
    attempt_number: int
    status: AttemptStatus
    score: float
    total_points: float
    percentage: float
    started_at: datetime
    completed_at: datetime | None = None
    time_taken_seconds: int | None = None

    model_config = ConfigDict(from_attributes=True)


class LabStepSubmissionDetail(BaseModel):
    """Step evaluation detail in attempt review."""

    step_id: int
    step_number: int
    step_title: str
    submitted_answer: str
    is_correct: bool
    points_earned: float
    max_points: float
    hint_used: bool
    feedback: str | None = None
    explanation: str | None = None
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LabAttemptDetail(BaseModel):
    """Full historical review of a completed or in-progress attempt."""

    id: int
    lab_id: int
    lab_title: str
    lab_slug: str
    lab_difficulty: str
    attempt_number: int
    status: AttemptStatus
    score: float
    total_points: float
    percentage: float
    started_at: datetime
    completed_at: datetime | None = None
    time_taken_seconds: int | None = None
    submissions: list[LabStepSubmissionDetail] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class LabTelemetryResponse(BaseModel):
    """Student aggregate progress metrics across hands-on labs."""

    total_labs: int
    completed_labs: int
    in_progress_labs: int
    average_score: float
    beginner_completed: int
    beginner_total: int
    intermediate_completed: int
    intermediate_total: int
    advanced_completed: int
    advanced_total: int
