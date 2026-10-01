from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.curriculum import Module
from app.schemas.curriculum import ModuleDetail

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/{module_id}", response_model=ModuleDetail)
def get_module_detail(module_id: str, db: DbSession) -> Module:
    """Retrieve detailed module metadata and contained topics by ID or slug."""
    query = (
        db.query(Module)
        .options(selectinload(Module.topics))
        .filter(Module.is_published.is_(True))
    )

    if module_id.isdigit():
        module = query.filter(Module.id == int(module_id)).first()
    else:
        module = query.filter(Module.slug == module_id).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' was not found.",
        )
    return module
