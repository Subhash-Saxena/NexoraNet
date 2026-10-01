from fastapi import APIRouter

from app.schemas.common import ModuleStatusResponse

router = APIRouter()


@router.get("", response_model=ModuleStatusResponse)
@router.get("/", response_model=ModuleStatusResponse, include_in_schema=False)
async def get_progress_status() -> ModuleStatusResponse:
    """Return status and metadata for student progress tracking and analytics."""
    return ModuleStatusResponse(
        module="progress",
        status="planned",
        description="Student skill tracking, competency matrix, and personalized weak-topic recommendations.",
        planned_phase="Phase 2",
        capabilities=[
            "Multi-track mastery scoring (Networking, Security, Analysis, Defense)",
            "Weak-topic identification and revision recommendations",
            "Module completion telemetry",
            "Certification readiness assessment index",
        ],
    )
