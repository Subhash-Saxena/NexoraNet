"""add step7 mock test catalog columns

Revision ID: f19a8b2c4e33
Revises: e48d3c51b921
Create Date: 2026-09-30 09:05:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f19a8b2c4e33"
down_revision: str | None = "e48d3c51b921"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("mock_tests", schema=None) as batch_op:
        batch_op.add_column(sa.Column("code", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("blueprint_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("prerequisites", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("tags", sa.String(length=255), nullable=True))
        batch_op.create_index(batch_op.f("ix_mock_tests_code"), ["code"], unique=True)
        batch_op.create_index(batch_op.f("ix_mock_tests_blueprint_id"), ["blueprint_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_mock_tests_blueprint_id",
            "test_blueprints",
            ["blueprint_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("mock_tests", schema=None) as batch_op:
        batch_op.drop_constraint("fk_mock_tests_blueprint_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_mock_tests_blueprint_id"))
        batch_op.drop_index(batch_op.f("ix_mock_tests_code"))
        batch_op.drop_column("tags")
        batch_op.drop_column("prerequisites")
        batch_op.drop_column("blueprint_id")
        batch_op.drop_column("code")
