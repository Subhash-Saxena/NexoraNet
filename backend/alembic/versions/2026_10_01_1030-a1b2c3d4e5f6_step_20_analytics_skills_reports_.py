"""step_20_analytics_skills_reports_portfolio_admin

Revision ID: a1b2c3d4e5f6
Revises: eb3a9c41decc
Create Date: 2026-10-01 10:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: str | None = 'eb3a9c41decc'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. skills
    op.create_table(
        'skills',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('skill_code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('related_topics', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_skills_skill_code'), 'skills', ['skill_code'], unique=True)
    op.create_index(op.f('ix_skills_category'), 'skills', ['category'], unique=False)

    # 2. skill_assessments
    op.create_table(
        'skill_assessments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('exposure', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_activities', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('accuracy', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('completion_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('recent_performance', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('practical_activity_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('confidence', sa.String(length=32), nullable=False, server_default='NOT_ENOUGH_DATA'),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('evidence_breakdown', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'skill_id', name='uq_user_skill_assessment'),
    )
    op.create_index(op.f('ix_skill_assessments_user_id'), 'skill_assessments', ['user_id'], unique=False)
    op.create_index(op.f('ix_skill_assessments_skill_id'), 'skill_assessments', ['skill_id'], unique=False)

    # 3. learning_activities
    op.create_table(
        'learning_activities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=64), nullable=False),
        sa.Column('reference_id', sa.String(length=128), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('points_earned', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='COMPLETED'),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_learning_activities_user_id'), 'learning_activities', ['user_id'], unique=False)
    op.create_index(op.f('ix_learning_activities_activity_type'), 'learning_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_learning_activities_reference_id'), 'learning_activities', ['reference_id'], unique=False)
    op.create_index(op.f('ix_learning_activities_occurred_at'), 'learning_activities', ['occurred_at'], unique=False)

    # 4. student_recommendations
    op.create_table(
        'student_recommendations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('target_url', sa.String(length=255), nullable=False),
        sa.Column('priority', sa.String(length=16), nullable=False, server_default='MEDIUM'),
        sa.Column('is_dismissed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_student_recommendations_user_id'), 'student_recommendations', ['user_id'], unique=False)

    # 5. achievements
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('badge_icon', sa.String(length=64), nullable=False),
        sa.Column('criteria_description', sa.Text(), nullable=False),
        sa.Column('required_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('target_type', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_achievements_code'), 'achievements', ['code'], unique=True)

    # 6. user_achievements
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('progress_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_unlocked', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    op.create_index(op.f('ix_user_achievements_user_id'), 'user_achievements', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_achievements_achievement_id'), 'user_achievements', ['achievement_id'], unique=False)

    # 7. portfolios
    op.create_table(
        'portfolios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('public_slug', sa.String(length=64), nullable=False),
        sa.Column('visibility', sa.String(length=32), nullable=False, server_default='PRIVATE'),
        sa.Column('display_name', sa.String(length=128), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('learning_focus', sa.String(length=128), nullable=True),
        sa.Column('social_links', sa.JSON(), nullable=False),
        sa.Column('show_stats', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('show_skills', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('show_certifications', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('no_index', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_portfolios_user_id'), 'portfolios', ['user_id'], unique=True)
    op.create_index(op.f('ix_portfolios_public_slug'), 'portfolios', ['public_slug'], unique=True)

    # 8. portfolio_projects
    op.create_table(
        'portfolio_projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('technologies', sa.JSON(), nullable=False),
        sa.Column('skills', sa.JSON(), nullable=False),
        sa.Column('learning_outcome', sa.Text(), nullable=False),
        sa.Column('repository_url', sa.String(length=512), nullable=True),
        sa.Column('demo_url', sa.String(length=512), nullable=True),
        sa.Column('completed_date', sa.String(length=32), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_portfolio_projects_portfolio_id'), 'portfolio_projects', ['portfolio_id'], unique=False)

    # 9. portfolio_items
    op.create_table(
        'portfolio_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(length=64), nullable=False),
        sa.Column('reference_id', sa.String(length=128), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('skills_demonstrated', sa.JSON(), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_portfolio_items_portfolio_id'), 'portfolio_items', ['portfolio_id'], unique=False)

    # 10. assessment_reports
    op.create_table(
        'assessment_reports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('report_uuid', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('learning_period', sa.String(length=128), nullable=False),
        sa.Column('summary_json', sa.JSON(), nullable=False),
        sa.Column('disclaimer', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_assessment_reports_report_uuid'), 'assessment_reports', ['report_uuid'], unique=True)
    op.create_index(op.f('ix_assessment_reports_user_id'), 'assessment_reports', ['user_id'], unique=False)

    # 11. educational_certificates
    op.create_table(
        'educational_certificates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('certificate_uuid', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_or_module_title', sa.String(length=255), nullable=False),
        sa.Column('course_or_module_slug', sa.String(length=128), nullable=False),
        sa.Column('student_name', sa.String(length=128), nullable=False),
        sa.Column('verification_code', sa.String(length=64), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('disclaimer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_educational_certificates_certificate_uuid'), 'educational_certificates', ['certificate_uuid'], unique=True)
    op.create_index(op.f('ix_educational_certificates_user_id'), 'educational_certificates', ['user_id'], unique=False)
    op.create_index(op.f('ix_educational_certificates_verification_code'), 'educational_certificates', ['verification_code'], unique=True)

    # 12. admin_audit_logs
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_username', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('target_type', sa.String(length=64), nullable=False),
        sa.Column('target_id', sa.String(length=128), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_admin_audit_logs_actor_username'), 'admin_audit_logs', ['actor_username'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_action'), 'admin_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_target_type'), 'admin_audit_logs', ['target_type'], unique=False)
    op.create_index(op.f('ix_admin_audit_logs_created_at'), 'admin_audit_logs', ['created_at'], unique=False)

    # 13. content_versions
    op.create_table(
        'content_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('content_type', sa.String(length=64), nullable=False),
        sa.Column('content_id', sa.String(length=128), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='PUBLISHED'),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('published_by', sa.String(length=64), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_content_versions_content_type'), 'content_versions', ['content_type'], unique=False)
    op.create_index(op.f('ix_content_versions_content_id'), 'content_versions', ['content_id'], unique=False)


def downgrade() -> None:
    op.drop_table('content_versions')
    op.drop_table('admin_audit_logs')
    op.drop_table('educational_certificates')
    op.drop_table('assessment_reports')
    op.drop_table('portfolio_items')
    op.drop_table('portfolio_projects')
    op.drop_table('portfolios')
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('student_recommendations')
    op.drop_table('learning_activities')
    op.drop_table('skill_assessments')
    op.drop_table('skills')
