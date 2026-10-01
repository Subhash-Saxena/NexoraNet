"""Pydantic v2 schemas for administration dashboard, content operations, and audit ledger."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class AdminDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_users: int
    active_learners: int
    catalog_counts: dict[str, int]
    publication_status: dict[str, int]
    recent_audit_logs: list[dict[str, Any]]


class AdminContentItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content_type: str
    code_or_slug: str
    title: str
    category: str
    difficulty: str
    status: str
    updated_at: str


class AdminContentPublishResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content_type: str
    content_id: str
    status: str
    version: int
    published_at: str


class AdminAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    actor_username: str
    action: str
    target_type: str
    target_id: str
    metadata: dict[str, Any]
    created_at: str
