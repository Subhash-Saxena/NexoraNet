"""Add Step 8 Adaptive Engine tables: performance_snapshots and recommendation_events.

Revision ID: a78b9c1d2e3f
Revises: f19a8b2c4e33
Create Date: 2026-09-30 09:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a78b9c1d2e3f"
down_revision: str | None = "f19a8b2c4e33"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create performance_snapshots table
    op.create_table(
        "performance_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("questions_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempts_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_accuracy", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("recommended_difficulty", sa.String(length=20), nullable=False, server_default="BEGINNER"),
        sa.Column("strong_topic_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("developing_topic_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("needs_practice_topic_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_performance_snapshots_id"), "performance_snapshots", ["id"], unique=False)
    op.create_index(op.f("ix_performance_snapshots_user_id"), "performance_snapshots", ["user_id"], unique=False)

    # 2. Create recommendation_events table
    op.create_table(
        "recommendation_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recommendation_type", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("topic_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("action_url", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False, server_default="GENERATED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recommendation_events_id"), "recommendation_events", ["id"], unique=False)
    op.create_index(op.f("ix_recommendation_events_user_id"), "recommendation_events", ["user_id"], unique=False)
    op.create_index(op.f("ix_recommendation_events_topic_id"), "recommendation_events", ["topic_id"], unique=False)
    op.create_index(op.f("ix_recommendation_events_recommendation_type"), "recommendation_events", ["recommendation_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_recommendation_events_recommendation_type"), table_name="recommendation_events")
    op.drop_index(op.f("ix_recommendation_events_topic_id"), table_name="recommendation_events")
    op.drop_index(op.f("ix_recommendation_events_user_id"), table_name="recommendation_events")
    op.drop_index(op.f("ix_recommendation_events_id"), table_name="recommendation_events")
    op.drop_table("recommendation_events")

    op.drop_index(op.f("ix_performance_snapshots_user_id"), table_name="performance_snapshots")
    op.drop_index(op.f("ix_performance_snapshots_id"), table_name="performance_snapshots")
    op.drop_table("performance_snapshots")
