from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.mock_test import (
    AttemptHistoryItem,
    AttemptStatusResponse,
    MarkQuestionRequest,
    SaveAnswerRequest,
    SaveAnswerResponse,
    StartAttemptResponse,
    TestResultResponse,
    TestReviewResponse,
)
from app.services.test_attempt_service import test_attempt_service

router = APIRouter()


@router.get("/history", response_model=list[AttemptHistoryItem])
def list_student_attempt_history(
    db: DbSession,
    current_user: CurrentUser,
) -> list[AttemptHistoryItem]:
    """Retrieve full chronological exam attempt records for the current student."""
    return test_attempt_service.list_user_attempts(
        user_id=current_user.id,
        db=db,
    )


@router.get("/{attempt_id}/status", response_model=AttemptStatusResponse)
def get_attempt_status(
    attempt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> AttemptStatusResponse:
    """
    Authoritative server-side timer synchronization and auto-finalization check.
    Returns remaining seconds and expiration state.
    """
    return test_attempt_service.get_attempt_status(
        user_id=current_user.id,
        attempt_id=attempt_id,
        db=db,
    )


@router.post("/{attempt_id}/save-answer", response_model=SaveAnswerResponse)
def save_student_answer(
    attempt_id: int,
    payload: SaveAnswerRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> SaveAnswerResponse:
    """
    Idempotently record selected option(s) for a question.
    Validates exam sitting state, ownership, and option integrity.
    """
    return test_attempt_service.save_answer(
        user_id=current_user.id,
        attempt_id=attempt_id,
        question_id=payload.question_id,
        selected_option_ids=payload.selected_option_ids,
        is_marked_for_review=payload.is_marked_for_review,
        db=db,
    )


@router.post(
    "/{attempt_id}/clear-answer/{question_id}", response_model=SaveAnswerResponse
)
def clear_student_answer(
    attempt_id: int,
    question_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> SaveAnswerResponse:
    """Clear selected option choices for a specific question."""
    return test_attempt_service.clear_answer(
        user_id=current_user.id,
        attempt_id=attempt_id,
        question_id=question_id,
        db=db,
    )


@router.post(
    "/{attempt_id}/mark-question/{question_id}", response_model=SaveAnswerResponse
)
def mark_question_for_review(
    attempt_id: int,
    question_id: int,
    payload: MarkQuestionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> SaveAnswerResponse:
    """Toggle the 'Mark for Review' flag for a question in the sitting."""
    return test_attempt_service.mark_question(
        user_id=current_user.id,
        attempt_id=attempt_id,
        question_id=question_id,
        is_marked=payload.is_marked_for_review,
        db=db,
    )


@router.post("/{attempt_id}/submit", response_model=TestResultResponse)
def submit_exam_attempt(
    attempt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> TestResultResponse:
    """
    Authoritatively score and finalize an active exam sitting.
    Evaluates pass/fail against passing threshold and calculates topic breakdowns.
    """
    return test_attempt_service.submit_attempt(
        user_id=current_user.id,
        attempt_id=attempt_id,
        db=db,
    )


@router.get("/{attempt_id}/result", response_model=TestResultResponse)
def get_attempt_result(
    attempt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> TestResultResponse:
    """Retrieve scorecard and topic-level performance metrics for a completed or expired attempt."""
    return test_attempt_service.get_attempt_result(
        user_id=current_user.id,
        attempt_id=attempt_id,
        db=db,
    )


@router.get("/{attempt_id}/review", response_model=TestReviewResponse)
def get_attempt_review(
    attempt_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> TestReviewResponse:
    """
    Post-exam detailed answer review revealing correct options and comprehensive explanations.
    Strictly forbidden (403) while the attempt is still in progress.
    """
    return test_attempt_service.get_attempt_review(
        user_id=current_user.id,
        attempt_id=attempt_id,
        db=db,
    )


@router.post("/{attempt_id}/practice", response_model=StartAttemptResponse)
def create_practice_session(
    attempt_id: int,
    db: DbSession,
    current_user: CurrentUser,
    mode: Annotated[
        str,
        Query(
            description="Practice mode: 'incorrect_or_unanswered', 'incorrect', or 'unanswered'"
        ),
    ] = "incorrect_or_unanswered",
) -> StartAttemptResponse:
    """Generate a focused targeted practice test from the missed or skipped questions of this attempt."""
    return test_attempt_service.create_practice_session(
        user_id=current_user.id,
        prior_attempt_id=attempt_id,
        mode=mode,
        db=db,
    )
