"""API Endpoints for Step 19 CTF Challenges & Advanced Training Engine.

Provides secure, rate-limited challenge solving workflows, zero-knowledge detail retrieval,
track progression, and adaptive recommendations.
"""

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.security import rate_limiter
from app.schemas.challenge import (
    ChallengeAttemptResponse,
    ChallengeDetailResponse,
    ChallengeMetricsResponse,
    ChallengeRecommendationResponse,
    ChallengeSummaryResponse,
    ChallengeTrackDetailResponse,
    ChallengeTrackSummaryResponse,
    FlagSubmissionRequest,
    FlagSubmissionResponse,
    HintUnlockRequest,
    HintUnlockResponse,
    NotesUpdateRequest,
    RevealSolutionRequest,
    RevealSolutionResponse,
)
from app.services.challenges.adaptive_challenge_service import (
    adaptive_challenge_service,
)
from app.services.challenges.attempt_service import attempt_service
from app.services.challenges.challenge_service import challenge_service

router = APIRouter()


# ------------------------------------------------------------------------------
# 1. Catalog, Metrics & Tracks (Defined before /{challenge_id} to avoid conflicts)
# ------------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[ChallengeSummaryResponse],
    summary="List challenges with optional filters and student completion status",
)
def list_challenges(
    db: DbSession,
    current_user: CurrentUser,
    category: Annotated[str | None, Query(description="Category filter")] = None,
    difficulty: Annotated[str | None, Query(description="Difficulty filter")] = None,
    search: Annotated[str | None, Query(description="Search keyword in title, id, or description")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> Any:
    """List educational challenges."""
    user_id = current_user.id if current_user else None
    return challenge_service.list_challenges(
        db=db,
        category=category,
        difficulty=difficulty,
        search=search,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/metrics",
    response_model=ChallengeMetricsResponse,
    summary="Get CTF platform metrics and personal completion stats",
)
def get_challenge_metrics(
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Retrieve platform KPI metrics and student solving progress."""
    user_id = current_user.id if current_user else None
    return challenge_service.get_challenge_metrics(db=db, user_id=user_id)


@router.get(
    "/tracks",
    response_model=list[ChallengeTrackSummaryResponse],
    summary="List all curriculum training tracks",
)
def list_tracks(
    db: DbSession,
) -> Any:
    """List 5 curated defensive training tracks."""
    return challenge_service.list_tracks(db=db)


@router.get(
    "/tracks/{track_id}",
    response_model=ChallengeTrackDetailResponse,
    summary="Get track detail with sequential challenges",
)
def get_track_detail(
    track_id: str,
    db: DbSession,
) -> Any:
    """Retrieve curriculum track details and sequence."""
    track = challenge_service.get_track_detail(db=db, track_id=track_id)
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track '{track_id}' not found.",
        )
    return track


@router.get(
    "/recommendations",
    response_model=list[ChallengeRecommendationResponse],
    summary="Get adaptive challenge recommendations and concept reviews",
)
def get_recommendations(
    db: DbSession,
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=10)] = 5,
) -> Any:
    """Retrieve personalized challenge and concept recommendations."""
    user_id = current_user.id if current_user else None
    return adaptive_challenge_service.get_recommendations(
        db=db,
        user_id=user_id,
        limit=limit,
    )


# ------------------------------------------------------------------------------
# 2. Challenge Details & Solving Attempt Workflows
# ------------------------------------------------------------------------------

@router.get(
    "/{challenge_id}",
    response_model=ChallengeDetailResponse,
    summary="Get full challenge detail and briefing (zero-knowledge flags)",
)
def get_challenge_detail(
    challenge_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Fetch challenge detail. Flag hashes and salts are strictly withheld."""
    user_id = current_user.id if current_user else None
    detail = challenge_service.get_challenge_detail(
        db=db,
        challenge_id_or_code=challenge_id,
        user_id=user_id,
    )
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{challenge_id}' not found.",
        )
    return detail


@router.post(
    "/{challenge_id}/start",
    response_model=ChallengeAttemptResponse,
    summary="Start or resume an attempt for a challenge",
)
def start_or_resume_attempt(
    challenge_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Start or resume a student attempt sandbox."""
    detail = challenge_service.get_challenge_detail(db=db, challenge_id_or_code=challenge_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Challenge '{challenge_id}' not found.",
        )
    user_id = current_user.id if current_user else None
    try:
        return attempt_service.start_or_resume_attempt(
            db=db,
            challenge_id=detail["id"],
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{challenge_id}/submit",
    response_model=FlagSubmissionResponse,
    summary="Submit flag for validation against current stage/challenge",
)
def submit_flag(
    challenge_id: str,
    payload: FlagSubmissionRequest,
    db: DbSession,
    current_user: CurrentUser,
    request: Request,
) -> Any:
    """Validate submitted flag using constant-time hash verification and rate limiting."""
    cfg = get_settings()
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, _, retry_after = rate_limiter.check(
        f"flag:{client_ip}:{payload.attempt_id}",
        max_requests=cfg.RATE_LIMIT_FLAG_PER_MINUTE,
        window_seconds=60,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for flag submissions. Please wait {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    user_id = current_user.id if current_user else None
    try:
        return attempt_service.submit_flag(
            db=db,
            attempt_id=payload.attempt_id,
            submitted_flag=payload.flag,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{challenge_id}/hint",
    response_model=HintUnlockResponse,
    summary="Unlock next progressive hint with score penalty deduction",
)
def unlock_hint(
    challenge_id: str,
    payload: HintUnlockRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Unlock next progressive hint."""
    user_id = current_user.id if current_user else None
    try:
        return attempt_service.unlock_hint(
            db=db,
            attempt_id=payload.attempt_id,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{challenge_id}/reveal",
    response_model=RevealSolutionResponse,
    summary="Reveal educational solution walkthrough (gives up attempt with 0 points)",
)
def reveal_solution(
    challenge_id: str,
    payload: RevealSolutionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Any:
    """Reveal complete solution explanation for review."""
    user_id = current_user.id if current_user else None
    try:
        return attempt_service.reveal_solution(
            db=db,
            attempt_id=payload.attempt_id,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{challenge_id}/notes",
    response_model=ChallengeAttemptResponse,
    summary="Autosave student private investigation notes",
)
def save_notes(
    challenge_id: str,
    payload: NotesUpdateRequest,
    db: DbSession,
) -> Any:
    """Autosave scratchpad investigation notes."""
    try:
        return attempt_service.save_notes(
            db=db,
            attempt_id=payload.attempt_id,
            notes_text=payload.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
