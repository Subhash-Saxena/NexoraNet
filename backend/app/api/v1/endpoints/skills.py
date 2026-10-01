"""Cybersecurity Skill Assessment API Endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.models.analytics import Skill
from app.schemas.analytics import SkillResponse
from app.services.analytics.skill_assessment_service import SkillAssessmentService

router = APIRouter()


@router.get("", response_model=list[SkillResponse])
@router.get("/", response_model=list[SkillResponse], include_in_schema=False)
def list_skills_assessment(
    db: DbSession, current_user: CurrentUser
) -> list[dict[str, Any]]:
    """Retrieve explainable proficiency and confidence assessments across all 28 cybersecurity skills."""
    return SkillAssessmentService.assess_all_skills(db, current_user)


@router.get("/assessment", response_model=list[SkillResponse])
def get_skills_assessment_summary(
    db: DbSession, current_user: CurrentUser
) -> list[dict[str, Any]]:
    """Alias for full skills assessment matrix."""
    return SkillAssessmentService.assess_all_skills(db, current_user)


@router.get("/{skill_id}", response_model=SkillResponse)
def get_single_skill_assessment(
    skill_id: str, db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Retrieve detailed evidence breakdown, confidence, and recommended practice for a specific skill."""
    if skill_id.isdigit():
        skill = db.query(Skill).filter(Skill.id == int(skill_id)).first()
    else:
        skill = db.query(Skill).filter(Skill.skill_code == skill_id.upper()).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_id}' was not found in taxonomy.",
        )

    return SkillAssessmentService.assess_single_skill(db, current_user, skill)
