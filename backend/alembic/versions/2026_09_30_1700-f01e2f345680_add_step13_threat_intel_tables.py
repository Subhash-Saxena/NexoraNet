"""Add Step 13 Threat Intelligence and IOC Investigation tables.

Revision ID: f01e2f345680
Revises: e01e2f345679
Create Date: 2026-09-30 17:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f01e2f345680"
down_revision: str | None = "e01e2f345679"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. threat_intel_sources
    op.create_table(
        "threat_intel_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False, server_default="SYNTHETIC"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reliability", sa.String(length=50), nullable=False, server_default="HIGH"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_threat_intel_sources_id", "threat_intel_sources", ["id"])
    op.create_index("ix_threat_intel_sources_name", "threat_intel_sources", ["name"])

    # 2. indicators
    op.create_table(
        "indicators",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_id", sa.String(length=50), nullable=False),
        sa.Column("indicator_type", sa.String(length=50), nullable=False),
        sa.Column("hash_type", sa.String(length=20), nullable=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("normalized_value", sa.String(length=512), nullable=False),
        sa.Column("display_value", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("source_name", sa.String(length=100), nullable=False, server_default="NexoraNet Synthetic Threat Intelligence"),
        sa.Column("classification", sa.String(length=50), nullable=False, server_default="UNKNOWN"),
        sa.Column("confidence", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="INFO"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("false_positive_reason", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("mitre_attack_id", sa.String(length=50), nullable=True),
        sa.Column("mitre_technique", sa.String(length=150), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["threat_intel_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("indicator_id"),
    )
    op.create_index("ix_indicators_id", "indicators", ["id"])
    op.create_index("ix_indicators_indicator_id", "indicators", ["indicator_id"])
    op.create_index("ix_indicators_indicator_type", "indicators", ["indicator_type"])
    op.create_index("ix_indicators_normalized_value", "indicators", ["normalized_value"])
    op.create_index("ix_indicators_classification", "indicators", ["classification"])
    op.create_index("ix_indicators_status", "indicators", ["status"])

    # 3. indicator_relationships
    op.create_table(
        "indicator_relationships",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_indicator_id", sa.Integer(), nullable=False),
        sa.Column("target_indicator_id", sa.Integer(), nullable=False),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_indicator_id"], ["indicators.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_indicator_id"], ["indicators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indicator_relationships_id", "indicator_relationships", ["id"])
    op.create_index("ix_indicator_relationships_source_id", "indicator_relationships", ["source_indicator_id"])
    op.create_index("ix_indicator_relationships_target_id", "indicator_relationships", ["target_indicator_id"])

    # 4. indicator_observations
    op.create_table(
        "indicator_observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=True),
        sa.Column("packet_number", sa.Integer(), nullable=True),
        sa.Column("alert_id", sa.Integer(), nullable=True),
        sa.Column("investigation_id", sa.Integer(), nullable=True),
        sa.Column("case_id", sa.Integer(), nullable=True),
        sa.Column("observation_type", sa.String(length=50), nullable=False),
        sa.Column("context_data", sa.Text(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["indicator_id"], ["indicators.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["alert_id"], ["detection_alerts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indicator_observations_id", "indicator_observations", ["id"])
    op.create_index("ix_indicator_observations_indicator_id", "indicator_observations", ["indicator_id"])
    op.create_index("ix_indicator_observations_capture_id", "indicator_observations", ["capture_id"])
    op.create_index("ix_indicator_observations_alert_id", "indicator_observations", ["alert_id"])
    op.create_index("ix_indicator_observations_investigation_id", "indicator_observations", ["investigation_id"])
    op.create_index("ix_indicator_observations_case_id", "indicator_observations", ["case_id"])

    # 5. indicator_timelines
    op.create_table(
        "indicator_timelines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("actor_name", sa.String(length=100), nullable=False, server_default="System"),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["indicator_id"], ["indicators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indicator_timelines_id", "indicator_timelines", ["id"])
    op.create_index("ix_indicator_timelines_indicator_id", "indicator_timelines", ["indicator_id"])

    # 6. indicator_notes
    op.create_table(
        "indicator_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("author_name", sa.String(length=100), nullable=False, server_default="SOC Analyst"),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["indicator_id"], ["indicators.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indicator_notes_id", "indicator_notes", ["id"])
    op.create_index("ix_indicator_notes_indicator_id", "indicator_notes", ["indicator_id"])

    # 7. indicator_watchlists
    op.create_table(
        "indicator_watchlists",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("added_by", sa.String(length=100), nullable=False, server_default="SOC Analyst"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["indicator_id"], ["indicators.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_indicator_watchlists_id", "indicator_watchlists", ["id"])
    op.create_index("ix_indicator_watchlists_indicator_id", "indicator_watchlists", ["indicator_id"])
    op.create_index("ix_indicator_watchlists_user_id", "indicator_watchlists", ["user_id"])

    # 8. threat_intel_challenges
    op.create_table(
        "threat_intel_challenges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=False, server_default="BEGINNER"),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("scenario_description", sa.Text(), nullable=False),
        sa.Column("target_indicator_value", sa.String(length=255), nullable=False),
        sa.Column("expected_classification", sa.String(length=50), nullable=False),
        sa.Column("expected_observations", sa.Text(), nullable=True),
        sa.Column("rubric_description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_threat_intel_challenges_id", "threat_intel_challenges", ["id"])
    op.create_index("ix_threat_intel_challenges_slug", "threat_intel_challenges", ["slug"])

    # 9. threat_intel_challenge_attempts
    op.create_table(
        "threat_intel_challenge_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("selected_classification", sa.String(length=50), nullable=False),
        sa.Column("hypothesis_text", sa.Text(), nullable=False),
        sa.Column("evidence_notes", sa.Text(), nullable=False),
        sa.Column("conclusion", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["challenge_id"], ["threat_intel_challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_intel_challenge_attempts_id", "threat_intel_challenge_attempts", ["id"])
    op.create_index("ix_threat_intel_challenge_attempts_challenge_id", "threat_intel_challenge_attempts", ["challenge_id"])
    op.create_index("ix_threat_intel_challenge_attempts_user_id", "threat_intel_challenge_attempts", ["user_id"])

    # 10. threat_intel_enrichment_cache
    op.create_table(
        "threat_intel_enrichment_cache",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("indicator_type", sa.String(length=50), nullable=False),
        sa.Column("normalized_value", sa.String(length=512), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("classification", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.String(length=50), nullable=False),
        sa.Column("categories", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("raw_metadata", sa.Text(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_intel_enrichment_cache_id", "threat_intel_enrichment_cache", ["id"])
    op.create_index("ix_threat_intel_enrichment_cache_normalized", "threat_intel_enrichment_cache", ["normalized_value"])


def downgrade() -> None:
    op.drop_table("threat_intel_enrichment_cache")
    op.drop_table("threat_intel_challenge_attempts")
    op.drop_table("threat_intel_challenges")
    op.drop_table("indicator_watchlists")
    op.drop_table("indicator_notes")
    op.drop_table("indicator_timelines")
    op.drop_table("indicator_observations")
    op.drop_table("indicator_relationships")
    op.drop_table("indicators")
    op.drop_table("threat_intel_sources")
