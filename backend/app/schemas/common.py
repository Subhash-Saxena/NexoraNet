from typing import Any

from pydantic import BaseModel, Field


class ModuleStatusResponse(BaseModel):
    """Schema describing the readiness status of platform modules."""

    module: str
    status: str = Field(..., json_schema_extra={"example": "planned"})
    description: str
    planned_phase: str = Field(..., json_schema_extra={"example": "Phase 2"})
    capabilities: list[str] = Field(default_factory=list)


class ErrorDetail(BaseModel):
    """Schema for structured error representation."""

    code: str
    message: str
    details: Any | None = None


class StandardErrorResponse(BaseModel):
    """Standard container for error payloads."""

    error: ErrorDetail
