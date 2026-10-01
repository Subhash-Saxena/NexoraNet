"""Pydantic schemas for Authentication and User Authorization."""

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import UserRole

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{3,32}$")


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class UserOut(BaseModel):
    """Public authenticated user profile (never exposes password_hash)."""

    id: int
    username: str
    email: str
    display_name: str | None = None
    role: UserRole
    current_level: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Login credentials schema."""

    username: str = Field(..., description="Username or email address", min_length=3, max_length=255)
    password: str = Field(..., description="User plaintext password", min_length=6, max_length=128)


class RegisterRequest(BaseModel):
    """New student user registration schema."""

    username: str = Field(..., min_length=3, max_length=32, description="Alphanumeric username")
    email: str = Field(..., min_length=5, max_length=255, description="Valid student email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong account password (min 8 characters)")
    display_name: str | None = Field(default=None, max_length=128, description="Optional public display name")
    role: UserRole | None = Field(default=UserRole.STUDENT, description="Account role")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("Invalid email address format.")
        return clean

    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if not USERNAME_REGEX.match(clean):
            raise ValueError(
                "Username must be 3-32 characters and contain only letters, numbers, underscores, periods, or hyphens."
            )
        return clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if v.isdigit() or v.isalpha():
            raise ValueError("Password must contain a mix of letters and numbers/special characters.")
        return v


class Token(BaseModel):
    """JWT bearer token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token lifespan in seconds")
    user: UserOut


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""

    sub: str
    role: str
    iat: int
    exp: int
    jti: str
