from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.models.enums import DifficultyLevel
from app.schemas.common import ModuleStatusResponse
from app.schemas.learning import (
    BookmarkItem,
    LearningProgressResponse,
    LearningSearchResponse,
)
from app.services.learning_service import (
    get_learning_progress,
    get_user_bookmarks,
    search_learning_content,
)

router = APIRouter()


@router.get("", response_model=ModuleStatusResponse)
@router.get("/", response_model=ModuleStatusResponse, include_in_schema=False)
def get_learning_status() -> ModuleStatusResponse:
    """Return status and metadata for structured networking curriculum."""
    return ModuleStatusResponse(
        module="learning",
        status="planned",
        description="Structured computer networking and defensive cybersecurity curriculum with interactive roadmaps and lesson progress tracking.",
        planned_phase="Phase 2",
        capabilities=[
            "19 Structured curriculum modules spanning Beginner to Advanced",
            "126 Categorized domain topics with prerequisite mappings",
            "Interactive concept visualizers and diagram systems",
            "Student lesson completion and progress telemetry",
            "Full-text curriculum search and bookmark management",
        ],
    )


@router.get("/progress", response_model=LearningProgressResponse)
def get_student_learning_progress(
    db: DbSession, current_user: CurrentUser
) -> LearningProgressResponse:
    """Retrieve overall, tiered, and continue-learning telemetry for active student."""
    return get_learning_progress(db, current_user.id)


@router.get("/search", response_model=LearningSearchResponse)
def search_curriculum(
    db: DbSession,
    q: Annotated[
        str, Query(min_length=1, description="Search term for curriculum content")
    ],
    difficulty: Annotated[
        str | None, Query(description="Optional difficulty filter")
    ] = None,
    content_type: Annotated[
        str | None, Query(description="Filter by entity type (topic, lesson, module)")
    ] = None,
) -> LearningSearchResponse:
    """Search curriculum hierarchy across courses, modules, topics, and lessons."""
    parsed_diff = None
    if difficulty:
        try:
            parsed_diff = DifficultyLevel(difficulty.upper())
        except ValueError:
            parsed_diff = None

    results = search_learning_content(db, q, parsed_diff, content_type)
    return LearningSearchResponse(
        query=q,
        total_results=len(results),
        results=results,
    )


@router.get("/bookmarks", response_model=list[BookmarkItem])
def list_student_bookmarks(
    db: DbSession, current_user: CurrentUser
) -> list[BookmarkItem]:
    """Retrieve all bookmarked lessons for the active student."""
    return get_user_bookmarks(db, current_user.id)
