"""Add Step 15 SIEM & Security Log Analysis Engine tables.

Revision ID: h01e2f345682
Revises: g01e2f345681
Create Date: 2026-09-30 20:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "h01e2f345682"
down_revision: str | None = "g01e2f345681"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. log_sources
    op.create_table(
        "log_sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stable_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False),
        sa.Column("vendor", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ACTIVE"),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stable_id"),
    )
    op.create_index("ix_log_sources_id", "log_sources", ["id"])
    op.create_index("ix_log_sources_stable_id", "log_sources", ["stable_id"])
    op.create_index("ix_log_sources_source_type", "log_sources", ["source_type"])
    op.create_index("ix_log_sources_status", "log_sources", ["status"])

    # 2. security_log_datasets
    op.create_table(
        "security_log_datasets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stable_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("dataset_type", sa.String(length=64), nullable=False, server_default="BEGINNER"),
        sa.Column("difficulty", sa.String(length=32), nullable=False, server_default="BEGINNER"),
        sa.Column("event_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stable_id"),
    )
    op.create_index("ix_security_log_datasets_id", "security_log_datasets", ["id"])
    op.create_index("ix_security_log_datasets_stable_id", "security_log_datasets", ["stable_id"])
    op.create_index("ix_security_log_datasets_dataset_type", "security_log_datasets", ["dataset_type"])

    # 3. raw_log_events
    op.create_table(
        "raw_log_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_message", sa.Text(), nullable=False),
        sa.Column("format", sa.String(length=32), nullable=False, server_default="JSON"),
        sa.Column("sequence_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["security_log_datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["log_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_raw_log_events_id", "raw_log_events", ["id"])
    op.create_index("ix_raw_log_events_source_id", "raw_log_events", ["source_id"])
    op.create_index("ix_raw_log_events_dataset_id", "raw_log_events", ["dataset_id"])
    op.create_index("ix_raw_log_events_timestamp", "raw_log_events", ["timestamp"])

    # 4. security_events
    op.create_table(
        "security_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_category", sa.String(length=64), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("source_ip", sa.String(length=64), nullable=True),
        sa.Column("source_port", sa.Integer(), nullable=True),
        sa.Column("destination_ip", sa.String(length=64), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=True),
        sa.Column("protocol", sa.String(length=32), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="INFO"),
        sa.Column("process_name", sa.String(length=255), nullable=True),
        sa.Column("parent_process", sa.String(length=255), nullable=True),
        sa.Column("command_summary", sa.Text(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_hash", sa.String(length=128), nullable=True),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("authentication_method", sa.String(length=64), nullable=True),
        sa.Column("result", sa.String(length=64), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("raw_event_id", sa.Integer(), nullable=True),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["security_log_datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["raw_event_id"], ["raw_log_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["log_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_security_events_id", "security_events", ["id"])
    op.create_index("ix_security_events_event_id", "security_events", ["event_id"])
    op.create_index("ix_security_events_timestamp", "security_events", ["timestamp"])
    op.create_index("ix_security_events_event_type", "security_events", ["event_type"])
    op.create_index("ix_security_events_event_category", "security_events", ["event_category"])
    op.create_index("ix_security_events_source_type", "security_events", ["source_type"])
    op.create_index("ix_security_events_host", "security_events", ["host"])
    op.create_index("ix_security_events_username", "security_events", ["username"])
    op.create_index("ix_security_events_source_ip", "security_events", ["source_ip"])
    op.create_index("ix_security_events_destination_ip", "security_events", ["destination_ip"])
    op.create_index("ix_security_events_source_port", "security_events", ["source_port"])
    op.create_index("ix_security_events_destination_port", "security_events", ["destination_port"])
    op.create_index("ix_security_events_protocol", "security_events", ["protocol"])
    op.create_index("ix_security_events_action", "security_events", ["action"])
    op.create_index("ix_security_events_status", "security_events", ["status"])
    op.create_index("ix_security_events_severity", "security_events", ["severity"])
    op.create_index("ix_security_events_domain", "security_events", ["domain"])
    op.create_index("ix_security_events_raw_event_id", "security_events", ["raw_event_id"])
    op.create_index("ix_security_events_dataset_id", "security_events", ["dataset_id"])
    op.create_index("ix_security_events_source_id", "security_events", ["source_id"])

    # 5. log_correlation_rules
    op.create_table(
        "log_correlation_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stable_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="MEDIUM"),
        sa.Column("confidence", sa.String(length=32), nullable=False, server_default="HIGH"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ENABLED"),
        sa.Column("version", sa.String(length=32), nullable=False, server_default="1.0.0"),
        sa.Column("logic", sa.Text(), nullable=False),
        sa.Column("time_window_seconds", sa.Integer(), nullable=False, server_default="300"),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stable_id"),
    )
    op.create_index("ix_log_correlation_rules_id", "log_correlation_rules", ["id"])
    op.create_index("ix_log_correlation_rules_stable_id", "log_correlation_rules", ["stable_id"])
    op.create_index("ix_log_correlation_rules_category", "log_correlation_rules", ["category"])
    op.create_index("ix_log_correlation_rules_status", "log_correlation_rules", ["status"])

    # 6. correlation_alerts
    op.create_table(
        "correlation_alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.String(length=64), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.String(length=32), nullable=False, server_default="HIGH"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="NEW"),
        sa.Column("event_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("source_context", sa.Text(), nullable=True),
        sa.Column("evidence_summary", sa.Text(), nullable=False),
        sa.Column("matched_event_ids", sa.Text(), nullable=True),
        sa.Column("soc_alert_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["security_log_datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_id"], ["log_correlation_rules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alert_id"),
    )
    op.create_index("ix_correlation_alerts_id", "correlation_alerts", ["id"])
    op.create_index("ix_correlation_alerts_alert_id", "correlation_alerts", ["alert_id"])
    op.create_index("ix_correlation_alerts_rule_id", "correlation_alerts", ["rule_id"])
    op.create_index("ix_correlation_alerts_dataset_id", "correlation_alerts", ["dataset_id"])
    op.create_index("ix_correlation_alerts_timestamp", "correlation_alerts", ["timestamp"])
    op.create_index("ix_correlation_alerts_status", "correlation_alerts", ["status"])

    # 7. saved_searches
    op.create_table(
        "saved_searches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("query_definition", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_saved_searches_id", "saved_searches", ["id"])
    op.create_index("ix_saved_searches_owner_id", "saved_searches", ["owner_id"])

    # 8. search_history
    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("query_definition", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_search_history_id", "search_history", ["id"])
    op.create_index("ix_search_history_user_id", "search_history", ["user_id"])
    op.create_index("ix_search_history_timestamp", "search_history", ["timestamp"])

    # 9. siem_lab_scenarios
    op.create_table(
        "siem_lab_scenarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=False, server_default="BEGINNER"),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("objectives", sa.Text(), nullable=False),
        sa.Column("expected_event_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hints", sa.Text(), nullable=True),
        sa.Column("recommended_query", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["security_log_datasets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_siem_lab_scenarios_id", "siem_lab_scenarios", ["id"])
    op.create_index("ix_siem_lab_scenarios_slug", "siem_lab_scenarios", ["slug"])
    op.create_index("ix_siem_lab_scenarios_dataset_id", "siem_lab_scenarios", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("siem_lab_scenarios")
    op.drop_table("search_history")
    op.drop_table("saved_searches")
    op.drop_table("correlation_alerts")
    op.drop_table("log_correlation_rules")
    op.drop_table("security_events")
    op.drop_table("raw_log_events")
    op.drop_table("security_log_datasets")
    op.drop_table("log_sources")
