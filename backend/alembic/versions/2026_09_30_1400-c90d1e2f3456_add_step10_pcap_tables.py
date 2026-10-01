"""Add Step 10 PCAP and Packet Analysis tables: captures, parsed_packets, capture_bookmarks, capture_notes, capture_findings.

Revision ID: c90d1e2f3456
Revises: b89c0d1e2f34
Create Date: 2026-09-30 14:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c90d1e2f3456"
down_revision: str | None = "b89c0d1e2f34"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create captures table
    op.create_table(
        "captures",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("format", sa.String(length=30), nullable=False, server_default="pcap"),
        sa.Column("packet_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="UPLOADED"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("is_sample", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sample_category", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("summary_metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_captures_id"), "captures", ["id"], unique=False)
    op.create_index(op.f("ix_captures_user_id"), "captures", ["user_id"], unique=False)
    op.create_index(op.f("ix_captures_status"), "captures", ["status"], unique=False)
    op.create_index(op.f("ix_captures_is_sample"), "captures", ["is_sample"], unique=False)

    # 2. Create parsed_packets table
    op.create_table(
        "parsed_packets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=False),
        sa.Column("packet_number", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.Float(), nullable=False),
        sa.Column("relative_time", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("captured_length", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("original_length", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("protocol", sa.String(length=30), nullable=False),
        sa.Column("source_mac", sa.String(length=30), nullable=True),
        sa.Column("destination_mac", sa.String(length=30), nullable=True),
        sa.Column("source_ip", sa.String(length=64), nullable=True),
        sa.Column("destination_ip", sa.String(length=64), nullable=True),
        sa.Column("source_port", sa.Integer(), nullable=True),
        sa.Column("destination_port", sa.Integer(), nullable=True),
        sa.Column("transport_protocol", sa.String(length=20), nullable=True),
        sa.Column("application_protocol", sa.String(length=20), nullable=True),
        sa.Column("info", sa.String(length=500), nullable=False),
        sa.Column("tcp_flags", sa.Text(), nullable=True),
        sa.Column("tcp_seq", sa.BigInteger(), nullable=True),
        sa.Column("tcp_ack", sa.BigInteger(), nullable=True),
        sa.Column("layers", sa.Text(), nullable=True),
        sa.Column("layer_details", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parsed_packets_id"), "parsed_packets", ["id"], unique=False)
    op.create_index(op.f("ix_parsed_packets_capture_id"), "parsed_packets", ["capture_id"], unique=False)
    op.create_index(op.f("ix_parsed_packets_packet_number"), "parsed_packets", ["packet_number"], unique=False)
    op.create_index(op.f("ix_parsed_packets_protocol"), "parsed_packets", ["protocol"], unique=False)
    op.create_index(op.f("ix_parsed_packets_source_ip"), "parsed_packets", ["source_ip"], unique=False)
    op.create_index(op.f("ix_parsed_packets_destination_ip"), "parsed_packets", ["destination_ip"], unique=False)
    op.create_index(op.f("ix_parsed_packets_source_port"), "parsed_packets", ["source_port"], unique=False)
    op.create_index(op.f("ix_parsed_packets_destination_port"), "parsed_packets", ["destination_port"], unique=False)

    # 3. Create capture_bookmarks table
    op.create_table(
        "capture_bookmarks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("packet_number", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_capture_bookmarks_id"), "capture_bookmarks", ["id"], unique=False)
    op.create_index(op.f("ix_capture_bookmarks_capture_id"), "capture_bookmarks", ["capture_id"], unique=False)
    op.create_index(op.f("ix_capture_bookmarks_user_id"), "capture_bookmarks", ["user_id"], unique=False)

    # 4. Create capture_notes table
    op.create_table(
        "capture_notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("target_type", sa.String(length=30), nullable=False, server_default="general"),
        sa.Column("target_id", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_capture_notes_id"), "capture_notes", ["id"], unique=False)
    op.create_index(op.f("ix_capture_notes_capture_id"), "capture_notes", ["capture_id"], unique=False)
    op.create_index(op.f("ix_capture_notes_user_id"), "capture_notes", ["user_id"], unique=False)

    # 5. Create capture_findings table
    op.create_table(
        "capture_findings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("capture_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="INFO"),
        sa.Column("evidence_packets", sa.Text(), nullable=True),
        sa.Column("source_endpoint", sa.String(length=100), nullable=True),
        sa.Column("destination_endpoint", sa.String(length=100), nullable=True),
        sa.Column("hypothesis", sa.Text(), nullable=True),
        sa.Column("conclusion", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["capture_id"], ["captures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_capture_findings_id"), "capture_findings", ["id"], unique=False)
    op.create_index(op.f("ix_capture_findings_capture_id"), "capture_findings", ["capture_id"], unique=False)
    op.create_index(op.f("ix_capture_findings_user_id"), "capture_findings", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("capture_findings")
    op.drop_table("capture_notes")
    op.drop_table("capture_bookmarks")
    op.drop_table("parsed_packets")
    op.drop_table("captures")
