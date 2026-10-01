from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    PROJECT_NAME: str = "NexoraNet API"
    PROJECT_TAGLINE: str = "Learn. Simulate. Analyze. Defend."
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server binding
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./nexoranet.db"

    # CORS configuration
    CORS_ORIGINS: str | list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # Security configuration
    SECRET_KEY: str = "nexoranet-dev-secret-key-change-in-production-only"
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database pooling (PostgreSQL)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 300

    # Rate limiting configuration (per client IP)
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 10
    RATE_LIMIT_FLAG_PER_MINUTE: int = 30

    # Security Headers & Network Security
    STRICT_SECURITY_HEADERS: bool = True
    TRUSTED_HOSTS: list[str] = ["*"]

    # Lab isolation boundary
    LAB_ALLOWED_SUBNET: str = "10.99.0.0/16"

    @property
    def effective_jwt_secret(self) -> str:
        """Return dedicated JWT secret key or fallback to system SECRET_KEY."""
        return self.JWT_SECRET_KEY if self.JWT_SECRET_KEY else self.SECRET_KEY

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def resolve_sqlite_path(cls, v: str) -> str:
        if (
            v.startswith("sqlite:///")
            and not v.startswith("sqlite:////")
            and not v.startswith("sqlite:///:memory:")
        ):
            rel_path = v[len("sqlite:///") :]
            backend_dir = Path(__file__).resolve().parents[2]
            abs_db_path = (backend_dir / rel_path).resolve()
            return f"sqlite:///{abs_db_path.as_posix()}"
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return []

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        """Fail fast on insecure configuration settings when running in production environment."""
        if self.ENVIRONMENT.lower() == "production":
            errors = []
            sec_key = self.effective_jwt_secret
            if (
                sec_key == "nexoranet-dev-secret-key-change-in-production-only"
                or "dev" in sec_key.lower()
                or "changeme" in sec_key.lower()
                or len(sec_key) < 32
            ):
                errors.append(
                    "SECRET_KEY / JWT_SECRET_KEY must be a cryptographically secure random string of >=32 chars in production."
                )

            if self.DATABASE_URL.startswith("sqlite"):
                errors.append(
                    "SQLite is prohibited in production; a production-grade database like PostgreSQL is required."
                )

            if self.DEBUG is True:
                errors.append("DEBUG must be set to False in production.")

            origins = self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else [self.CORS_ORIGINS]
            if "*" in origins:
                errors.append("Wildcard '*' CORS origins are strictly forbidden in production.")
            for origin in origins:
                if "localhost" in origin or "127.0.0.1" in origin:
                    errors.append(f"Insecure local origin '{origin}' detected in production CORS configuration.")

            if errors:
                raise ValueError("Insecure production configuration detected:\n" + "\n".join(f"- {e}" for e in errors))
        return self

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached instance of application settings."""
    return Settings()
