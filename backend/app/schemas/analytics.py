"""Pydantic v2 schemas for student analytics, skills, recommendations, reports, and portfolio."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StudentOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    display_name: str
    current_level: str
    total_learning_time_minutes: int
    lessons_completed: int
    total_lessons: int
    labs_completed: int
    total_labs: int
    tests_attempted: int
    tests_completed: int
    challenges_attempted: int
    challenges_solved: int
    total_challenges: int
    total_challenge_points: float
    soc_scenarios_completed: int
    total_scenarios: int
    incidents_investigated: int
    pcap_investigations_completed: int
    siem_investigations_completed: int
    endpoint_investigations_completed: int
    current_learning_streak: int
    recent_activity: list[dict[str, Any]]


class LearningProgressModule(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    module_id: int
    title: str
    slug: str
    category: str
    total_lessons: int
    completed_lessons: int
    completion_percentage: float


class LearningProgressSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    overall_completion_percentage: float
    total_lessons: int
    completed_lessons: int
    modules: list[LearningProgressModule]


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: int
    skill_code: str
    name: str
    category: str
    description: str
    related_topics: list[str]
    attempts: int
    completed_activities: int
    practical_activities: int
    accuracy: float
    completion_rate: float
    recent_performance: float
    confidence: str
    confidence_reason: str
    evidence_breakdown: dict[str, Any]
    educational_guidance: str
    last_activity_at: str | None = None


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recommendation_type: str
    title: str
    rationale: str
    target_url: str
    priority: str
    is_dismissed: bool
    created_at: str


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str
    description: str
    category: str
    badge_icon: str
    criteria_description: str
    required_count: int
    target_type: str
    progress_count: int
    is_unlocked: bool
    unlocked_at: str | None = None


class PortfolioProjectCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., min_length=5)
    technologies: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    learning_outcome: str = Field("", max_length=500)
    repository_url: str | None = None
    demo_url: str | None = None
    completed_date: str | None = None
    is_featured: bool = True


class PortfolioProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    technologies: list[str] | None = None
    skills: list[str] | None = None
    learning_outcome: str | None = None
    repository_url: str | None = None
    demo_url: str | None = None
    completed_date: str | None = None
    is_featured: bool | None = None


class PortfolioUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    learning_focus: str | None = None
    visibility: str | None = None
    social_links: dict[str, str] | None = None
    show_stats: bool | None = None
    show_skills: bool | None = None
    show_certifications: bool | None = None
    no_index: bool | None = None


class AssessmentReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_uuid: str
    title: str
    generated_at: str
    disclaimer: str
    summary: dict[str, Any]


class CertificateVerifyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    verification_code: str
    student_name: str
    course_or_module_title: str
    issued_at: str
    disclaimer: str
    is_valid: bool
