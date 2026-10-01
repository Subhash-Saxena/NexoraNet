"""add_step6_question_bank_code_column

Revision ID: e48d3c51b921
Revises: c39f182da410
Create Date: 2026-09-29 23:20:00.000000+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e48d3c51b921"
down_revision: str | None = "c39f182da410"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("questions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("code", sa.String(length=64), nullable=True)
        )
        batch_op.create_index(
            batch_op.f("ix_questions_code"), ["code"], unique=True
        )


def downgrade() -> None:
    with op.batch_alter_table("questions", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_questions_code"))
        batch_op.drop_column("code")
