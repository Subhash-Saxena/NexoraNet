from typing import Any

from pydantic import BaseModel

from app.models.enums import (
    AttemptStatus,
    CognitiveLevel,
    DifficultyLevel,
    MockTestStatus,
    MockTestType,
    QuestionType,
)


class MockTestBrief(BaseModel):
    id: int
    code: str | None = None
    title: str
    slug: str
    description: str | None = None
    difficulty: DifficultyLevel
    test_type: MockTestType
    duration_minutes: int
    total_questions: int
    passing_percentage: float
    status: MockTestStatus
    prerequisites: str | None = None
    tags: list[str] = []
    topics_covered: list[str] = []
    is_ready: bool = True
    shortfall: int = 0
    latest_attempt_score: float | None = None
    latest_attempt_status: str | None = None
    active_attempt_id: int | None = None
    attempt_count: int = 0

    model_config = {"from_attributes": True}


class StudentOptionBrief(BaseModel):
    id: int
    option_text: str
    order_index: int

    model_config = {"from_attributes": True}


class StudentQuestionPayload(BaseModel):
    id: int
    question_number: int
    question_text: str
    question_type: QuestionType
    points: int
    topic_title: str
    difficulty: DifficultyLevel
    options: list[StudentOptionBrief] = []

    model_config = {"from_attributes": True}


class MockTestDetail(MockTestBrief):
    instructions: str | None = None
    what_you_will_practice: list[str] = []
    blueprint_id: int | None = None
    topics_breakdown: list[dict[str, Any]] = []
    questions: list[StudentQuestionPayload] = []


class StudentAnswerBrief(BaseModel):
    question_id: int
    selected_option_ids: list[int]
    is_marked_for_review: bool
    answered_at: str


class StartAttemptResponse(BaseModel):
    attempt_id: int
    test_id: int
    test_title: str
    test_slug: str
    duration_minutes: int
    passing_percentage: float
    started_at: str
    expires_at: str
    remaining_seconds: int
    status: AttemptStatus
    questions: list[StudentQuestionPayload]
    saved_answers: list[StudentAnswerBrief]


class SaveAnswerRequest(BaseModel):
    question_id: int
    selected_option_ids: list[int] = []
    is_marked_for_review: bool | None = None


class SaveAnswerResponse(BaseModel):
    success: bool
    question_id: int
    selected_option_ids: list[int]
    is_marked_for_review: bool
    message: str


class MarkQuestionRequest(BaseModel):
    is_marked_for_review: bool


class AttemptStatusResponse(BaseModel):
    attempt_id: int
    status: AttemptStatus
    started_at: str
    expires_at: str
    remaining_seconds: int
    is_expired: bool
    answered_count: int
    marked_count: int
    total_questions: int


class TopicPerformanceResponse(BaseModel):
    topic_id: int
    topic_title: str
    total_questions: int
    correct_questions: int
    points_earned: float
    total_points: float
    percentage: float


class DifficultyPerformanceResponse(BaseModel):
    difficulty: str
    total_questions: int
    correct_questions: int
    percentage: float


class TestResultResponse(BaseModel):
    __test__ = False
    attempt_id: int
    test_id: int
    test_title: str
    test_slug: str
    status: AttemptStatus
    score: float
    percentage: float
    total_points: float
    earned_points: float
    passing_percentage: float
    passed: bool
    total_questions: int
    attempted_questions: int
    unanswered_questions: int
    correct_answers: int
    incorrect_answers: int
    time_taken_seconds: int
    started_at: str
    submitted_at: str | None = None
    topic_breakdown: list[TopicPerformanceResponse] = []
    difficulty_breakdown: list[DifficultyPerformanceResponse] = []


class ReviewOptionItem(BaseModel):
    id: int
    option_text: str
    is_correct: bool


