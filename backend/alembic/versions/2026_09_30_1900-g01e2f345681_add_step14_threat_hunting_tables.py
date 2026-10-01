"""Add Step 14 Threat Hunting and Investigation tables.

Revision ID: g01e2f345681
Revises: f01e2f345680
Create Date: 2026-09-30 19:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "g01e2f345681"
down_revision: str | None = "f01e2f345680"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. hunt_datasets
    op.create_table(
        "hunt_datasets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dataset_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("dataset_type", sa.String(length=50), nullable=False, server_default="PCAP"),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("event_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="READY"),
        sa.Column("time_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dataset_id"),
    )
    op.create_index("ix_hunt_datasets_id", "hunt_datasets", ["id"])
    op.create_index("ix_hunt_datasets_dataset_id", "hunt_datasets", ["dataset_id"])
    op.create_index("ix_hunt_datasets_dataset_type", "hunt_datasets", ["dataset_type"])
    op.create_index("ix_hunt_datasets_status", "hunt_datasets", ["status"])

    # 2. hunt_events
    op.create_table(
        "hunt_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("dataset_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_ip", sa.String(length=45), nullable=True),
        sa.Column("destination_ip", sa.String(length=45), nullable=True),
        sa.Column("source_port", sa.Integer(), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=True),
        sa.Column("protocol", sa.String(length=20), nullable=True),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("url", sa.String(length=1024), nullable=True),
        sa.Column("ioc_id", sa.Integer(), nullable=True),
        sa.Column("alert_id", sa.Integer(), nullable=True),
        sa.Column("soc_alert_id", sa.Integer(), nullable=True),
        sa.Column("pcap_capture_id", sa.Integer(), nullable=True),
        sa.Column("pcap_packet_number", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("summary", sa.String(length=500), nullable=True),
        sa.Column("payload_preview", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["hunt_datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ioc_id"], ["indicators.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["alert_id"], ["detection_alerts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["soc_alert_id"], ["investigation_alerts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["pcap_capture_id"], ["captures.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_hunt_events_id", "hunt_events", ["id"])
    op.create_index("ix_hunt_events_event_id", "hunt_events", ["event_id"])
    op.create_index("ix_hunt_events_dataset_id", "hunt_events", ["dataset_id"])
    op.create_index("ix_hunt_events_event_type", "hunt_events", ["event_type"])
    op.create_index("ix_hunt_events_timestamp", "hunt_events", ["timestamp"])
    op.create_index("ix_hunt_events_source_ip", "hunt_events", ["source_ip"])
    op.create_index("ix_hunt_events_destination_ip", "hunt_events", ["destination_ip"])
    op.create_index("ix_hunt_events_source_port", "hunt_events", ["source_port"])
    op.create_index("ix_hunt_events_destination_port", "hunt_events", ["destination_port"])
    op.create_index("ix_hunt_events_protocol", "hunt_events", ["protocol"])
    op.create_index("ix_hunt_events_domain", "hunt_events", ["domain"])
    op.create_index("ix_hunt_events_ioc_id", "hunt_events", ["ioc_id"])
    op.create_index("ix_hunt_events_alert_id", "hunt_events", ["alert_id"])
    op.create_index("ix_hunt_events_soc_alert_id", "hunt_events", ["soc_alert_id"])
    op.create_index("ix_hunt_events_pcap_capture_id", "hunt_events", ["pcap_capture_id"])
    op.create_index("ix_hunt_events_pcap_packet_number", "hunt_events", ["pcap_packet_number"])
    op.create_index("ix_hunt_events_severity", "hunt_events", ["severity"])

    # 3. threat_hunts
    op.create_table(
        "threat_hunts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hunt_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="DRAFT"),
        sa.Column("difficulty", sa.String(length=20), nullable=False, server_default="BEGINNER"),
        sa.Column("dataset_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scenario_slug", sa.String(length=100), nullable=True),
        sa.Column("initial_pivot_type", sa.String(length=50), nullable=True),
        sa.Column("initial_pivot_value", sa.String(length=255), nullable=True),
        sa.Column("query_history", sa.Text(), nullable=True),
        sa.Column("conclusion", sa.Text(), nullable=True),
        sa.Column("conclusion_disposition", sa.String(length=30), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("score_breakdown", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["hunt_datasets.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hunt_id"),
    )
    op.create_index("ix_threat_hunts_id", "threat_hunts", ["id"])
    op.create_index("ix_threat_hunts_hunt_id", "threat_hunts", ["hunt_id"])
    op.create_index("ix_threat_hunts_status", "threat_hunts", ["status"])
    op.create_index("ix_threat_hunts_difficulty", "threat_hunts", ["difficulty"])
    op.create_index("ix_threat_hunts_dataset_id", "threat_hunts", ["dataset_id"])
    op.create_index("ix_threat_hunts_user_id", "threat_hunts", ["user_id"])
    op.create_index("ix_threat_hunts_scenario_slug", "threat_hunts", ["scenario_slug"])

    # 4. threat_hunt_hypotheses
    op.create_table(
        "threat_hunt_hypotheses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hunt_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("confidence", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("analyst_reasoning", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["hunt_id"], ["threat_hunts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_hunt_hypotheses_id", "threat_hunt_hypotheses", ["id"])
    op.create_index("ix_threat_hunt_hypotheses_hunt_id", "threat_hunt_hypotheses", ["hunt_id"])
    op.create_index("ix_threat_hunt_hypotheses_status", "threat_hunt_hypotheses", ["status"])

    # 5. threat_hunt_evidence
    op.create_table(
        "threat_hunt_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hunt_id", sa.Integer(), nullable=False),
        sa.Column("hypothesis_id", sa.Integer(), nullable=True),
        sa.Column("evidence_type", sa.String(length=30), nullable=False, server_default="EVENT"),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("relevance", sa.String(length=20), nullable=False, server_default="SUPPORTING"),
        sa.Column("analyst_note", sa.Text(), nullable=True),
        sa.Column("data_snapshot", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["hunt_id"], ["threat_hunts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hypothesis_id"], ["threat_hunt_hypotheses.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_hunt_evidence_id", "threat_hunt_evidence", ["id"])
    op.create_index("ix_threat_hunt_evidence_hunt_id", "threat_hunt_evidence", ["hunt_id"])
    op.create_index("ix_threat_hunt_evidence_hypothesis_id", "threat_hunt_evidence", ["hypothesis_id"])
    op.create_index("ix_threat_hunt_evidence_evidence_type", "threat_hunt_evidence", ["evidence_type"])
    op.create_index("ix_threat_hunt_evidence_source_id", "threat_hunt_evidence", ["source_id"])
    op.create_index("ix_threat_hunt_evidence_relevance", "threat_hunt_evidence", ["relevance"])

    # 6. threat_hunt_findings
    op.create_table(
        "threat_hunt_findings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hunt_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("finding_type", sa.String(length=30), nullable=False, server_default="OBSERVATION"),
        sa.Column("confidence", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mitigation_recommendation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["hunt_id"], ["threat_hunts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_hunt_findings_id", "threat_hunt_findings", ["id"])
    op.create_index("ix_threat_hunt_findings_hunt_id", "threat_hunt_findings", ["hunt_id"])
    op.create_index("ix_threat_hunt_findings_finding_type", "threat_hunt_findings", ["finding_type"])

    # 7. threat_hunt_notes
    op.create_table(
        "threat_hunt_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hunt_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("author_name", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("related_event_id", sa.String(length=64), nullable=True),
        sa.Column("related_alert_id", sa.Integer(), nullable=True),
        sa.Column("related_ioc_id", sa.Integer(), nullable=True),
        sa.Column("related_hypothesis_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["hunt_id"], ["threat_hunts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_threat_hunt_notes_id", "threat_hunt_notes", ["id"])
    op.create_index("ix_threat_hunt_notes_hunt_id", "threat_hunt_notes", ["hunt_id"])
    op.create_index("ix_threat_hunt_notes_user_id", "threat_hunt_notes", ["user_id"])
    op.create_index("ix_threat_hunt_notes_related_event_id", "threat_hunt_notes", ["related_event_id"])
    op.create_index("ix_threat_hunt_notes_related_alert_id", "threat_hunt_notes", ["related_alert_id"])
    op.create_index("ix_threat_hunt_notes_related_ioc_id", "threat_hunt_notes", ["related_ioc_id"])
    op.create_index("ix_threat_hunt_notes_related_hypothesis_id", "threat_hunt_notes", ["related_hypothesis_id"])


def downgrade() -> None:
    op.drop_table("threat_hunt_notes")
    op.drop_table("threat_hunt_findings")
    op.drop_table("threat_hunt_evidence")
    op.drop_table("threat_hunt_hypotheses")
    op.drop_table("threat_hunts")
    op.drop_table("hunt_events")
    op.drop_table("hunt_datasets")
