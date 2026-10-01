from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ContentType, DifficultyLevel, ProgressStatus
from app.schemas.curriculum import LessonBrief, TopicBrief


class PrerequisiteTopicBrief(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: DifficultyLevel
    is_completed: bool = False

    model_config = {"from_attributes": True}


class LessonBriefWithProgress(BaseModel):
    id: int
    topic_id: int
    title: str
    slug: str
    content_type: ContentType
    order_index: int
    estimated_minutes: int
    difficulty: DifficultyLevel
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    is_bookmarked: bool = False

    model_config = {"from_attributes": True}


class RelatedItemBrief(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: DifficultyLevel
    status: str = "coming_soon"
    description: str | None = None


class TopicDetailExtended(BaseModel):
    id: int
    module_id: int
    module_title: str
    module_slug: str
    course_id: int
    course_title: str
    course_slug: str
    title: str
    slug: str
    description: str | None = None
    difficulty: DifficultyLevel
    order_index: int
    estimated_minutes: int
    learning_objectives: list[str] = []
    security_relevance: str | None = None
    prerequisites: list[PrerequisiteTopicBrief] = []
    lessons: list[LessonBriefWithProgress] = []
    lessons_count: int = 0
    completed_lessons_count: int = 0
    completion_percentage: float = 0.0
    related_labs: list[RelatedItemBrief] = []
    related_mock_tests: list[RelatedItemBrief] = []
    next_topic: TopicBrief | None = None
    previous_topic: TopicBrief | None = None

    model_config = {"from_attributes": True}


class LessonDetailExtended(BaseModel):
    id: int
    topic_id: int
    topic_title: str
    topic_slug: str
    module_id: int
    module_title: str
    module_slug: str
    course_id: int
    course_title: str
    course_slug: str
    title: str
    slug: str
    description: str | None = None
    content: str
    content_type: ContentType
    order_index: int
    estimated_minutes: int
    difficulty: DifficultyLevel
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    last_accessed_at: datetime | None = None
    is_bookmarked: bool = False
    next_lesson: LessonBrief | None = None
    previous_lesson: LessonBrief | None = None
    related_lab: RelatedItemBrief | None = None
    related_mock_test: RelatedItemBrief | None = None

    model_config = {"from_attributes": True}


class LevelProgress(BaseModel):
    level: DifficultyLevel
    total_lessons: int = 0
    completed_lessons: int = 0
    percentage: float = 0.0


class ContinueLearningItem(BaseModel):
    lesson_id: int
    lesson_title: str
    lesson_slug: str
    topic_title: str
    topic_slug: str
    module_title: str
    module_slug: str
    difficulty: DifficultyLevel
    estimated_minutes: int
    lesson_index: int
    total_topic_lessons: int


class LearningProgressResponse(BaseModel):
    overall_percentage: float
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    remaining_lessons: int
    current_level: str
    beginner_progress: LevelProgress
    intermediate_progress: LevelProgress
    advanced_progress: LevelProgress
    continue_learning: ContinueLearningItem | None = None


class SearchResultItem(BaseModel):
    type: str  # 'course', 'module', 'topic', 'lesson'
    id: int
    title: str
    slug: str
    description: str | None = None
    difficulty: DifficultyLevel
    parent_title: str | None = None
    url: str


class LearningSearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResultItem]


class BookmarkItem(BaseModel):
    id: int
    lesson_id: int
    lesson_title: str
    lesson_slug: str
    topic_title: str
    topic_slug: str
    module_title: str
    module_slug: str
    difficulty: DifficultyLevel
    estimated_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LessonActionResponse(BaseModel):
    message: str
    lesson_id: int
    status: ProgressStatus
    updated_at: datetime
