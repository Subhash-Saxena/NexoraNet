"""
Adaptive Practice Test Session API Endpoints.

Allows students to initiate dynamically compiled practice tests and track
authoritative session status while reusing the core Mock Test sitting mechanics.
"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.adaptive import StartAdaptiveTestRequest
from app.schemas.mock_test import AttemptStatusResponse, StartAttemptResponse
from app.services.adaptive_test_service import adaptive_test_service
from app.services.test_attempt_service import test_attempt_service

router = APIRouter()


@router.post("/start", response_model=StartAttemptResponse)
def start_adaptive_practice_test(
    payload: StartAdaptiveTestRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> StartAttemptResponse:
    """
    Dynamically compile and launch a personalized adaptive practice session.
    Calibrates topic quotas and question difficulties according to recent student metrics.
    """
    return adaptive_test_service.generate_and_start_adaptive_test(
        user_id=current_user.id,
        request=payload,
        db=db,
    )


@router.get("/{attempt_id}", response_model=StartAttemptResponse)
def get_adaptive_test_session(
    attempt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> StartAttemptResponse:
    """
    Retrieve sitting questions, order, and server timer for an active adaptive session.
    Zero-knowledge shielding guarantees correct answers and rationales are never exposed.
    """
    # Re-fetch sitting session via test_attempt_service
    from app.models.mock_test import MockTestAttempt

    attempt_obj = (
        db.query(MockTestAttempt)
        .filter(MockTestAttempt.id == attempt_id, MockTestAttempt.user_id == current_user.id)
        .first()
    )
    if not attempt_obj:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Adaptive attempt ID {attempt_id} was not found.",
        )

    return test_attempt_service.start_or_resume_attempt(
        user_id=current_user.id,
        test_id_or_slug=attempt_obj.mock_test_id,
        retake=False,
        db=db,
    )


@router.get("/{attempt_id}/status", response_model=AttemptStatusResponse)
def get_adaptive_test_status(
    attempt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> AttemptStatusResponse:
    """Synchronize server-authoritative timer and check expiration state."""
    return test_attempt_service.get_attempt_status(
        user_id=current_user.id,
        attempt_id=attempt_id,
        db=db,
    )
