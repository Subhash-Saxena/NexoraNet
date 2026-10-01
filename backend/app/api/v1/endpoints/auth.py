"""Authentication endpoints: Login, Registration, and User Profile.

Provides JWT issuance, brute-force rate limiting, and password verification.
"""

import logging

import jwt
from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import or_

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    hash_password,
    rate_limiter,
    token_revocation_registry,
    verify_password,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, Token, UserOut

logger = logging.getLogger("nexoranet.auth")
router = APIRouter()
settings = get_settings()


def _get_client_ip(request: Request) -> str:
    """Extract client IP safely from forwarded headers or direct connection."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user and issue JWT bearer token",
)
def login(
    req: LoginRequest,
    db: DbSession,
    request: Request,
    response: Response,
) -> Token:
    """Verify credentials, enforce brute-force rate limiting, and issue JWT."""
    client_ip = _get_client_ip(request)
    allowed, _remaining, retry_after = rate_limiter.check(
        f"login:{client_ip}",
        max_requests=settings.RATE_LIMIT_LOGIN_PER_MINUTE,
        window_seconds=60,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please retry in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    # Allow login by either username or email address
    identifier = req.username.strip().lower()
    user = (
        db.query(User)
        .filter(or_(User.username.ilike(identifier), User.email.ilike(identifier)))
        .first()
    )

    if not user or not user.is_active or not verify_password(req.password, user.password_hash):
        # Generic authentication failure message prevents username enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue signed JWT token
    token = create_access_token(
        subject=user.id,
        role=user.role.value,
    )

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
def register(
    req: RegisterRequest,
    db: DbSession,
    request: Request,
) -> Token:
    """Register student user account, hash password, and issue initial JWT."""
    client_ip = _get_client_ip(request)
    allowed, _remaining, retry_after = rate_limiter.check(
        f"register:{client_ip}",
        max_requests=settings.RATE_LIMIT_LOGIN_PER_MINUTE,
        window_seconds=60,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Registration rate limit exceeded. Please wait {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    clean_username = req.username.strip().lower()
    clean_email = str(req.email).strip().lower()

    # Verify uniqueness
    existing = (
        db.query(User)
        .filter(or_(User.username.ilike(clean_username), User.email.ilike(clean_email)))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this username or email already exists.",
        )

    # Securely hash password using PBKDF2-HMAC-SHA256
    hashed_pw = hash_password(req.password)

    new_user = User(
        username=clean_username,
        email=clean_email,
        password_hash=hashed_pw,
        display_name=req.display_name or req.username,
        role=UserRole.STUDENT,
        current_level="Cadet Defend-I",
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        subject=new_user.id,
        role=new_user.role.value,
    )

    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(new_user),
    )


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current authenticated user profile",
)
def get_current_user_profile(
    current_user: CurrentUser,
) -> UserOut:
    """Return identity and roles of the current authenticated user."""
    return UserOut.model_validate(current_user)


@router.post(
    "/logout",
    summary="Invalidate active session and revoke JWT access token",
)
def logout(
    request: Request,
    current_user: CurrentUser,
) -> dict[str, str]:
    """Revoke caller's active bearer token server-side and invalidate session."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split("Bearer ", 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                settings.effective_jwt_secret,
                algorithms=[settings.JWT_ALGORITHM],
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                token_revocation_registry.revoke(jti, exp)
        except jwt.PyJWTError as e:
            logger.debug(f"Invalid or expired token during logout: {e}")

    return {
        "status": "ok",
        "message": "Successfully logged out. Session credentials invalidated.",
    }

