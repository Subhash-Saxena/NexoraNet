from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.curriculum import Course
from app.schemas.curriculum import CourseBrief, CourseDetail

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[CourseBrief])
@router.get("/", response_model=list[CourseBrief], include_in_schema=False)
def list_courses(db: DbSession) -> list[CourseBrief]:
    """Retrieve all published curriculum courses."""
    courses = (
        db.query(Course)
        .filter(Course.is_published.is_(True))
        .options(selectinload(Course.modules))
        .all()
    )

    results = []
    for c in courses:
        results.append(
            CourseBrief(
                id=c.id,
                title=c.title,
                slug=c.slug,
                description=c.description,
                level=c.level,
                estimated_hours=c.estimated_hours,
                modules_count=len(c.modules),
            )
        )
    return results


@router.get("/{course_id}", response_model=CourseDetail)
def get_course_detail(course_id: str, db: DbSession) -> Course:
    """Retrieve a single course and its modules/topics by ID or slug."""
    query = (
        db.query(Course)
        .options(selectinload(Course.modules))
        .filter(Course.is_published.is_(True))
    )

    if course_id.isdigit():
        course = query.filter(Course.id == int(course_id)).first()
    else:
        course = query.filter(Course.slug == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' was not found.",
        )
    return course
