from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.curriculum import Lesson, Topic
from app.schemas.curriculum import LessonBrief
from app.schemas.learning import LessonActionResponse, LessonDetailExtended
from app.services.learning_service import (
    get_lesson_detail_extended,
    get_next_and_previous_lesson,
    mark_lesson_completed,
    mark_lesson_started,
    toggle_lesson_bookmark,
)

router = APIRouter()


def _resolve_lesson(lesson_id: str, db: Session) -> Lesson:
    """Helper to query lesson by integer ID or string slug with relationship joins."""
    query = (
        db.query(Lesson)
        .options(selectinload(Lesson.topic).selectinload(Topic.module))
        .filter(Lesson.is_published.is_(True))
    )
    if lesson_id.isdigit():
        lesson = query.filter(Lesson.id == int(lesson_id)).first()
    else:
        lesson = query.filter(Lesson.slug == lesson_id).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson '{lesson_id}' was not found.",
        )
    return lesson


@router.get("/{lesson_id}", response_model=LessonDetailExtended)
def get_lesson_detail(
    lesson_id: str, db: DbSession, current_user: CurrentUser
) -> LessonDetailExtended:
    """Retrieve full lesson view with markdown content, breadcrumbs, and student progress."""
    lesson = _resolve_lesson(lesson_id, db)
    return get_lesson_detail_extended(db, current_user.id, lesson)


@router.get("/{lesson_id}/next", response_model=LessonBrief)
def get_next_lesson(lesson_id: str, db: DbSession) -> LessonBrief:
    """Retrieve the next logical sequential lesson in the curriculum."""
    lesson = _resolve_lesson(lesson_id, db)
    _, next_l = get_next_and_previous_lesson(db, lesson)
    if not next_l:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subsequent lesson found in this track.",
        )
    return next_l


@router.get("/{lesson_id}/previous", response_model=LessonBrief)
def get_previous_lesson(lesson_id: str, db: DbSession) -> LessonBrief:
    """Retrieve the previous sequential lesson in the curriculum."""
    lesson = _resolve_lesson(lesson_id, db)
    prev_l, _ = get_next_and_previous_lesson(db, lesson)
    if not prev_l:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No prior lesson found in this track.",
        )
    return prev_l


@router.post("/{lesson_id}/start", response_model=LessonActionResponse)
def start_lesson(
    lesson_id: str, db: DbSession, current_user: CurrentUser
) -> LessonActionResponse:
    """Mark a lesson as IN_PROGRESS and track access time."""
    lesson = _resolve_lesson(lesson_id, db)
    progress = mark_lesson_started(db, current_user.id, lesson.id)
    return LessonActionResponse(
        message="Lesson marked as in progress.",
        lesson_id=lesson.id,
        status=progress.status,
        updated_at=progress.last_accessed_at or datetime.now(timezone.utc),
    )


@router.post("/{lesson_id}/complete", response_model=LessonActionResponse)
def complete_lesson(
    lesson_id: str, db: DbSession, current_user: CurrentUser
) -> LessonActionResponse:
    """Mark a lesson as COMPLETED and update topic proficiency scores."""
    lesson = _resolve_lesson(lesson_id, db)
    progress = mark_lesson_completed(db, current_user.id, lesson.id)
    return LessonActionResponse(
        message="Lesson marked as completed.",
        lesson_id=lesson.id,
        status=progress.status,
        updated_at=progress.completed_at or datetime.now(timezone.utc),
    )


@router.post("/{lesson_id}/bookmark")
def bookmark_lesson(
    lesson_id: str, db: DbSession, current_user: CurrentUser
) -> dict[str, bool]:
    """Bookmark a lesson for user's quick revision list."""
    lesson = _resolve_lesson(lesson_id, db)
    is_bm = toggle_lesson_bookmark(db, current_user.id, lesson.id, bookmark=True)
    return {"is_bookmarked": is_bm}


@router.delete("/{lesson_id}/bookmark")
def unbookmark_lesson(
    lesson_id: str, db: DbSession, current_user: CurrentUser
) -> dict[str, bool]:
    """Remove a lesson from user's bookmarks list."""
    lesson = _resolve_lesson(lesson_id, db)
    is_bm = toggle_lesson_bookmark(db, current_user.id, lesson.id, bookmark=False)
    return {"is_bookmarked": is_bm}
