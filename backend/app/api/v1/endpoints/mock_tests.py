from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.mock_test import MockTest, TestBlueprint, TestBlueprintTopic
from app.schemas.mock_test import (
    AttemptHistoryItem,
    BlueprintValidationResponse,
    CatalogCategoryItem,
    CatalogDifficultyItem,
    CatalogFilterOptionsResponse,
    CatalogStatisticsResponse,
    CatalogTopicItem,
    CatalogTypeItem,
    GenerateTestFromBlueprintRequest,
    MockTestBrief,
    MockTestDetail,
    MockTestPreviewResponse,
    StartAttemptResponse,
    TestBlueprintResponse,
    TestBlueprintRuleBrief,
)
from app.services.mock_test_catalog_service import mock_test_catalog_service
from app.services.mock_test_service import mock_test_service
from app.services.test_attempt_service import test_attempt_service
from app.services.test_generation_service import test_generation_service

router = APIRouter()


@router.get("", response_model=list[MockTestBrief])
@router.get("/", response_model=list[MockTestBrief], include_in_schema=False)
def list_mock_tests(
    db: DbSession,
    current_user: CurrentUser,
    category: Annotated[
        str | None,
        Query(
            description="Filter by catalog category (all, recommended, beginner, intermediate, advanced, comprehensive, full_mocks)"
        ),
    ] = None,
    difficulty: Annotated[
        str | None,
        Query(
            description="Filter by difficulty (BEGINNER, INTERMEDIATE, ADVANCED, MIXED)"
        ),
    ] = None,
    test_type: Annotated[
        str | None,
        Query(
            description="Filter by test type (TOPIC, DIFFICULTY, MIXED, COMPREHENSIVE, PRACTICE, FULL_MOCK)"
        ),
    ] = None,
    topic: Annotated[
        str | None,
        Query(description="Filter by topic slug or topic title substring"),
    ] = None,
    duration_min: Annotated[
        int | None,
        Query(description="Minimum duration in minutes", ge=0),
    ] = None,
    duration_max: Annotated[
        int | None,
        Query(description="Maximum duration in minutes", ge=0),
    ] = None,
    status_filter: Annotated[
        str | None,
        Query(
            alias="status",
            description="Filter by publishing status (PUBLISHED, DRAFT)",
        ),
    ] = None,
    q: Annotated[
        str | None,
        Query(
            description="Search by keyword across title, description, code, or tags"
        ),
    ] = None,
) -> list[MockTestBrief]:
    """
    Query mock test catalog with multi-dimensional filtering, student progress,
    active attempt resumption, and readiness diagnostics.
    """
    return mock_test_catalog_service.list_catalog_tests(
        db=db,
        category=category,
        difficulty=difficulty,
        test_type=test_type,
        topic=topic,
        duration_min=duration_min,
        duration_max=duration_max,
        status=status_filter,
        q=q,
        user_id=current_user.id,
    )


@router.get("/categories", response_model=list[CatalogCategoryItem])
def list_catalog_categories(
    db: DbSession, current_user: CurrentUser
) -> list[CatalogCategoryItem]:
    """Retrieve all catalog categories with live test counts."""
    return mock_test_catalog_service.list_catalog_categories(
        db=db, user_id=current_user.id
    )


@router.get("/topics", response_model=list[CatalogTopicItem])
def list_catalog_topics(db: DbSession) -> list[CatalogTopicItem]:
    """Retrieve distinct topics represented in the mock test catalog with test counts."""
    return mock_test_catalog_service.list_catalog_topics(db)


@router.get("/difficulties", response_model=list[CatalogDifficultyItem])
def list_catalog_difficulties(db: DbSession) -> list[CatalogDifficultyItem]:
    """Retrieve distinct difficulty levels with test counts."""
    return mock_test_catalog_service.list_catalog_difficulties(db)


@router.get("/types", response_model=list[CatalogTypeItem])
def list_catalog_types(db: DbSession) -> list[CatalogTypeItem]:
    """Retrieve distinct assessment types with test counts."""
    return mock_test_catalog_service.list_catalog_types(db)


@router.get("/filter-options", response_model=CatalogFilterOptionsResponse)
def get_filter_options(
    db: DbSession, current_user: CurrentUser
) -> CatalogFilterOptionsResponse:
    """Retrieve aggregated filter options (categories, topics, difficulties, types, durations)."""
    return mock_test_catalog_service.get_filter_options(
        db=db, user_id=current_user.id
    )


@router.get("/statistics", response_model=CatalogStatisticsResponse)
def get_catalog_statistics(db: DbSession) -> CatalogStatisticsResponse:
    """Retrieve metrics across the complete mock test catalog."""
    return mock_test_catalog_service.get_catalog_statistics(db)


@router.get("/blueprints/list", response_model=list[TestBlueprintResponse])
def list_test_blueprints(db: DbSession) -> list[TestBlueprintResponse]:
    """List all exam blueprints with syllabus distribution rules."""
    blueprints = (
        db.query(TestBlueprint)
        .options(
            selectinload(TestBlueprint.topics).selectinload(
                TestBlueprintTopic.topic
            )
        )
        .order_by(TestBlueprint.id.asc())
        .all()
    )

    results: list[TestBlueprintResponse] = []
    for bp in blueprints:
        rules: list[TestBlueprintRuleBrief] = [
            TestBlueprintRuleBrief(
                id=r.id,
                topic_id=r.topic_id,
                topic_title=r.topic.title if r.topic else f"Topic #{r.topic_id}",
                difficulty=r.difficulty,
                question_count=r.question_count,
                question_type=r.question_type,
                cognitive_level=r.cognitive_level,
            )
            for r in bp.topics
        ]
        results.append(
            TestBlueprintResponse(
                id=bp.id,
                title=bp.title,
                slug=bp.slug,
                description=bp.description,
                total_questions=bp.total_questions,
                duration_minutes=bp.duration_minutes,
                difficulty=bp.difficulty,
                rules=rules,
            )
        )
    return results


