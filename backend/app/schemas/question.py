from pydantic import BaseModel

from app.models.enums import (
    CognitiveLevel,
    DifficultyLevel,
    QuestionStatus,
    QuestionType,
)


class QuestionTagResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class StudentQuestionOptionResponse(BaseModel):
    """Option payload for student testing without correctness indicators."""

    id: int
    option_text: str
    order_index: int

    model_config = {"from_attributes": True}


class AdminQuestionOptionResponse(StudentQuestionOptionResponse):
    """Option payload for instructors and test authors."""

    is_correct: bool
    explanation: str | None = None


class StudentQuestionResponse(BaseModel):
    """
    Student-facing question schema.
    CRITICAL SECURITY GUARANTEE: Neither 'is_correct' nor answer explanations
    are leaked through this schema prior to official exam submission.
    """

    id: int
    code: str | None = None
    question_text: str
    question_type: QuestionType
    topic_id: int
    difficulty: DifficultyLevel
    cognitive_level: CognitiveLevel
    points: int
    estimated_seconds: int
    options: list[StudentQuestionOptionResponse] = []
    tags: list[QuestionTagResponse] = []

    model_config = {"from_attributes": True}


class AdminQuestionResponse(BaseModel):
    """Instructor/administrative question schema with answer keys and explanations."""

    id: int
    code: str | None = None
    question_text: str
    question_type: QuestionType
    topic_id: int
    difficulty: DifficultyLevel
    cognitive_level: CognitiveLevel
    explanation: str
    learning_objective: str | None = None
    points: int
    estimated_seconds: int
    status: QuestionStatus
    options: list[AdminQuestionOptionResponse] = []
    tags: list[QuestionTagResponse] = []

    model_config = {"from_attributes": True}


class QuestionOptionCreate(BaseModel):
    option_text: str
    is_correct: bool = False
    order_index: int = 0
    explanation: str | None = None


class AdminQuestionCreate(BaseModel):
    code: str | None = None
    question_text: str
    question_type: QuestionType
    topic_id: int
    difficulty: DifficultyLevel
    cognitive_level: CognitiveLevel = CognitiveLevel.UNDERSTAND
    explanation: str
    learning_objective: str | None = None
    points: int = 1
    estimated_seconds: int = 60
    status: QuestionStatus = QuestionStatus.PUBLISHED
    options: list[QuestionOptionCreate] = []
    tags: list[str] = []


class AdminQuestionUpdate(BaseModel):
    code: str | None = None
    question_text: str | None = None
    question_type: QuestionType | None = None
    topic_id: int | None = None
    difficulty: DifficultyLevel | None = None
    cognitive_level: CognitiveLevel | None = None
    explanation: str | None = None
    learning_objective: str | None = None
    points: int | None = None
    estimated_seconds: int | None = None
    status: QuestionStatus | None = None
    options: list[QuestionOptionCreate] | None = None
    tags: list[str] | None = None


class QuestionBankStatistics(BaseModel):
    total_questions: int
    by_difficulty: dict[str, int]
    by_topic: dict[str, int]
    by_question_type: dict[str, int]
    by_cognitive_level: dict[str, int]
    by_status: dict[str, int]

