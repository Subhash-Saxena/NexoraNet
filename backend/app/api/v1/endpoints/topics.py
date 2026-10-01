from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession, OptionalUser
from app.models.curriculum import Module, Topic
from app.models.enums import DifficultyLevel
from app.schemas.curriculum import TopicBrief
from app.schemas.learning import LessonBriefWithProgress, TopicDetailExtended
from app.services.learning_service import (
    get_topic_detail_extended,
)

router = APIRouter()


@router.get("", response_model=list[TopicBrief])
@router.get("/", response_model=list[TopicBrief], include_in_schema=False)
def list_topics(
    db: DbSession,
    module_id: Annotated[
        int | None, Query(description="Filter topics by parent module ID")
    ] = None,
    difficulty: Annotated[
        str | None, Query(description="Filter by difficulty level (case-insensitive)")
    ] = None,
) -> list[Topic]:
    """List topics across modules with optional filtering by parent module or difficulty."""
    query = (
        db.query(Topic)
        .options(selectinload(Topic.module))
        .filter(Topic.is_published.is_(True))
    )
    if module_id is not None:
        query = query.filter(Topic.module_id == module_id)
    if difficulty:
        try:
            diff_enum = DifficultyLevel(difficulty.upper())
            query = query.filter(Topic.difficulty == diff_enum)
        except ValueError:
            return []
    return query.order_by(Topic.order_index).all()


@router.get("/{topic_id}", response_model=TopicDetailExtended)
def get_topic_detail(
    topic_id: str, db: DbSession, current_user: OptionalUser = None
) -> TopicDetailExtended:
    """Retrieve full topic detail view with lesson outline and student progress indicators."""
    query = (
        db.query(Topic)
        .options(selectinload(Topic.module), selectinload(Topic.lessons))
        .filter(Topic.is_published.is_(True))
    )
    if topic_id.isdigit():
        topic = query.filter(Topic.id == int(topic_id)).first()
    else:
        topic = query.filter(Topic.slug == topic_id).first()

    # Fallback: check if topic_id is actually a module slug (e.g. from learning roadmap or path banner)
    if not topic:
        module = db.query(Module).filter(Module.slug == topic_id).first()
        if module:
            topic = (
                query.filter(Topic.module_id == module.id)
                .order_by(Topic.order_index)
                .first()
            )

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' was not found.",
        )

    user_id = current_user.id if current_user else None
    return get_topic_detail_extended(db, user_id, topic)


@router.get("/{topic_id}/lessons", response_model=list[LessonBriefWithProgress])
def get_topic_lessons(
    topic_id: str, db: DbSession, current_user: OptionalUser = None
) -> list[LessonBriefWithProgress]:
    """Retrieve lessons within a specific topic including student completion status."""
    query = db.query(Topic).filter(Topic.is_published.is_(True))
    if topic_id.isdigit():
        topic = query.filter(Topic.id == int(topic_id)).first()
    else:
        topic = query.filter(Topic.slug == topic_id).first()

    # Fallback: check if topic_id is actually a module slug
    if not topic:
        module = db.query(Module).filter(Module.slug == topic_id).first()
        if module:
            topic = (
                query.filter(Topic.module_id == module.id)
                .order_by(Topic.order_index)
                .first()
            )

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' was not found.",
        )

    user_id = current_user.id if current_user else None
    detail = get_topic_detail_extended(db, user_id, topic)
    return detail.lessons