@router.get(
    "/blueprints/{blueprint_id}/validate",
    response_model=BlueprintValidationResponse,
)
def validate_blueprint(
    blueprint_id: int,
    db: DbSession,
) -> BlueprintValidationResponse:
    """Check whether sufficient published questions exist in the question bank for this blueprint."""
    val = test_generation_service.validate_blueprint_availability(
        db, blueprint_id
    )
    return BlueprintValidationResponse(**val)


@router.post(
    "/blueprints/{blueprint_id}/generate",
    response_model=MockTestDetail,
    status_code=status.HTTP_201_CREATED,
)
def generate_mock_test_from_blueprint(
    blueprint_id: int,
    db: DbSession,
    payload: GenerateTestFromBlueprintRequest | None = None,
) -> MockTestDetail:
    """Generate and publish a dynamic mock examination following the specified syllabus blueprint."""
    custom_title = payload.custom_title if payload else None
    custom_slug = payload.custom_slug if payload else None
    random_seed = payload.random_seed if payload else None

    mock_test = test_generation_service.generate_mock_test_from_blueprint(
        db=db,
        blueprint_id=blueprint_id,
        custom_title=custom_title,
        custom_slug=custom_slug,
        random_seed=random_seed,
    )

    detail = mock_test_service.get_mock_test_detail(db, mock_test.id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve generated examination metadata.",
        )
    return detail


@router.get(
    "/{mock_test_id}/blueprint",
    response_model=TestBlueprintResponse,
)
def get_mock_test_blueprint(
    mock_test_id: str,
    db: DbSession,
) -> TestBlueprintResponse:
    """Retrieve syllabus blueprint specification associated with a mock test."""
    query = (
        db.query(MockTest)
        .options(
            selectinload(MockTest.blueprint)
            .selectinload(TestBlueprint.topics)
            .selectinload(TestBlueprintTopic.topic)
        )
    )
    if mock_test_id.isdigit():
        mt = query.filter(MockTest.id == int(mock_test_id)).first()
    else:
        mt = query.filter(MockTest.slug == mock_test_id).first()

    if not mt or not mt.blueprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint not found for mock test '{mock_test_id}'.",
        )

    bp = mt.blueprint
    rules = [
        TestBlueprintRuleBrief(
            id=r.id,
            topic_id=r.topic_id,
            topic_title=r.topic.title if r.topic else f"Topic #{r.topic_id}",
            difficulty=r.difficulty,
            question_count=r.question_count,
            question_type=r.question_type,
            cognitive_level=r.cognitive_level,
        )
        for r in bp.topics
    ]
    return TestBlueprintResponse(
        id=bp.id,
        title=bp.title,
        slug=bp.slug,
        description=bp.description,
        total_questions=bp.total_questions,
        duration_minutes=bp.duration_minutes,
        difficulty=bp.difficulty,
        rules=rules,
    )


@router.get(
    "/{mock_test_id}/preview",
    response_model=MockTestPreviewResponse,
)
def get_mock_test_preview(
    mock_test_id: str,
    db: DbSession,
) -> MockTestPreviewResponse:
    """
    Generate a safe syllabus preview showing learning objectives and topic breakdown
    WITHOUT leaking question text or answer options.
    """
    preview = mock_test_catalog_service.get_test_preview(db, mock_test_id)
    if not preview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mock test '{mock_test_id}' not found.",
        )
    return preview


@router.get(
    "/{mock_test_id}/attempt-history",
    response_model=list[AttemptHistoryItem],
)
def get_test_attempt_history(
    mock_test_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> list[AttemptHistoryItem]:
    """Retrieve chronological attempts completed by the current student for this specific examination."""
    return mock_test_catalog_service.get_attempt_history(
        db=db,
        test_id_or_slug=mock_test_id,
        user_id=current_user.id,
    )


@router.get("/{mock_test_id}", response_model=MockTestDetail)
def get_mock_test_detail(
    mock_test_id: str,
    db: DbSession,
    current_user: CurrentUser,
) -> MockTestDetail:
    """Retrieve comprehensive mock test metadata, instructions, and syllabus distribution."""
    detail = mock_test_service.get_mock_test_detail(
        db=db,
        test_id_or_slug=mock_test_id,
        user_id=current_user.id,
    )
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mock test '{mock_test_id}' was not found.",
        )
    return detail


@router.post("/{mock_test_id}/start", response_model=StartAttemptResponse)
def start_or_resume_test(
    mock_test_id: str,
    db: DbSession,
    current_user: CurrentUser,
    retake: Annotated[
        bool,
        Query(
            description="If true, start a fresh attempt even if a prior completed sitting exists"
        ),
    ] = False,
) -> StartAttemptResponse:
    """
    Launch or resume a mock examination sitting.
    Questions are served with zero-knowledge shielding (no correct answers or explanations).
    """
    return test_attempt_service.start_or_resume_attempt(
        user_id=current_user.id,
        test_id_or_slug=mock_test_id,
        retake=retake,
        db=db,
    )
