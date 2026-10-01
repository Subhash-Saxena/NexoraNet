"""Add Step 9 Network Simulator tables: simulator_topologies, simulator_scenarios, simulator_scenario_attempts.

Revision ID: b89c0d1e2f34
Revises: a78b9c1d2e3f
Create Date: 2026-09-30 10:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b89c0d1e2f34"
down_revision: str | None = "a78b9c1d2e3f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create simulator_topologies table
    op.create_table(
        "simulator_topologies",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(length=20), nullable=False, server_default="BEGINNER"),
        sa.Column("is_prebuilt", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("topology_data", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_simulator_topologies_id"), "simulator_topologies", ["id"], unique=False)
    op.create_index(op.f("ix_simulator_topologies_slug"), "simulator_topologies", ["slug"], unique=True)
    op.create_index(op.f("ix_simulator_topologies_user_id"), "simulator_topologies", ["user_id"], unique=False)

    # 2. Create simulator_scenarios table
    op.create_table(
        "simulator_scenarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False, server_default="BEGINNER"),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="FUNDAMENTALS"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("learning_objectives", sa.Text(), nullable=True),
        sa.Column("initial_topology", sa.Text(), nullable=True),
        sa.Column("tasks", sa.Text(), nullable=True),
        sa.Column("validation_rules", sa.Text(), nullable=True),
        sa.Column("hints", sa.Text(), nullable=True),
        sa.Column("solution_explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_simulator_scenarios_id"), "simulator_scenarios", ["id"], unique=False)
    op.create_index(op.f("ix_simulator_scenarios_slug"), "simulator_scenarios", ["slug"], unique=True)

    # 3. Create simulator_scenario_attempts table
    op.create_table(
        "simulator_scenario_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("scenario_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="IN_PROGRESS"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hints_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("validation_results", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["scenario_id"], ["simulator_scenarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_simulator_scenario_attempts_id"), "simulator_scenario_attempts", ["id"], unique=False)
    op.create_index(op.f("ix_simulator_scenario_attempts_scenario_id"), "simulator_scenario_attempts", ["scenario_id"], unique=False)
    op.create_index(op.f("ix_simulator_scenario_attempts_user_id"), "simulator_scenario_attempts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_simulator_scenario_attempts_user_id"), table_name="simulator_scenario_attempts")
    op.drop_index(op.f("ix_simulator_scenario_attempts_scenario_id"), table_name="simulator_scenario_attempts")
    op.drop_index(op.f("ix_simulator_scenario_attempts_id"), table_name="simulator_scenario_attempts")
    op.drop_table("simulator_scenario_attempts")

    op.drop_index(op.f("ix_simulator_scenarios_slug"), table_name="simulator_scenarios")
    op.drop_index(op.f("ix_simulator_scenarios_id"), table_name="simulator_scenarios")
    op.drop_table("simulator_scenarios")

    op.drop_index(op.f("ix_simulator_topologies_user_id"), table_name="simulator_topologies")
    op.drop_index(op.f("ix_simulator_topologies_slug"), table_name="simulator_topologies")
    op.drop_index(op.f("ix_simulator_topologies_id"), table_name="simulator_topologies")
    op.drop_table("simulator_topologies")
