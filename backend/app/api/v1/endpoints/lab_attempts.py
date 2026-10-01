"""NexoraNet Lab Attempt and Execution Endpoints.

Handles step submissions, answer evaluation, scoring, attempt finalization,
and historical review for hands-on networking labs.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.lab import (
    LabAttemptBrief,
    LabAttemptDetail,
    LabDetailResponse,
    StepSubmitRequest,
    StepSubmitResponse,
)
from app.services.lab_service import (
    get_attempt_detail,
    list_user_attempts,
    retry_lab,
    submit_lab_step,
)

router = APIRouter()


@router.get("", response_model=list[LabAttemptBrief])
@router.get("/", response_model=list[LabAttemptBrief], include_in_schema=False)
def get_user_lab_attempts(db: DbSession, current_user: CurrentUser) -> list[LabAttemptBrief]:
    """List historical lab attempts for the authenticated student."""
    return list_user_attempts(db, current_user.id)


@router.get("/{attempt_id}", response_model=LabAttemptDetail)
def get_lab_attempt_detail(
    attempt_id: int, db: DbSession, current_user: CurrentUser
) -> LabAttemptDetail:
    """Retrieve full review and evaluation breakdown for a specific attempt."""
    return get_attempt_detail(db, current_user.id, attempt_id)


@router.post("/{attempt_id}/steps/{step_id}/submit", response_model=StepSubmitResponse)
def submit_step_answer(
    attempt_id: int,
    step_id: int,
    payload: StepSubmitRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> StepSubmitResponse:
    """Validate student answer for a lab step, record submission idempotently,

    and update overall attempt progress.
    """
    return submit_lab_step(
        db=db,
        user_id=current_user.id,
        attempt_id=attempt_id,
        step_id=step_id,
        submitted_answer=payload.submitted_answer,
        hint_used=payload.hint_used,
    )


@router.post("/{attempt_id}/retry", response_model=LabDetailResponse)
def retry_lab_attempt(
    attempt_id: int, db: DbSession, current_user: CurrentUser
) -> LabDetailResponse:
    """Finalize current attempt and create a brand new attempt while preserving past performance records."""
    return retry_lab(db, current_user.id, attempt_id)
