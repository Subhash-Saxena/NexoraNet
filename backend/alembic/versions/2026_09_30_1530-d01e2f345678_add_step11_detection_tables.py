"""Add Step 11 Detection Engine tables: detection_rules, detection_runs, detection_alerts, alert_evidence, alert_notes, alert_status_history.

Revision ID: d01e2f345678
Revises: c90d1e2f3456
Create Date: 2026-09-30 15:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d01e2f345678"
down_revision: str | None = "c90d1e2f3456"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create detection_rules table
    op.create_table(
        "detection_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("confidence_default", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ENABLED"),
        sa.Column("logic_type", sa.String(length=50), nullable=False, server_default="THRESHOLD"),
        sa.Column("conditions", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("time_window_seconds", sa.Integer(), nullable=True),
        sa.Column("mitre_attack_id", sa.String(length=50), nullable=True),
        sa.Column("mitre_technique", sa.String(length=100), nullable=True),
        sa.Column("explanation_template", sa.Text(), nullable=False),
        sa.Column("investigation_guide", sa.Text(), nullable=False),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rule_id"),
    )
    op.create_index(op.f("ix_detection_rules_id"), "detection_rules", ["id"], unique=False)
    op.create_index(op.f("ix_detection_rules_rule_id"), "detection_rules", ["rule_id"], unique=True)
    op.create_index(op.f("ix_detection_rules_category"), "detection_rules", ["category"], unique=False)
    op.create_index(op.f("ix_detection_rules_severity"), "detection_rules", ["severity"], unique=False)
    op.create_index(op.f("ix_detection_rules_status"), "detection_rules", ["status"], unique=False)
    op.create_index(op.f("ix_detection_rules_is_builtin"), "detection_rules", ["is_builtin"], unique=False)

    # 2. Create detection_runs table
    op.create_table(
        "detection_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="PCAP"),
        sa.Column("capture_id", sa.Integer(), nullable=True),
        sa.Column("simulation_scenario_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="QUEUED"),
        sa.Column("rules_evaluated", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("rules_matched", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("alerts_generated", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["simulation_scenario_id"], ["simulator_scenarios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_detection_runs_id"), "detection_runs", ["id"], unique=False)
    op.create_index(op.f("ix_detection_runs_user_id"), "detection_runs", ["user_id"], unique=False)
    op.create_index(op.f("ix_detection_runs_source_type"), "detection_runs", ["source_type"], unique=False)
    op.create_index(op.f("ix_detection_runs_capture_id"), "detection_runs", ["capture_id"], unique=False)
    op.create_index(op.f("ix_detection_runs_simulation_scenario_id"), "detection_runs", ["simulation_scenario_id"], unique=False)
    op.create_index(op.f("ix_detection_runs_status"), "detection_runs", ["status"], unique=False)

    # 3. Create detection_alerts table
    op.create_table(
        "detection_alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="NEW"),
        sa.Column("source_ip", sa.String(length=64), nullable=True),
        sa.Column("source_port", sa.Integer(), nullable=True),
        sa.Column("destination_ip", sa.String(length=64), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=True),
        sa.Column("protocol", sa.String(length=30), nullable=True),
        sa.Column("first_seen_timestamp", sa.Float(), nullable=True),
        sa.Column("last_seen_timestamp", sa.Float(), nullable=True),
        sa.Column("packet_count", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("dedup_key", sa.String(length=255), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("mitre_attack_id", sa.String(length=50), nullable=True),
        sa.Column("mitre_technique", sa.String(length=100), nullable=True),
        sa.Column("investigation_steps", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_id"], ["detection_rules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["detection_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_detection_alerts_id"), "detection_alerts", ["id"], unique=False)
    op.create_index(op.f("ix_detection_alerts_run_id"), "detection_alerts", ["run_id"], unique=False)
    op.create_index(op.f("ix_detection_alerts_rule_id"), "detection_alerts", ["rule_id"], unique=False)
    op.create_index(op.f("ix_detection_alerts_capture_id"), "detection_alerts", ["capture_id"], unique=False)
    op.create_index(op.f("ix_detection_alerts_user_id"), "detection_alerts", ["user_id"], unique=False)
    op.create_index(op.f("ix_detection_alerts_category"), "detection_alerts", ["category"], unique=False)
    op.create_index(op.f("ix_detection_alerts_severity"), "detection_alerts", ["severity"], unique=False)
    op.create_index(op.f("ix_detection_alerts_confidence"), "detection_alerts", ["confidence"], unique=False)
    op.create_index(op.f("ix_detection_alerts_status"), "detection_alerts", ["status"], unique=False)
    op.create_index(op.f("ix_detection_alerts_source_ip"), "detection_alerts", ["source_ip"], unique=False)
    op.create_index(op.f("ix_detection_alerts_destination_ip"), "detection_alerts", ["destination_ip"], unique=False)
    op.create_index(op.f("ix_detection_alerts_dedup_key"), "detection_alerts", ["dedup_key"], unique=False)

    # 4. Create alert_evidence table
    op.create_table(
        "alert_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("evidence_type", sa.String(length=40), nullable=False),
        sa.Column("packet_id", sa.Integer(), nullable=True),
        sa.Column("packet_number", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_data", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["detection_alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["packet_id"], ["parsed_packets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alert_evidence_id"), "alert_evidence", ["id"], unique=False)
    op.create_index(op.f("ix_alert_evidence_alert_id"), "alert_evidence", ["alert_id"], unique=False)
    op.create_index(op.f("ix_alert_evidence_evidence_type"), "alert_evidence", ["evidence_type"], unique=False)
    op.create_index(op.f("ix_alert_evidence_packet_id"), "alert_evidence", ["packet_id"], unique=False)

    # 5. Create alert_notes table
    op.create_table(
        "alert_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["detection_alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alert_notes_id"), "alert_notes", ["id"], unique=False)
    op.create_index(op.f("ix_alert_notes_alert_id"), "alert_notes", ["alert_id"], unique=False)
    op.create_index(op.f("ix_alert_notes_user_id"), "alert_notes", ["user_id"], unique=False)

    # 6. Create alert_status_history table
    op.create_table(
        "alert_status_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("previous_status", sa.String(length=30), nullable=True),
        sa.Column("new_status", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["detection_alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alert_status_history_id"), "alert_status_history", ["id"], unique=False)
    op.create_index(op.f("ix_alert_status_history_alert_id"), "alert_status_history", ["alert_id"], unique=False)
    op.create_index(op.f("ix_alert_status_history_user_id"), "alert_status_history", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("alert_status_history")
    op.drop_table("alert_notes")
    op.drop_table("alert_evidence")
    op.drop_table("detection_alerts")
    op.drop_table("detection_runs")
    op.drop_table("detection_rules")