class QuestionReviewItem(BaseModel):
    question_id: int
    question_number: int
    question_text: str
    question_type: QuestionType
    points: int
    topic_title: str
    difficulty: DifficultyLevel
    options: list[ReviewOptionItem] = []
    selected_option_ids: list[int] = []
    is_correct: bool
    points_earned: int
    is_marked_for_review: bool
    explanation: str


class TestReviewResponse(BaseModel):
    __test__ = False
    attempt_id: int
    test_id: int
    test_title: str
    test_slug: str
    status: AttemptStatus
    result: TestResultResponse
    questions: list[QuestionReviewItem]


class AttemptHistoryItem(BaseModel):
    attempt_id: int
    test_id: int
    test_title: str
    test_slug: str
    difficulty: DifficultyLevel
    test_type: MockTestType
    status: AttemptStatus
    score: float
    total_points: float
    percentage: float
    passed: bool
    started_at: str
    submitted_at: str | None = None
    time_taken_seconds: int


class TestBlueprintRuleBrief(BaseModel):
    __test__ = False
    id: int
    topic_id: int
    topic_title: str | None = None
    difficulty: DifficultyLevel | None = None
    question_count: int
    question_type: QuestionType | None = None
    cognitive_level: CognitiveLevel | None = None

    model_config = {"from_attributes": True}


class TestBlueprintResponse(BaseModel):
    __test__ = False
    id: int
    title: str
    slug: str
    description: str | None = None
    total_questions: int
    duration_minutes: int
    difficulty: DifficultyLevel
    rules: list[TestBlueprintRuleBrief] = []

    model_config = {"from_attributes": True}


class BlueprintValidationRule(BaseModel):
    rule_id: int
    topic_id: int
    topic_title: str
    difficulty: str | None = None
    required_count: int
    available_count: int
    shortfall: int
    is_met: bool


class BlueprintValidationResponse(BaseModel):
    blueprint_id: int
    blueprint_title: str
    total_required_questions: int
    is_sufficient: bool
    rules: list[BlueprintValidationRule] = []


class GenerateTestFromBlueprintRequest(BaseModel):
    custom_title: str | None = None
    custom_slug: str | None = None
    random_seed: int | None = None


# Step 7: Mock Test Catalog Schemas


class CatalogCategoryItem(BaseModel):
    key: str
    title: str
    description: str
    test_count: int
    icon: str


class CatalogTopicItem(BaseModel):
    topic_id: int
    topic_title: str
    topic_slug: str
    test_count: int


class CatalogDifficultyItem(BaseModel):
    difficulty: DifficultyLevel
    label: str
    test_count: int


class CatalogTypeItem(BaseModel):
    test_type: MockTestType
    label: str
    test_count: int


class CatalogDurationOption(BaseModel):
    label: str
    min_minutes: int
    max_minutes: int | None = None


class CatalogFilterOptionsResponse(BaseModel):
    categories: list[CatalogCategoryItem]
    topics: list[CatalogTopicItem]
    difficulties: list[CatalogDifficultyItem]
    types: list[CatalogTypeItem]
    duration_ranges: list[CatalogDurationOption]


class CatalogStatisticsResponse(BaseModel):
    total_tests: int
    ready_tests: int
    draft_tests: int
    beginner_tests: int
    intermediate_tests: int
    advanced_tests: int
    full_mock_tests: int
    total_questions_represented: int


class MockTestPreviewTopicRule(BaseModel):
    topic_title: str
    topic_slug: str
    difficulty: DifficultyLevel | None = None
    question_count: int
    available_in_bank: int
    is_met: bool


class MockTestPreviewResponse(BaseModel):
    id: int
    code: str | None = None
    title: str
    slug: str
    description: str | None = None
    difficulty: DifficultyLevel
    test_type: MockTestType
    duration_minutes: int
    total_questions: int
    passing_percentage: float
    status: MockTestStatus
    prerequisites: str | None = None
    tags: list[str] = []
    is_ready: bool
    shortfall: int
    topics_covered: list[str] = []
    what_you_will_practice: list[str] = []
    syllabus_rules: list[MockTestPreviewTopicRule] = []
