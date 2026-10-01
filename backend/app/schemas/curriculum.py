from pydantic import BaseModel

from app.models.enums import ContentType, DifficultyLevel


class LessonBrief(BaseModel):
    id: int
    topic_id: int
    title: str
    slug: str
    content_type: ContentType
    order_index: int
    estimated_minutes: int
    difficulty: DifficultyLevel

    model_config = {"from_attributes": True}


class LessonDetail(LessonBrief):
    description: str | None = None
    content: str


class TopicBrief(BaseModel):
    id: int
    module_id: int
    title: str
    slug: str
    description: str | None = None
    difficulty: DifficultyLevel
    order_index: int

    model_config = {"from_attributes": True}


class TopicDetail(TopicBrief):
    lessons: list[LessonBrief] = []


class ModuleBrief(BaseModel):
    id: int
    course_id: int
    title: str
    slug: str
    description: str | None = None
    order_index: int
    difficulty: DifficultyLevel
    topics_count: int = 0

    model_config = {"from_attributes": True}


class ModuleDetail(BaseModel):
    id: int
    course_id: int
    title: str
    slug: str
    description: str | None = None
    order_index: int
    difficulty: DifficultyLevel
    topics: list[TopicBrief] = []

    model_config = {"from_attributes": True}


class CourseBrief(BaseModel):
    id: int
    title: str
    slug: str
    description: str | None = None
    level: DifficultyLevel
    estimated_hours: int
    modules_count: int = 0

    model_config = {"from_attributes": True}


class CourseDetail(BaseModel):
    id: int
    title: str
    slug: str
    description: str | None = None
    level: DifficultyLevel
    estimated_hours: int
    modules: list[ModuleDetail] = []

    model_config = {"from_attributes": True}
