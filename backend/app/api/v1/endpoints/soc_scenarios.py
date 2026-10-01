"""Educational Advanced SOC Scenario API Endpoints.

Provides endpoints for Scenario Catalog browsing, 9-stage guided investigation
workspace, progressive hint system, and transparent rubric evaluation.
Strictly offline educational simulation.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.soc_scenario import (
    ScenarioAttemptResponse,
    ScenarioEvaluationResponse,
    ScenarioHintResponse,
    ScenarioMetricsResponse,
    SocScenarioDetailResponse,
    SocScenarioSummaryResponse,
    StageUpdateRequest,
)
from app.services.soc_scenarios.scenario_attempt_service import ScenarioAttemptService
from app.services.soc_scenarios.scenario_service import ScenarioService

router = APIRouter()


# ------------------------------------------------------------------------------
# 1. Scenario Catalog & Metrics
# ------------------------------------------------------------------------------
@router.get(
    "",
    response_model=list[SocScenarioSummaryResponse],
    summary="List available advanced SOC scenarios",
)
def list_scenarios(
    db: DbSession,
    difficulty: str | None = Query(None, description="BEGINNER, INTERMEDIATE, ADVANCED, EXPERT"),
    category: str | None = Query(None, description="Scenario domain category"),
    search: str | None = Query(None, description="Search by title, description, or ID"),
) -> Any:
    """Retrieve catalog of 28 educational SOC scenarios with optional filters."""
    return ScenarioService.list_scenarios(
        db=db,
        difficulty=difficulty,
        category=category,
        search=search,
    )


@router.get(
    "/metrics",
    response_model=ScenarioMetricsResponse,
    summary="Get scenario engagement and completion metrics",
)
def get_scenario_metrics(
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve overall scenario stats, completion distribution, and average scores."""
    user_id = current_user.id if current_user else None
    return ScenarioService.get_scenario_metrics(db=db, user_id=user_id)


@router.get(
    "/{scenario_id}",
    response_model=SocScenarioDetailResponse,
    summary="Get scenario briefing and investigation materials",
)
def get_scenario_detail(
    scenario_id: str,
    db: DbSession,
) -> Any:
    """Fetch complete scenario specification for the investigation room."""
    sc = ScenarioService.get_scenario(db=db, identifier=scenario_id)
    if not sc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{scenario_id}' not found.",
        )
    return sc


# ------------------------------------------------------------------------------
# 2. Interactive Investigation Sessions (9 Stages)
# ------------------------------------------------------------------------------
@router.post(
    "/{scenario_id}/start",
    response_model=ScenarioAttemptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start new attempt session for scenario",
)
def start_scenario_attempt(
    scenario_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Initialize an interactive 9-stage investigation session."""
    try:
        user_id = current_user.id if current_user else None
        att = ScenarioAttemptService.start_attempt(db=db, scenario_identifier=scenario_id, user_id=user_id)
        resp = ScenarioAttemptResponse.model_validate(att)
        if att.scenario:
            resp.scenario_identifier = att.scenario.scenario_id
            resp.scenario_title = att.scenario.title
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/attempts/{attempt_id}",
    response_model=ScenarioAttemptResponse,
    summary="Get scenario attempt session progress",
)
def get_attempt_status(
    attempt_id: str,
    db: DbSession,
) -> Any:
    """Retrieve current stage, selected artifacts, and scores for an active attempt."""
    att = ScenarioAttemptService.get_attempt(db=db, attempt_id=attempt_id)
    if not att:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attempt '{attempt_id}' not found.",
        )
    resp = ScenarioAttemptResponse.model_validate(att)
    if att.scenario:
        resp.scenario_identifier = att.scenario.scenario_id
        resp.scenario_title = att.scenario.title
    return resp


@router.post(
    "/attempts/{attempt_id}/stage",
    response_model=ScenarioAttemptResponse,
    summary="Update stage inputs and optionally advance to next stage",
)
def update_stage_inputs(
    attempt_id: str,
    payload: StageUpdateRequest,
    db: DbSession,
) -> Any:
    """Save learner choices for the active stage (evidence, correlations, hypothesis, MITRE)."""
    try:
        att = ScenarioAttemptService.update_stage_data(
            db=db,
            attempt_id=attempt_id,
            stage_name=payload.stage_name,
            stage_payload=payload.data,
            advance_stage=payload.advance_stage,
        )
        resp = ScenarioAttemptResponse.model_validate(att)
        if att.scenario:
            resp.scenario_identifier = att.scenario.scenario_id
            resp.scenario_title = att.scenario.title
        return resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/attempts/{attempt_id}/hint",
    response_model=ScenarioHintResponse,
    summary="Unlock progressive hint with penalty deduction",
)
def unlock_hint(
    attempt_id: str,
    db: DbSession,
) -> Any:
    """Request progressive hint with score penalty."""
    try:
        return ScenarioAttemptService.unlock_hint(db=db, attempt_id=attempt_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/attempts/{attempt_id}/submit",
    response_model=ScenarioEvaluationResponse,
    summary="Submit investigation attempt for grading and feedback",
)
def submit_attempt(
    attempt_id: str,
    db: DbSession,
) -> Any:
    """Finalize investigation session, grade against transparent rubric, and generate feedback."""
    try:
        return ScenarioAttemptService.submit_and_evaluate(db=db, attempt_id=attempt_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
