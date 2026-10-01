"""add_step5_mock_test_engine_schema

Revision ID: c39f182da410
Revises: b28c4e61f092
Create Date: 2026-09-29 22:30:00.000000+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c39f182da410"
down_revision: str | None = "b28c4e61f092"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Extend mock_tests with test_type and instructions
    with op.batch_alter_table("mock_tests", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "test_type",
                sa.String(length=20),
                nullable=False,
                server_default="MIXED",
            )
        )
        batch_op.add_column(
            sa.Column("instructions", sa.Text(), nullable=True)
        )
        batch_op.create_index(
            batch_op.f("ix_mock_tests_test_type"), ["test_type"], unique=False
        )

    # 2. Extend student_answers with is_marked_for_review
    with op.batch_alter_table("student_answers", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_marked_for_review",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    # 3. Extend test_results with total_points, earned_points, passing_percentage, passed
    with op.batch_alter_table("test_results", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "total_points",
                sa.Float(),
                nullable=False,
                server_default=sa.text("0.0"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "earned_points",
                sa.Float(),
                nullable=False,
                server_default=sa.text("0.0"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "passing_percentage",
                sa.Float(),
                nullable=False,
                server_default=sa.text("70.0"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "passed",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("test_results", schema=None) as batch_op:
        batch_op.drop_column("passed")
        batch_op.drop_column("passing_percentage")
        batch_op.drop_column("earned_points")
        batch_op.drop_column("total_points")

    with op.batch_alter_table("student_answers", schema=None) as batch_op:
        batch_op.drop_column("is_marked_for_review")

    with op.batch_alter_table("mock_tests", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_mock_tests_test_type"))
        batch_op.drop_column("instructions")
        batch_op.drop_column("test_type")
