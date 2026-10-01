"""NexoraNet Hands-on Lab Endpoints.

Provides endpoints for listing, searching, starting, and inspecting
technical networking and defensive cybersecurity labs.
"""

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.models.enums import DifficultyLevel
from app.schemas.common import ModuleStatusResponse
from app.schemas.lab import (
    LabBriefResponse,
    LabDetailResponse,
    LabStepDetail,
    LabTelemetryResponse,
)
from app.services.lab_service import (
    get_lab_detail,
    get_lab_telemetry,
    list_labs,
    start_lab,
)

router = APIRouter()


@router.get("/status", response_model=ModuleStatusResponse)
def get_labs_module_status() -> ModuleStatusResponse:
    """Return status and architectural metadata for hands-on networking lab engine."""
    return ModuleStatusResponse(
        module_name="Hands-on Networking Labs",
        status="active",
        description="Isolated containerized environments for practicing practical networking skills safely.",
    )


@router.get("", response_model=list[LabBriefResponse])
@router.get("/", response_model=list[LabBriefResponse], include_in_schema=False)
def get_all_labs(
    db: DbSession,
    current_user: CurrentUser,
    difficulty: Annotated[
        str | None, Query(description="Filter by difficulty level (BEGINNER, INTERMEDIATE, ADVANCED)")
    ] = None,
    topic_id: Annotated[int | None, Query(description="Filter by curriculum topic id")] = None,
    environment: Annotated[
        str | None, Query(description="Filter by environment (e.g. PACKET_TRACER_EQUIVALENT, LINUX_TERMINAL)")
    ] = None,
    status: Annotated[
        str | None, Query(description="Filter by student attempt status (e.g. NOT_STARTED, IN_PROGRESS, COMPLETED)")
    ] = None,
    q: Annotated[
        str | None, Query(description="Search term in lab title or description")
    ] = None,
) -> list[LabBriefResponse]:
    """List all published hands-on labs with user attempt status and score summaries."""
    parsed_diff = None
    if difficulty:
        try:
            parsed_diff = DifficultyLevel(difficulty.upper())
        except ValueError:
            return []

    return list_labs(
        db=db,
        user_id=current_user.id,
        difficulty=parsed_diff,
        topic_id=topic_id,
        environment=environment,
        status_filter=status,
        q=q,
    )


@router.get("/telemetry", response_model=LabTelemetryResponse)
def get_student_lab_telemetry(db: DbSession, current_user: CurrentUser) -> LabTelemetryResponse:
    """Retrieve aggregate lab progress, average score, and tier metrics for the active student."""
    return get_lab_telemetry(db, current_user.id)


@router.get("/search", response_model=list[LabBriefResponse])
def search_labs(
    db: DbSession,
    current_user: CurrentUser,
    q: Annotated[str, Query(min_length=1, description="Search query string")],
    difficulty: Annotated[str | None, Query(description="Optional difficulty filter")] = None,
) -> list[LabBriefResponse]:
    """Search published labs by keyword."""
    parsed_diff = None
    if difficulty:
        try:
            parsed_diff = DifficultyLevel(difficulty.upper())
        except ValueError:
            pass

    return list_labs(db=db, user_id=current_user.id, difficulty=parsed_diff, q=q)


@router.get("/slug/{slug}", response_model=LabDetailResponse)
def get_lab_by_slug(slug: str, db: DbSession, current_user: CurrentUser) -> LabDetailResponse:
    """Retrieve full lab workspace data by unique slug identifier."""
    return get_lab_detail(db, current_user.id, slug)


@router.get("/{lab_id}", response_model=LabDetailResponse)
def get_lab_by_id_or_slug(lab_id: str, db: DbSession, current_user: CurrentUser) -> LabDetailResponse:
    """Retrieve full lab workspace data by numeric ID or slug."""
    return get_lab_detail(db, current_user.id, lab_id)


@router.get("/{lab_id}/steps", response_model=list[LabStepDetail])
def get_lab_steps(lab_id: str, db: DbSession, current_user: CurrentUser) -> list[LabStepDetail]:
    """Retrieve ordered steps for a lab with safe question inputs."""
    detail = get_lab_detail(db, current_user.id, lab_id)
    return detail.steps


@router.post("/{lab_id}/start", response_model=LabDetailResponse)
def start_lab_attempt(lab_id: str, db: DbSession, current_user: CurrentUser) -> LabDetailResponse:
    """Start or resume a student attempt for the target lab."""
    return start_lab(db, current_user.id, lab_id)
