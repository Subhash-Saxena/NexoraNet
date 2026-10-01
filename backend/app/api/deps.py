"""FastAPI request dependencies for Database sessions, Authentication, and Role-Based Access Control (RBAC)."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User

settings = get_settings()

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_user_role: Annotated[str | None, Header(alias="X-User-Role")] = None,
    x_user_id: Annotated[int | None, Header(alias="X-User-Id")] = None,
) -> User:
    """Resolve authenticated user from JWT Bearer token or development test headers.

    Production Policy:
    In production (ENVIRONMENT=production), valid Bearer JWT authentication is strictly required.

    Development Policy:
    In development and testing, Bearer JWT is honored first. If absent, fallback to X-User-Role /
    X-User-Id or the default seeded student is permitted for local developer productivity and test suites.
    """
    # 1. Bearer JWT Authentication (Standard in all environments)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split("Bearer ", 1)[1].strip()
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if user_id_str:
            try:
                user_id = int(user_id_str)
                user = db.query(User).filter(User.id == user_id).first()
                if not user or not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User account is inactive or does not exist.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return user
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Malformed user subject in authentication token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    # 2. Strict Production Guardrail: No unauthenticated access in production
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or are invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Development / Test fallbacks (Only allowed when ENVIRONMENT is not production)
    if x_user_id is not None:
        user = db.query(User).filter(User.id == x_user_id).first()
        if user:
            return user

    if x_user_role:
        role_clean = x_user_role.strip().upper()
        if role_clean in ("ADMIN", "INSTRUCTOR", "STUDENT"):
            user = db.query(User).filter(User.role == UserRole(role_clean)).first()
            if user:
                return user

    # Default fallback: student_dev or first student
    user = db.query(User).filter(User.username == "student_dev").first()
    if not user:
        user = db.query(User).filter(User.role == UserRole.STUDENT).first()
    if not user:
        user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No student user accounts found in database. Please run seeding script.",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_optional_current_user(
    db: DbSession,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_user_role: Annotated[str | None, Header(alias="X-User-Role")] = None,
    x_user_id: Annotated[int | None, Header(alias="X-User-Id")] = None,
) -> User | None:
    """Resolve current user if credentials provided, or return None for public/preview requests."""
    try:
        return get_current_user(db, authorization, x_user_role, x_user_id)
    except HTTPException:
        return None


OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]



def require_admin_user(current_user: CurrentUser) -> User:
    """Enforce strict server-side administrator authorization."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator authorization required. Students cannot access administrative controls.",
        )
    return current_user


AdminUser = Annotated[User, Depends(require_admin_user)]


def require_instructor_or_admin(current_user: CurrentUser) -> User:
    """Enforce instructor or administrator authorization for instructional management."""
    if current_user.role not in (UserRole.ADMIN, UserRole.INSTRUCTOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instructor or Administrator authorization required.",
        )
    return current_user


StaffUser = Annotated[User, Depends(require_instructor_or_admin)]


def verify_resource_ownership(resource_owner_id: int, current_user: User) -> None:
    """IDOR protection: Verify current user owns the target resource, or has Staff/Admin privileges."""
    if current_user.role in (UserRole.ADMIN, UserRole.INSTRUCTOR):
        return  # Staff and admins may inspect or moderate student resources

    if current_user.id != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to view or modify another student's record.",
        )
