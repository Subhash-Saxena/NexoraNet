"""Student Portfolio API Endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import (
    PortfolioProjectCreate,
    PortfolioProjectUpdate,
    PortfolioUpdate,
)
from app.services.analytics.portfolio_service import PortfolioService

router = APIRouter()


@router.get("", response_model=dict[str, Any])
@router.get("/", response_model=dict[str, Any], include_in_schema=False)
def get_my_portfolio(
    db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Retrieve the current user's portfolio with privacy settings, projects, and demonstrated work."""
    p = PortfolioService.get_or_create_portfolio(db, current_user)
    return {
        "id": p.id,
        "public_slug": p.public_slug,
        "visibility": p.visibility.value if hasattr(p.visibility, "value") else str(p.visibility),
        "display_name": p.display_name,
        "bio": p.bio,
        "learning_focus": p.learning_focus,
        "social_links": p.social_links,
        "show_stats": p.show_stats,
        "show_skills": p.show_skills,
        "show_certifications": p.show_certifications,
        "no_index": p.no_index,
        "projects": [
            {
                "id": proj.id,
                "title": proj.title,
                "description": proj.description,
                "technologies": proj.technologies,
                "skills": proj.skills,
                "learning_outcome": proj.learning_outcome,
                "repository_url": proj.repository_url,
                "demo_url": proj.demo_url,
                "completed_date": proj.completed_date,
                "is_featured": proj.is_featured,
            }
            for proj in p.projects
        ],
    }


@router.put("", response_model=dict[str, Any])
def update_my_portfolio(
    payload: PortfolioUpdate, db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Update portfolio profile details, privacy tiers, and visibility preferences."""
    data = payload.model_dump(exclude_unset=True)
    p = PortfolioService.update_portfolio(db, current_user, data)
    return {
        "id": p.id,
        "public_slug": p.public_slug,
        "visibility": p.visibility.value if hasattr(p.visibility, "value") else str(p.visibility),
        "display_name": p.display_name,
        "bio": p.bio,
        "learning_focus": p.learning_focus,
        "social_links": p.social_links,
        "show_stats": p.show_stats,
        "show_skills": p.show_skills,
        "show_certifications": p.show_certifications,
        "no_index": p.no_index,
        "projects": [
            {
                "id": proj.id,
                "title": proj.title,
                "description": proj.description,
                "technologies": proj.technologies,
                "skills": proj.skills,
                "learning_outcome": proj.learning_outcome,
                "repository_url": proj.repository_url,
                "demo_url": proj.demo_url,
                "completed_date": proj.completed_date,
                "is_featured": proj.is_featured,
            }
            for proj in p.projects
        ],
    }


@router.get("/public/{public_slug}", response_model=dict[str, Any])
def get_public_portfolio(
    public_slug: str, db: DbSession
) -> dict[str, Any]:
    """Public read-only portfolio endpoint. Strips private emails, notes, flags, and sensitive fields."""
    try:
        return PortfolioService.get_public_portfolio(db, public_slug)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/projects", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_project(
    payload: PortfolioProjectCreate, db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Add a custom student project to portfolio with strict URL validation and text sanitization."""
    try:
        proj = PortfolioService.add_project(db, current_user, payload.model_dump())
        return {
            "id": proj.id,
            "title": proj.title,
            "description": proj.description,
            "technologies": proj.technologies,
            "skills": proj.skills,
            "learning_outcome": proj.learning_outcome,
            "repository_url": proj.repository_url,
            "demo_url": proj.demo_url,
            "completed_date": proj.completed_date,
            "is_featured": proj.is_featured,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/projects/{project_id}", response_model=dict[str, Any])
def update_project(
    project_id: int,
    payload: PortfolioProjectUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Update project with IDOR ownership verification."""
    try:
        proj = PortfolioService.update_project(
            db, current_user, project_id, payload.model_dump(exclude_unset=True)
        )
        return {
            "id": proj.id,
            "title": proj.title,
            "description": proj.description,
            "technologies": proj.technologies,
            "skills": proj.skills,
            "learning_outcome": proj.learning_outcome,
            "repository_url": proj.repository_url,
            "demo_url": proj.demo_url,
            "completed_date": proj.completed_date,
            "is_featured": proj.is_featured,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/projects/{project_id}", response_model=dict[str, Any])
def delete_project(
    project_id: int, db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Delete project with IDOR ownership verification."""
    success = PortfolioService.delete_project(db, current_user, project_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return {"status": "deleted", "project_id": project_id}


@router.get("/export/json", response_model=dict[str, Any])
def export_portfolio_json(
    db: DbSession, current_user: CurrentUser
) -> dict[str, Any]:
    """Export portfolio as structured JSON document without leaking private metadata or answers."""
    return PortfolioService.export_portfolio_json(db, current_user)
