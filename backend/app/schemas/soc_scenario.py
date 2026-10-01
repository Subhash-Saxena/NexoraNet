"""Pydantic schemas for Step 18 Advanced Educational SOC Scenarios.

Supports scenario catalog, 9-stage investigation workspace, progressive hints,
and transparent rubric scoring.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SocScenarioSummaryResponse(BaseModel):
    id: int
    scenario_id: str
    title: str
    description: str
    difficulty: str
    category: str
    estimated_duration_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SocScenarioDetailResponse(SocScenarioSummaryResponse):
    learning_objectives: str
    initial_signal_json: str
    available_evidence_json: str
    correlation_targets_json: str
    hypotheses_options_json: str
    mitre_techniques_json: str
    response_options_json: str
    scoring_rubric_json: str
    hints_json: str
    solution_explanation: str


class ScenarioAttemptResponse(BaseModel):
    id: int
    attempt_id: str
    scenario_id: int
    scenario_identifier: str = ""
    scenario_title: str = ""
    user_id: int | None
    status: str
    current_stage: str
    stage_data_json: str
    hints_used: int
    score: float
    score_breakdown_json: str | None
    started_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class StageUpdateRequest(BaseModel):
    stage_name: str
    data: dict[str, Any]
    advance_stage: bool = False


class ScenarioHintResponse(BaseModel):
    hint: str
    hints_used: int
    remaining: int
    penalty_applied: float = 0.0
    message: str | None = None


class ScenarioEvaluationResponse(BaseModel):
    attempt_id: str
    scenario_id: str
    scenario_title: str
    status: str
    score: float
    max_score: float = 100.0
    passed: bool
    breakdown: dict[str, float]
    feedback: list[str]
    solution_explanation: str
    completed_at: str | None


class ScenarioMetricsResponse(BaseModel):
    total_scenarios: int
    total_attempts: int
    completed_attempts: int
    avg_score: float
    user_completed: int
    difficulty_distribution: dict[str, int]
    category_distribution: dict[str, int]
