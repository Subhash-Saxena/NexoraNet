"""add_step4_lab_engine_schema

Revision ID: b28c4e61f092
Revises: 749a1792479c
Create Date: 2026-09-29 20:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b28c4e61f092"
down_revision: str | None = "749a1792479c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Update labs table
    with op.batch_alter_table("labs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("instructions", sa.Text(), nullable=True))

    # 2. Update lab_steps table
    with op.batch_alter_table("lab_steps", schema=None) as batch_op:
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("points", sa.Integer(), server_default="10", nullable=False)
        )
        batch_op.add_column(
            sa.Column("is_required", sa.Boolean(), server_default="1", nullable=False)
        )

    # 3. Update lab_questions table
    with op.batch_alter_table("lab_questions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("step_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_lab_questions_step_id",
            "lab_steps",
            ["step_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            op.f("ix_lab_questions_step_id"), ["step_id"], unique=False
        )

    # 4. Update lab_attempts table
    with op.batch_alter_table("lab_attempts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("attempt_number", sa.Integer(), server_default="1", nullable=False)
        )
        batch_op.add_column(
            sa.Column("total_points", sa.Float(), server_default="0.0", nullable=False)
        )
        batch_op.add_column(
            sa.Column("percentage", sa.Float(), server_default="0.0", nullable=False)
        )
        batch_op.add_column(
            sa.Column("time_taken_seconds", sa.Integer(), nullable=True)
        )

    # 5. Create lab_step_submissions table
    op.create_table(
        "lab_step_submissions",
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("step_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=True),
        sa.Column("attempt_number", sa.Integer(), server_default="1", nullable=False),
        sa.Column("submitted_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("points_earned", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("hint_used", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"], ["lab_attempts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["step_id"], ["lab_steps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["question_id"], ["lab_questions.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_lab_step_submissions_id"), "lab_step_submissions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_lab_step_submissions_attempt_id"),
        "lab_step_submissions",
        ["attempt_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lab_step_submissions_step_id"),
        "lab_step_submissions",
        ["step_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_lab_step_submissions_question_id"),
        "lab_step_submissions",
        ["question_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_lab_step_submissions_question_id"),
        table_name="lab_step_submissions",
    )
    op.drop_index(
        op.f("ix_lab_step_submissions_step_id"),
        table_name="lab_step_submissions",
    )
    op.drop_index(
        op.f("ix_lab_step_submissions_attempt_id"),
        table_name="lab_step_submissions",
    )
    op.drop_index(
        op.f("ix_lab_step_submissions_id"),
        table_name="lab_step_submissions",
    )
    op.drop_table("lab_step_submissions")

    with op.batch_alter_table("lab_attempts", schema=None) as batch_op:
        batch_op.drop_column("time_taken_seconds")
        batch_op.drop_column("percentage")
        batch_op.drop_column("total_points")
        batch_op.drop_column("attempt_number")

    with op.batch_alter_table("lab_questions", schema=None) as batch_op:
        batch_op.drop_index(op.f("ix_lab_questions_step_id"))
        batch_op.drop_constraint("fk_lab_questions_step_id", type_="foreignkey")
        batch_op.drop_column("step_id")

    with op.batch_alter_table("lab_steps", schema=None) as batch_op:
        batch_op.drop_column("is_required")
        batch_op.drop_column("points")
        batch_op.drop_column("description")

    with op.batch_alter_table("labs", schema=None) as batch_op:
        batch_op.drop_column("instructions")
