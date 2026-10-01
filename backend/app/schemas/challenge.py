"""Pydantic schemas for Step 19 CTF Challenges & Advanced Training Engine.

Supports challenge catalog, zero-knowledge detail views, progressive hints,
safe flag submissions, attempt lifecycle, tracks, and performance metrics.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChallengeSummaryResponse(BaseModel):
    """Compact summary of a challenge for catalog listing."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    challenge_id: str
    title: str
    category: str
    difficulty: str
    challenge_type: str
    points: int
    estimated_minutes: int
    description: str
    is_multi_stage: bool
    flag_format: str
    status: str = "NOT_STARTED"
    created_at: datetime


class ChallengeStageResponse(BaseModel):
    """Multi-stage challenge progression task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    stage_order: int
    title: str
    description: str
    tasks_json: str
    points: int
    is_terminal: bool


class ChallengeHintResponse(BaseModel):
    """Progressive hint with penalty information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    hint_number: int
    penalty_percent: float
    penalty_points: float
    is_unlocked: bool
    hint_text: str | None = None


class ChallengeEvidenceResponse(BaseModel):
    """Synthetic evidence attachment for offline inspection."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    evidence_type: str
    title: str
    description: str
    order_index: int
    content_json: str


class ChallengeDetailResponse(BaseModel):
    """Full educational challenge detail (zero-knowledge: flags never exposed)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    challenge_id: str
    title: str
    category: str
    difficulty: str
    challenge_type: str
    points: int
    estimated_minutes: int
    description: str
    scenario: str
    learning_objectives: str
    prerequisites: str
    environment_description: str
    tasks_json: str
    skills_tested_json: str
    related_lesson_slug: str | None = None
    related_lab_slug: str | None = None
    related_mitre_technique: str | None = None
    flag_format: str
    is_multi_stage: bool
    simulation_only: bool = True
    stages: list[ChallengeStageResponse] = []
    hints: list[ChallengeHintResponse] = []
    evidence: list[ChallengeEvidenceResponse] = []
    solution_explanation: str | None = None
    common_mistakes: str | None = None
    is_solved: bool = False
    revealed_solution: bool = False
    active_attempt_id: str | None = None


class ChallengeAttemptResponse(BaseModel):
    """Active student attempt tracking state."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    attempt_id: str
    challenge_id: int
    user_id: int | None = None
    status: str
    current_stage_order: int
    stage_progress_json: str
    hints_unlocked: int
    hints_penalty: float
    attempts_count: int
    score: float
    max_score: float
    solved: bool
    revealed_solution: bool
    started_at: datetime
    completed_at: datetime | None = None
    last_activity_at: datetime
    notes: str = ""


class StartAttemptRequest(BaseModel):
    """Request to start or resume a challenge attempt."""

    challenge_id: int


class FlagSubmissionRequest(BaseModel):
    """Submitting a flag for verification."""

    attempt_id: str
    flag: str = Field(..., min_length=1, max_length=256)


class FlagSubmissionResponse(BaseModel):
    """Result of flag verification."""

    is_correct: bool
    solved: bool
    points_awarded: float
    current_score: float
    current_stage: int
    feedback: str
    attempts_used: int
    solution_explanation: str | None = None


class HintUnlockRequest(BaseModel):
    """Request to unlock the next progressive hint."""

    attempt_id: str


class HintUnlockResponse(BaseModel):
    """Unlocked hint content with penalty details."""

    message: str
    hint_number: int
    hint_text: str | None = None
    penalty_applied: float
    total_penalty: float
    remaining_hints: int


class RevealSolutionRequest(BaseModel):
    """Request to reveal solution walkthrough ("give up")."""

    attempt_id: str


class RevealSolutionResponse(BaseModel):
    """Revealed solution educational walkthrough."""

    revealed: bool
    score: float
    solution_explanation: str
    common_mistakes: str
    message: str


class NotesUpdateRequest(BaseModel):
    """Autosave student private notes."""

    attempt_id: str
    notes: str = Field(..., max_length=20000)


class ChallengeTrackSummaryResponse(BaseModel):
    """Track summary with challenge counts."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    track_id: str
    title: str
    description: str
    target_role: str
    difficulty: str
    badge_name: str
    challenges_count: int


class ChallengeTrackItemResponse(BaseModel):
    """Sequential challenge item within a track."""

    order_index: int
    is_required: bool
    challenge: dict[str, Any]


class ChallengeTrackDetailResponse(BaseModel):
    """Track detail with all sequential challenges."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    track_id: str
    title: str
    description: str
    target_role: str
    difficulty: str
    badge_name: str
    items: list[ChallengeTrackItemResponse] = []


class ChallengeMetricsResponse(BaseModel):
    """Platform KPI metrics and student solving progress."""

    total_challenges: int
    difficulty_distribution: dict[str, int]
    category_distribution: dict[str, int]
    user_solved: int
    user_in_progress: int
    total_points_earned: float
    completion_rate_percent: float


class ChallengeRecommendationResponse(BaseModel):
    """Personalized next action or concept review."""

    type: str
    title: str
    challenge_id: str
    category: str
    difficulty: str
    points: int
    reason: str
    action_url: str
    related_lesson_slug: str | None = None
    related_lab_slug: str | None = None
