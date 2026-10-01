from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.enums import QuestionStatus
from app.models.question import Question
from app.schemas.question import (
    AdminQuestionCreate,
    AdminQuestionResponse,
    AdminQuestionUpdate,
    QuestionBankStatistics,
    StudentQuestionResponse,
)
from app.services.question_bank_service import QuestionBankService

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/statistics", response_model=QuestionBankStatistics)
def get_question_bank_statistics(db: DbSession) -> QuestionBankStatistics:
    """
    Retrieve comprehensive question bank statistics:
    total questions, breakdowns by difficulty, topic, question type,
    cognitive level, and publication status.
    """
    return QuestionBankService.get_statistics(db)


@router.get("", response_model=list[StudentQuestionResponse])
@router.get("/", response_model=list[StudentQuestionResponse], include_in_schema=False)
def list_questions(
    db: DbSession,
    topic_id: Annotated[int | None, Query(description="Filter by topic ID")] = None,
    difficulty: Annotated[
        str | None, Query(description="Filter by difficulty (case-insensitive)")
    ] = None,
    question_type: Annotated[
        str | None, Query(description="Filter by question format (case-insensitive)")
    ] = None,
    cognitive_level: Annotated[
        str | None, Query(description="Filter by cognitive level (REMEMBER, UNDERSTAND, APPLY, ANALYZE)")
    ] = None,
    tag: Annotated[
        str | None, Query(description="Filter by tag slug (e.g., 'tcp', 'subnetting')")
    ] = None,
    search: Annotated[
        str | None, Query(description="Search term in question text")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=500, description="Page limit")] = 100,
    offset: Annotated[int, Query(ge=0, description="Page offset")] = 0,
) -> list[Question]:
    """
    Retrieve questions for practice drills and assessments.
    CRITICAL SECURITY NOTICE: Student responses strictly omit answer keys and
    explanations to preserve exam integrity.
    """
    return QuestionBankService.search_questions(
        db=db,
        topic_id=topic_id,
        difficulty=difficulty,
        question_type=question_type,
        cognitive_level=cognitive_level,
        tag=tag,
        search_query=search,
        status=QuestionStatus.PUBLISHED,
        limit=limit,
        offset=offset,
    )


@router.get("/code/{code}", response_model=StudentQuestionResponse)
def get_question_by_code(code: str, db: DbSession) -> Question:
    """Retrieve an individual question by its stable identifier (e.g. 'NET-FUND-001')."""
    question = (
        db.query(Question)
        .options(
            selectinload(Question.options),
            selectinload(Question.tags),
        )
        .filter(Question.code == code, Question.status == QuestionStatus.PUBLISHED)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with code '{code}' was not found.",
        )
    return question


@router.get("/admin/list", response_model=list[AdminQuestionResponse], tags=["Admin"])
def list_admin_questions(
    db: DbSession,
    topic_id: Annotated[int | None, Query(description="Filter by topic ID")] = None,
    difficulty: Annotated[str | None, Query(description="Filter by difficulty")] = None,
    status_filter: Annotated[str | None, Query(description="Filter by QuestionStatus")] = None,
    search: Annotated[str | None, Query(description="Search text")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Question]:
    """Instructor/Author endpoint returning question details including answer keys."""
    parsed_status = None
    if status_filter:
        try:
            parsed_status = QuestionStatus(status_filter.upper())
        except ValueError:
            pass

    return QuestionBankService.search_questions(
        db=db,
        topic_id=topic_id,
        difficulty=difficulty,
        search_query=search,
        status=parsed_status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/admin/{question_id}", response_model=AdminQuestionResponse, tags=["Admin"]
)
def get_admin_question(question_id: int, db: DbSession) -> Question:
    """
    Instructor/Author endpoint returning full question details,
    including correctness attributes and authoritative rationale.
    """
    question = (
        db.query(Question)
        .options(
            selectinload(Question.options),
            selectinload(Question.tags),
        )
        .filter(Question.id == question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID '{question_id}' was not found.",
        )
    return question


@router.post("/admin/create", response_model=AdminQuestionResponse, tags=["Admin"], status_code=status.HTTP_201_CREATED)
def create_admin_question(payload: AdminQuestionCreate, db: DbSession) -> Question:
    """Author a new question with validation and option correctness."""
    try:
        return QuestionBankService.create_admin_question(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/admin/{question_id}", response_model=AdminQuestionResponse, tags=["Admin"])
def update_admin_question(question_id: int, payload: AdminQuestionUpdate, db: DbSession) -> Question:
    """Update an existing question and its options."""
    try:
        return QuestionBankService.update_admin_question(db, question_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/admin/{question_id}/publish", response_model=AdminQuestionResponse, tags=["Admin"])
@router.put("/admin/{question_id}/publish", response_model=AdminQuestionResponse, tags=["Admin"])
def publish_question(question_id: int, db: DbSession) -> Question:
    """Publish a draft or review question."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    q.status = QuestionStatus.PUBLISHED
    db.commit()
    db.refresh(q)
    return q


@router.post("/admin/{question_id}/archive", response_model=AdminQuestionResponse, tags=["Admin"])
@router.put("/admin/{question_id}/archive", response_model=AdminQuestionResponse, tags=["Admin"])
def archive_question(question_id: int, db: DbSession) -> Question:
    """Archive a question so it is no longer served to students."""
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    q.status = QuestionStatus.ARCHIVED
    db.commit()
    db.refresh(q)
    return q


@router.get("/{question_id}", response_model=StudentQuestionResponse)
def get_question(question_id: int, db: DbSession) -> Question:
    """Retrieve an individual question without answer key or internal explanations."""
    question = (
        db.query(Question)
        .options(
            selectinload(Question.options),
            selectinload(Question.tags),
        )
        .filter(Question.id == question_id, Question.status == QuestionStatus.PUBLISHED)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID '{question_id}' was not found.",
        )
    return question
