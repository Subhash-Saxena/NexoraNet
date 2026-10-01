from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Schema for system health liveness status."""

    status: str = Field(default="ok", json_schema_extra={"example": "ok"})
    service: str = Field(
        default="NexoraNet API", json_schema_extra={"example": "NexoraNet API"}
    )
    environment: str = Field(
        default="development", json_schema_extra={"example": "production"}
    )


class ReadinessResponse(BaseModel):
    """Schema for system readiness and database connectivity probe."""

    status: str = Field(default="ready", json_schema_extra={"example": "ready"})
    service: str = Field(
        default="NexoraNet API", json_schema_extra={"example": "NexoraNet API"}
    )
    database: str = Field(
        default="connected", json_schema_extra={"example": "connected"}
    )
