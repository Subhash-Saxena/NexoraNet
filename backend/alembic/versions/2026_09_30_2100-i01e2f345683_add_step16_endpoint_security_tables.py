"""Add Step 16 Endpoint Security & Host Investigation Engine tables.

Revision ID: i01e2f345683
Revises: h01e2f345682
Create Date: 2026-09-30 21:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "i01e2f345683"
down_revision: str | None = "h01e2f345682"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. endpoint_hosts
    op.create_table(
        "endpoint_hosts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stable_id", sa.String(length=64), nullable=False),
        sa.Column("hostname", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=64), nullable=False, server_default="WINDOWS"),
        sa.Column("platform_version", sa.String(length=128), nullable=False),
        sa.Column("architecture", sa.String(length=32), nullable=False, server_default="X64"),
        sa.Column("environment", sa.String(length=64), nullable=False, server_default="WORKSTATION"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ONLINE"),
        sa.Column("risk_level", sa.String(length=32), nullable=False, server_default="LOW"),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("mac_address", sa.String(length=32), nullable=True),
        sa.Column("os_build", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hostname"),
        sa.UniqueConstraint("stable_id"),
    )
    op.create_index("ix_endpoint_hosts_id", "endpoint_hosts", ["id"])
    op.create_index("ix_endpoint_hosts_stable_id", "endpoint_hosts", ["stable_id"])
    op.create_index("ix_endpoint_hosts_hostname", "endpoint_hosts", ["hostname"])
    op.create_index("ix_endpoint_hosts_platform", "endpoint_hosts", ["platform"])
    op.create_index("ix_endpoint_hosts_environment", "endpoint_hosts", ["environment"])
    op.create_index("ix_endpoint_hosts_status", "endpoint_hosts", ["status"])
    op.create_index("ix_endpoint_hosts_risk_level", "endpoint_hosts", ["risk_level"])

    # 2. endpoint_events
    op.create_table(
        "endpoint_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_category", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=True),
        sa.Column("process_name", sa.String(length=255), nullable=True),
        sa.Column("process_id", sa.Integer(), nullable=True),
        sa.Column("parent_process_id", sa.Integer(), nullable=True),
        sa.Column("parent_process_name", sa.String(length=255), nullable=True),
        sa.Column("command_summary", sa.String(length=1000), nullable=True),
        sa.Column("integrity_level", sa.String(length=32), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_path", sa.String(length=1000), nullable=True),
        sa.Column("file_hash", sa.String(length=128), nullable=True),
        sa.Column("file_action", sa.String(length=32), nullable=True),
        sa.Column("source_ip", sa.String(length=45), nullable=True),
        sa.Column("source_port", sa.Integer(), nullable=True),
        sa.Column("destination_ip", sa.String(length=45), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=True),
        sa.Column("protocol", sa.String(length=32), nullable=True),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("dns_query_type", sa.String(length=32), nullable=True),
        sa.Column("dns_response", sa.String(length=255), nullable=True),
        sa.Column("service_name", sa.String(length=128), nullable=True),
        sa.Column("service_display_name", sa.String(length=255), nullable=True),
        sa.Column("service_action", sa.String(length=64), nullable=True),
        sa.Column("persistence_type", sa.String(length=64), nullable=True),
        sa.Column("auth_method", sa.String(length=64), nullable=True),
        sa.Column("auth_failure_reason", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=True),
        sa.Column("result", sa.String(length=64), nullable=True),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="INFO"),
        sa.Column("raw_event_reference", sa.String(length=128), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["endpoint_hosts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_endpoint_events_id", "endpoint_events", ["id"])
    op.create_index("ix_endpoint_events_event_id", "endpoint_events", ["event_id"])
    op.create_index("ix_endpoint_events_host_id", "endpoint_events", ["host_id"])
    op.create_index("ix_endpoint_events_timestamp", "endpoint_events", ["timestamp"])
    op.create_index("ix_endpoint_events_event_type", "endpoint_events", ["event_type"])
    op.create_index("ix_endpoint_events_event_category", "endpoint_events", ["event_category"])
    op.create_index("ix_endpoint_events_username", "endpoint_events", ["username"])
    op.create_index("ix_endpoint_events_process_name", "endpoint_events", ["process_name"])
    op.create_index("ix_endpoint_events_process_id", "endpoint_events", ["process_id"])
    op.create_index("ix_endpoint_events_parent_process_id", "endpoint_events", ["parent_process_id"])
    op.create_index("ix_endpoint_events_source_ip", "endpoint_events", ["source_ip"])
    op.create_index("ix_endpoint_events_destination_ip", "endpoint_events", ["destination_ip"])
    op.create_index("ix_endpoint_events_destination_port", "endpoint_events", ["destination_port"])
    op.create_index("ix_endpoint_events_domain", "endpoint_events", ["domain"])
    op.create_index("ix_endpoint_events_file_name", "endpoint_events", ["file_name"])
    op.create_index("ix_endpoint_events_file_hash", "endpoint_events", ["file_hash"])
    op.create_index("ix_endpoint_events_result", "endpoint_events", ["result"])
    op.create_index("ix_endpoint_events_severity", "endpoint_events", ["severity"])

    # 3. endpoint_investigations
    op.create_table(
        "endpoint_investigations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stable_id", sa.String(length=64), nullable=False),
        sa.Column("host_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="P2"),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scenario_slug", sa.String(length=128), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["endpoint_hosts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stable_id"),
    )
    op.create_index("ix_endpoint_investigations_id", "endpoint_investigations", ["id"])
    op.create_index("ix_endpoint_investigations_stable_id", "endpoint_investigations", ["stable_id"])
    op.create_index("ix_endpoint_investigations_host_id", "endpoint_investigations", ["host_id"])
    op.create_index("ix_endpoint_investigations_user_id", "endpoint_investigations", ["user_id"])
    op.create_index("ix_endpoint_investigations_status", "endpoint_investigations", ["status"])
    op.create_index("ix_endpoint_investigations_priority", "endpoint_investigations", ["priority"])
    op.create_index("ix_endpoint_investigations_scenario_slug", "endpoint_investigations", ["scenario_slug"])

    # 4. endpoint_hypotheses
    op.create_table(
        "endpoint_hypotheses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="OPEN"),
        sa.Column("confidence", sa.String(length=32), nullable=False, server_default="MEDIUM"),
        sa.Column("analyst_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["endpoint_investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_endpoint_hypotheses_id", "endpoint_hypotheses", ["id"])
    op.create_index("ix_endpoint_hypotheses_investigation_id", "endpoint_hypotheses", ["investigation_id"])
    op.create_index("ix_endpoint_hypotheses_status", "endpoint_hypotheses", ["status"])

    # 5. endpoint_evidence
    op.create_table(
        "endpoint_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("hypothesis_id", sa.Integer(), nullable=True),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("evidence_type", sa.String(length=64), nullable=False, server_default="EVENT"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("relevance", sa.String(length=32), nullable=False, server_default="SUPPORTING"),
        sa.Column("artifact_data_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["endpoint_events.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["hypothesis_id"], ["endpoint_hypotheses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["investigation_id"], ["endpoint_investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_endpoint_evidence_id", "endpoint_evidence", ["id"])
    op.create_index("ix_endpoint_evidence_investigation_id", "endpoint_evidence", ["investigation_id"])
    op.create_index("ix_endpoint_evidence_hypothesis_id", "endpoint_evidence", ["hypothesis_id"])
    op.create_index("ix_endpoint_evidence_event_id", "endpoint_evidence", ["event_id"])
    op.create_index("ix_endpoint_evidence_evidence_type", "endpoint_evidence", ["evidence_type"])
    op.create_index("ix_endpoint_evidence_relevance", "endpoint_evidence", ["relevance"])

    # 6. endpoint_findings
    op.create_table(
        "endpoint_findings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("mitre_attack_id", sa.String(length=64), nullable=True),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="MEDIUM"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["endpoint_investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_endpoint_findings_id", "endpoint_findings", ["id"])
    op.create_index("ix_endpoint_findings_investigation_id", "endpoint_findings", ["investigation_id"])

    # 7. endpoint_conclusions
    op.create_table(
        "endpoint_conclusions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("verdict", sa.String(length=64), nullable=False, server_default="BENIGN_ANOMALY"),
        sa.Column("training_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score_breakdown_json", sa.Text(), nullable=True),
        sa.Column("lessons_learned", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["endpoint_investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("investigation_id"),
    )
    op.create_index("ix_endpoint_conclusions_id", "endpoint_conclusions", ["id"])
    op.create_index("ix_endpoint_conclusions_investigation_id", "endpoint_conclusions", ["investigation_id"])
    op.create_index("ix_endpoint_conclusions_verdict", "endpoint_conclusions", ["verdict"])

    # 8. endpoint_scenarios
    op.create_table(
        "endpoint_scenarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scenario_id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=False, server_default="BEGINNER"),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("target_host_stable_id", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("background", sa.Text(), nullable=False),
        sa.Column("objectives_json", sa.Text(), nullable=False),
        sa.Column("hints_json", sa.Text(), nullable=False),
        sa.Column("solution_rubric_json", sa.Text(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scenario_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_endpoint_scenarios_id", "endpoint_scenarios", ["id"])
    op.create_index("ix_endpoint_scenarios_scenario_id", "endpoint_scenarios", ["scenario_id"])
    op.create_index("ix_endpoint_scenarios_slug", "endpoint_scenarios", ["slug"])
    op.create_index("ix_endpoint_scenarios_difficulty", "endpoint_scenarios", ["difficulty"])


def downgrade() -> None:
    op.drop_table("endpoint_scenarios")
    op.drop_table("endpoint_conclusions")
    op.drop_table("endpoint_findings")
    op.drop_table("endpoint_evidence")
    op.drop_table("endpoint_hypotheses")
    op.drop_table("endpoint_investigations")
    op.drop_table("endpoint_events")
    op.drop_table("endpoint_hosts")
