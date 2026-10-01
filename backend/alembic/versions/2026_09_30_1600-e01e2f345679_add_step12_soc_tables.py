"""Add Step 12 SOC Dashboard, Investigation, Case Management, and Triage tables.

Revision ID: e01e2f345679
Revises: d01e2f345678
Create Date: 2026-09-30 16:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e01e2f345679"
down_revision: str | None = "d01e2f345678"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Update detection_alerts with Step 12 triage & prioritization fields
    with op.batch_alter_table("detection_alerts") as batch_op:
        batch_op.add_column(
            sa.Column("classification", sa.String(length=30), nullable=False, server_default="UNREVIEWED")
        )
        batch_op.add_column(
            sa.Column("priority", sa.String(length=10), nullable=False, server_default="P3")
        )
        batch_op.add_column(
            sa.Column("assigned_to_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_detection_alerts_assigned_to_id",
            "users",
            ["assigned_to_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_detection_alerts_classification", ["classification"])
        batch_op.create_index("ix_detection_alerts_priority", ["priority"])
        batch_op.create_index("ix_detection_alerts_assigned_to_id", ["assigned_to_id"])

    # 2. Create investigations table
    op.create_table(
        "investigations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("priority", sa.String(length=10), nullable=False, server_default="P3"),
        sa.Column("classification", sa.String(length=30), nullable=False, server_default="UNREVIEWED"),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("assigned_to_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("conclusion", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assigned_to_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("investigation_id"),
    )
    op.create_index("ix_investigations_id", "investigations", ["id"])
    op.create_index("ix_investigations_investigation_id", "investigations", ["investigation_id"], unique=True)
    op.create_index("ix_investigations_status", "investigations", ["status"])
    op.create_index("ix_investigations_priority", "investigations", ["priority"])
    op.create_index("ix_investigations_classification", "investigations", ["classification"])
    op.create_index("ix_investigations_created_by_id", "investigations", ["created_by_id"])
    op.create_index("ix_investigations_assigned_to_id", "investigations", ["assigned_to_id"])

    # 3. Create investigation_alerts association table
    op.create_table(
        "investigation_alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("relationship_type", sa.String(length=30), nullable=False, server_default="PRIMARY"),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alert_id"], ["detection_alerts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigation_alerts_id", "investigation_alerts", ["id"])
    op.create_index("ix_investigation_alerts_investigation_id", "investigation_alerts", ["investigation_id"])
    op.create_index("ix_investigation_alerts_alert_id", "investigation_alerts", ["alert_id"])

    # 4. Create investigation_evidence table
    op.create_table(
        "investigation_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("evidence_type", sa.String(length=40), nullable=False),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("capture_id", sa.Integer(), nullable=True),
        sa.Column("packet_number", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_data", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigation_evidence_id", "investigation_evidence", ["id"])
    op.create_index("ix_investigation_evidence_investigation_id", "investigation_evidence", ["investigation_id"])
    op.create_index("ix_investigation_evidence_evidence_type", "investigation_evidence", ["evidence_type"])
    op.create_index("ix_investigation_evidence_capture_id", "investigation_evidence", ["capture_id"])

    # 5. Create investigation_hypotheses table
    op.create_table(
        "investigation_hypotheses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("hypothesis_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="UNTESTED"),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("supporting_evidence_ids", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigation_hypotheses_id", "investigation_hypotheses", ["id"])
    op.create_index("ix_investigation_hypotheses_investigation_id", "investigation_hypotheses", ["investigation_id"])
    op.create_index("ix_investigation_hypotheses_status", "investigation_hypotheses", ["status"])

    # 6. Create investigation_findings table
    op.create_table(
        "investigation_findings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("evidence_summary", sa.Text(), nullable=True),
        sa.Column("confidence", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigation_findings_id", "investigation_findings", ["id"])
    op.create_index("ix_investigation_findings_investigation_id", "investigation_findings", ["investigation_id"])

    # 7. Create investigation_notes table
    op.create_table(
        "investigation_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigation_notes_id", "investigation_notes", ["id"])
    op.create_index("ix_investigation_notes_investigation_id", "investigation_notes", ["investigation_id"])
    op.create_index("ix_investigation_notes_user_id", "investigation_notes", ["user_id"])

    # 8. Create cases table
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("priority", sa.String(length=10), nullable=False, server_default="P3"),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("assigned_to_id", sa.Integer(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assigned_to_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id"),
    )
    op.create_index("ix_cases_id", "cases", ["id"])
    op.create_index("ix_cases_case_id", "cases", ["case_id"], unique=True)
    op.create_index("ix_cases_status", "cases", ["status"])
    op.create_index("ix_cases_priority", "cases", ["priority"])
    op.create_index("ix_cases_created_by_id", "cases", ["created_by_id"])
    op.create_index("ix_cases_assigned_to_id", "cases", ["assigned_to_id"])

    # 9. Create case_alerts association table
    op.create_table(
        "case_alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["alert_id"], ["detection_alerts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_alerts_id", "case_alerts", ["id"])
    op.create_index("ix_case_alerts_case_id", "case_alerts", ["case_id"])
    op.create_index("ix_case_alerts_alert_id", "case_alerts", ["alert_id"])

    # 10. Create case_investigations association table
    op.create_table(
        "case_investigations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("investigation_id", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_investigations_id", "case_investigations", ["id"])
    op.create_index("ix_case_investigations_case_id", "case_investigations", ["case_id"])
    op.create_index("ix_case_investigations_investigation_id", "case_investigations", ["investigation_id"])

    # 11. Create case_notes table
    op.create_table(
        "case_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_case_notes_id", "case_notes", ["id"])
    op.create_index("ix_case_notes_case_id", "case_notes", ["case_id"])
    op.create_index("ix_case_notes_user_id", "case_notes", ["user_id"])

    # 12. Create soc_audit_logs table
    op.create_table(
        "soc_audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("actor_name", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("object_type", sa.String(length=50), nullable=False),
        sa.Column("object_id", sa.String(length=100), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_soc_audit_logs_id", "soc_audit_logs", ["id"])
    op.create_index("ix_soc_audit_logs_user_id", "soc_audit_logs", ["user_id"])
    op.create_index("ix_soc_audit_logs_action", "soc_audit_logs", ["action"])
    op.create_index("ix_soc_audit_logs_object_type", "soc_audit_logs", ["object_type"])
    op.create_index("ix_soc_audit_logs_object_id", "soc_audit_logs", ["object_id"])

    # 13. Create soc_notifications table
    op.create_table(
        "soc_notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_soc_notifications_id", "soc_notifications", ["id"])
    op.create_index("ix_soc_notifications_user_id", "soc_notifications", ["user_id"])
    op.create_index("ix_soc_notifications_notification_type", "soc_notifications", ["notification_type"])
    op.create_index("ix_soc_notifications_is_read", "soc_notifications", ["is_read"])

    # 14. Create soc_challenges table
    op.create_table(
        "soc_challenges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("scenario_type", sa.String(length=50), nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=30), nullable=False, server_default="INTERMEDIATE"),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("expected_observations", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("rubric_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_soc_challenges_id", "soc_challenges", ["id"])
    op.create_index("ix_soc_challenges_slug", "soc_challenges", ["slug"], unique=True)
    op.create_index("ix_soc_challenges_scenario_type", "soc_challenges", ["scenario_type"])
    op.create_index("ix_soc_challenges_capture_id", "soc_challenges", ["capture_id"])

    # 15. Create soc_challenge_attempts table
    op.create_table(
        "soc_challenge_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("investigation_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="IN_PROGRESS"),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("score_breakdown", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("feedback", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["challenge_id"], ["soc_challenges.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_soc_challenge_attempts_id", "soc_challenge_attempts", ["id"])
    op.create_index("ix_soc_challenge_attempts_challenge_id", "soc_challenge_attempts", ["challenge_id"])
    op.create_index("ix_soc_challenge_attempts_user_id", "soc_challenge_attempts", ["user_id"])
    op.create_index("ix_soc_challenge_attempts_investigation_id", "soc_challenge_attempts", ["investigation_id"])


def downgrade() -> None:
    op.drop_table("soc_challenge_attempts")
    op.drop_table("soc_challenges")
    op.drop_table("soc_notifications")
    op.drop_table("soc_audit_logs")
    op.drop_table("case_notes")
    op.drop_table("case_investigations")
    op.drop_table("case_alerts")
    op.drop_table("cases")
    op.drop_table("investigation_notes")
    op.drop_table("investigation_findings")
    op.drop_table("investigation_hypotheses")
    op.drop_table("investigation_evidence")
    op.drop_table("investigation_alerts")
    op.drop_table("investigations")

    with op.batch_alter_table("detection_alerts") as batch_op:
        batch_op.drop_index("ix_detection_alerts_assigned_to_id")
        batch_op.drop_index("ix_detection_alerts_priority")
        batch_op.drop_index("ix_detection_alerts_classification")
        batch_op.drop_constraint("fk_detection_alerts_assigned_to_id", type_="foreignkey")
        batch_op.drop_column("assigned_to_id")
        batch_op.drop_column("priority")
        batch_op.drop_column("classification")
