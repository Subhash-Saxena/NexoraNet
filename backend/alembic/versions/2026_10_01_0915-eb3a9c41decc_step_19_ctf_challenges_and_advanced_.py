"""step_19_ctf_challenges_and_advanced_training

Revision ID: eb3a9c41decc
Revises: ca2d83e1cdbb
Create Date: 2026-10-01 09:15:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'eb3a9c41decc'
down_revision: str | None = 'ca2d83e1cdbb'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. challenges
    op.create_table(
        'challenges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('difficulty', sa.String(length=32), nullable=False),
        sa.Column('challenge_type', sa.String(length=64), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scenario', sa.Text(), nullable=False),
        sa.Column('learning_objectives', sa.Text(), nullable=False),
        sa.Column('prerequisites', sa.Text(), nullable=False),
        sa.Column('environment_description', sa.Text(), nullable=False),
        sa.Column('tasks_json', sa.Text(), nullable=False),
        sa.Column('skills_tested_json', sa.Text(), nullable=False),
        sa.Column('related_lesson_slug', sa.String(length=128), nullable=True),
        sa.Column('related_lab_slug', sa.String(length=128), nullable=True),
        sa.Column('related_mitre_technique', sa.String(length=64), nullable=True),
        sa.Column('flag_hash', sa.String(length=255), nullable=False),
        sa.Column('flag_salt', sa.String(length=64), nullable=False),
        sa.Column('flag_format', sa.String(length=64), nullable=False),
        sa.Column('validation_type', sa.String(length=32), nullable=False),
        sa.Column('solution_explanation', sa.Text(), nullable=False),
        sa.Column('common_mistakes', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_multi_stage', sa.Boolean(), nullable=False),
        sa.Column('simulation_only', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenges_id'), 'challenges', ['id'], unique=False)
    op.create_index(op.f('ix_challenges_challenge_id'), 'challenges', ['challenge_id'], unique=True)
    op.create_index(op.f('ix_challenges_category'), 'challenges', ['category'], unique=False)
    op.create_index(op.f('ix_challenges_difficulty'), 'challenges', ['difficulty'], unique=False)

    # 2. challenge_stages
    op.create_table(
        'challenge_stages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('stage_order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('tasks_json', sa.Text(), nullable=False),
        sa.Column('flag_hash', sa.String(length=255), nullable=False),
        sa.Column('flag_salt', sa.String(length=64), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('is_terminal', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenge_stages_id'), 'challenge_stages', ['id'], unique=False)
    op.create_index(op.f('ix_challenge_stages_challenge_id'), 'challenge_stages', ['challenge_id'], unique=False)

    # 3. challenge_hints
    op.create_table(
        'challenge_hints',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('hint_number', sa.Integer(), nullable=False),
        sa.Column('hint_text', sa.Text(), nullable=False),
        sa.Column('penalty_percent', sa.Float(), nullable=False),
        sa.Column('penalty_points', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenge_hints_id'), 'challenge_hints', ['id'], unique=False)
    op.create_index(op.f('ix_challenge_hints_challenge_id'), 'challenge_hints', ['challenge_id'], unique=False)

    # 4. challenge_evidence
    op.create_table(
        'challenge_evidence',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('evidence_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('content_json', sa.Text(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenge_evidence_id'), 'challenge_evidence', ['id'], unique=False)
    op.create_index(op.f('ix_challenge_evidence_challenge_id'), 'challenge_evidence', ['challenge_id'], unique=False)

    # 5. challenge_attempts
    op.create_table(
        'challenge_attempts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('attempt_id', sa.String(length=64), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('current_stage_order', sa.Integer(), nullable=False),
        sa.Column('stage_progress_json', sa.Text(), nullable=False),
        sa.Column('hints_unlocked', sa.Integer(), nullable=False),
        sa.Column('hints_penalty', sa.Float(), nullable=False),
        sa.Column('attempts_count', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), nullable=False),
        sa.Column('solved', sa.Boolean(), nullable=False),
        sa.Column('revealed_solution', sa.Boolean(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenge_attempts_id'), 'challenge_attempts', ['id'], unique=False)
    op.create_index(op.f('ix_challenge_attempts_attempt_id'), 'challenge_attempts', ['attempt_id'], unique=True)
    op.create_index(op.f('ix_challenge_attempts_challenge_id'), 'challenge_attempts', ['challenge_id'], unique=False)
    op.create_index(op.f('ix_challenge_attempts_user_id'), 'challenge_attempts', ['user_id'], unique=False)

    # 6. challenge_submissions
    op.create_table(
        'challenge_submissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('attempt_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('submitted_flag', sa.String(length=255), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('points_awarded', sa.Float(), nullable=False),
        sa.Column('feedback', sa.String(length=255), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['attempt_id'], ['challenge_attempts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenge_submissions_id'), 'challenge_submissions', ['id'], unique=False)
    op.create_index(op.f('ix_challenge_submissions_attempt_id'), 'challenge_submissions', ['attempt_id'], unique=False)
    op.create_index(op.f('ix_challenge_submissions_challenge_id'), 'challenge_submissions', ['challenge_id'], unique=False)
    op.create_index(op.f('ix_challenge_submissions_user_id'), 'challenge_submissions', ['user_id'], unique=False)

    # 7. challenge_tracks
    op.create_table(
        'challenge_tracks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('track_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('target_role', sa.String(length=128), nullable=False),
        sa.Column('difficulty', sa.String(length=32), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('badge_name', sa.String(length=128), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenge_tracks_id'), 'challenge_tracks', ['id'], unique=False)
    op.create_index(op.f('ix_challenge_tracks_track_id'), 'challenge_tracks', ['track_id'], unique=True)

    # 8. challenge_track_items
    op.create_table(
        'challenge_track_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('track_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['track_id'], ['challenge_tracks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenge_track_items_id'), 'challenge_track_items', ['id'], unique=False)
    op.create_index(op.f('ix_challenge_track_items_track_id'), 'challenge_track_items', ['track_id'], unique=False)
    op.create_index(op.f('ix_challenge_track_items_challenge_id'), 'challenge_track_items', ['challenge_id'], unique=False)


def downgrade() -> None:
    op.drop_table('challenge_track_items')
    op.drop_table('challenge_tracks')
    op.drop_table('challenge_submissions')
    op.drop_table('challenge_attempts')
    op.drop_table('challenge_evidence')
    op.drop_table('challenge_hints')
    op.drop_table('challenge_stages')
    op.drop_table('challenges')
