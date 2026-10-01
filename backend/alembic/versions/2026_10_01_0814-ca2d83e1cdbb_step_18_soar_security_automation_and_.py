"""step_18_soar_security_automation_and_soc_scenarios

Revision ID: ca2d83e1cdbb
Revises: 71031b25909d
Create Date: 2026-10-01 08:14:17.629026

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ca2d83e1cdbb'
down_revision: str | None = '71031b25909d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. automation_audit_logs
    op.create_table(
        'automation_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.String(length=100), nullable=False),
        sa.Column('previous_state', sa.String(length=50), nullable=True),
        sa.Column('new_state', sa.String(length=50), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('simulation_only', sa.Boolean(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_automation_audit_logs_execution_id'), 'automation_audit_logs', ['execution_id'], unique=False)
    op.create_index(op.f('ix_automation_audit_logs_id'), 'automation_audit_logs', ['id'], unique=False)

    # 2. automation_playbooks
    op.create_table(
        'automation_playbooks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('playbook_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('trigger_type', sa.String(length=50), nullable=False),
        sa.Column('trigger_filter_json', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('requires_approval', sa.Boolean(), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('simulation_only', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_automation_playbooks_category'), 'automation_playbooks', ['category'], unique=False)
    op.create_index(op.f('ix_automation_playbooks_id'), 'automation_playbooks', ['id'], unique=False)
    op.create_index(op.f('ix_automation_playbooks_playbook_id'), 'automation_playbooks', ['playbook_id'], unique=True)
    op.create_index(op.f('ix_automation_playbooks_status'), 'automation_playbooks', ['status'], unique=False)
    op.create_index(op.f('ix_automation_playbooks_trigger_type'), 'automation_playbooks', ['trigger_type'], unique=False)

    # 3. soc_scenarios
    op.create_table(
        'soc_scenarios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('scenario_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('learning_objectives', sa.Text(), nullable=False),
        sa.Column('initial_signal_json', sa.Text(), nullable=False),
        sa.Column('available_evidence_json', sa.Text(), nullable=False),
        sa.Column('correlation_targets_json', sa.Text(), nullable=False),
        sa.Column('hypotheses_options_json', sa.Text(), nullable=False),
        sa.Column('mitre_techniques_json', sa.Text(), nullable=False),
        sa.Column('response_options_json', sa.Text(), nullable=False),
        sa.Column('scoring_rubric_json', sa.Text(), nullable=False),
        sa.Column('hints_json', sa.Text(), nullable=False),
        sa.Column('solution_explanation', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_soc_scenarios_category'), 'soc_scenarios', ['category'], unique=False)
    op.create_index(op.f('ix_soc_scenarios_difficulty'), 'soc_scenarios', ['difficulty'], unique=False)
    op.create_index(op.f('ix_soc_scenarios_id'), 'soc_scenarios', ['id'], unique=False)
    op.create_index(op.f('ix_soc_scenarios_scenario_id'), 'soc_scenarios', ['scenario_id'], unique=True)

    # 4. automation_steps
    op.create_table(
        'automation_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('playbook_id', sa.Integer(), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('parameters_json', sa.Text(), nullable=True),
        sa.Column('condition_json', sa.Text(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=False),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('on_failure', sa.String(length=20), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['playbook_id'], ['automation_playbooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_automation_steps_id'), 'automation_steps', ['id'], unique=False)
    op.create_index(op.f('ix_automation_steps_playbook_id'), 'automation_steps', ['playbook_id'], unique=False)

    # 5. playbook_executions
    op.create_table(
        'playbook_executions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.String(length=50), nullable=False),
        sa.Column('playbook_id', sa.Integer(), nullable=False),
        sa.Column('trigger_source', sa.String(length=50), nullable=False),
        sa.Column('source_id', sa.String(length=100), nullable=False),
        sa.Column('idempotency_key', sa.String(length=150), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('current_step_order', sa.Integer(), nullable=False),
        sa.Column('total_steps', sa.Integer(), nullable=False),
        sa.Column('requested_by', sa.String(length=100), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approval_status', sa.String(length=20), nullable=True),
        sa.Column('approval_reason', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('simulation_only', sa.Boolean(), nullable=False),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('artifacts_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['playbook_id'], ['automation_playbooks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playbook_executions_execution_id'), 'playbook_executions', ['execution_id'], unique=True)
    op.create_index(op.f('ix_playbook_executions_id'), 'playbook_executions', ['id'], unique=False)
    op.create_index(op.f('ix_playbook_executions_idempotency_key'), 'playbook_executions', ['idempotency_key'], unique=True)
    op.create_index(op.f('ix_playbook_executions_playbook_id'), 'playbook_executions', ['playbook_id'], unique=False)
    op.create_index(op.f('ix_playbook_executions_source_id'), 'playbook_executions', ['source_id'], unique=False)
    op.create_index(op.f('ix_playbook_executions_status'), 'playbook_executions', ['status'], unique=False)

    # 6. scenario_attempts
    op.create_table(
        'scenario_attempts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('attempt_id', sa.String(length=50), nullable=False),
        sa.Column('scenario_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('current_stage', sa.String(length=50), nullable=False),
        sa.Column('stage_data_json', sa.Text(), nullable=False),
        sa.Column('hints_used', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('score_breakdown_json', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['scenario_id'], ['soc_scenarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenario_attempts_attempt_id'), 'scenario_attempts', ['attempt_id'], unique=True)
    op.create_index(op.f('ix_scenario_attempts_id'), 'scenario_attempts', ['id'], unique=False)
    op.create_index(op.f('ix_scenario_attempts_scenario_id'), 'scenario_attempts', ['scenario_id'], unique=False)
    op.create_index(op.f('ix_scenario_attempts_status'), 'scenario_attempts', ['status'], unique=False)
    op.create_index(op.f('ix_scenario_attempts_user_id'), 'scenario_attempts', ['user_id'], unique=False)

    # 7. execution_step_logs
    op.create_table(
        'execution_step_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('execution_id', sa.Integer(), nullable=False),
        sa.Column('step_id', sa.Integer(), nullable=True),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(length=255), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('input_summary', sa.Text(), nullable=True),
        sa.Column('output_summary', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_attempt', sa.Integer(), nullable=False),
        sa.Column('simulation_only', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['execution_id'], ['playbook_executions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['step_id'], ['automation_steps.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_execution_step_logs_execution_id'), 'execution_step_logs', ['execution_id'], unique=False)
    op.create_index(op.f('ix_execution_step_logs_id'), 'execution_step_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('execution_step_logs')
    op.drop_table('scenario_attempts')
    op.drop_table('playbook_executions')
    op.drop_table('automation_steps')
    op.drop_table('soc_scenarios')
    op.drop_table('automation_playbooks')
    op.drop_table('automation_audit_logs')
