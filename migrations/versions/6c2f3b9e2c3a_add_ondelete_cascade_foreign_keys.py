"""Add ON DELETE CASCADE to foreign keys

Revision ID: 6c2f3b9e2c3a
Revises: 79d198a977d5
Create Date: 2025-11-11 16:19:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6c2f3b9e2c3a'
down_revision: Union[str, Sequence[str], None] = '79d198a977d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ON DELETE CASCADE to FK constraints."""
    # features.saas_info_id -> saas_info.id
    op.drop_constraint('features_saas_info_id_fkey', 'features', type_='foreignkey')
    op.create_foreign_key(
        'features_saas_info_id_fkey',
        source_table='features',
        referent_table='saas_info',
        local_cols=['saas_info_id'],
        remote_cols=['id'],
        ondelete='CASCADE',
    )

    # pricing_plans.saas_info_id -> saas_info.id
    op.drop_constraint('pricing_plans_saas_info_id_fkey', 'pricing_plans', type_='foreignkey')
    op.create_foreign_key(
        'pricing_plans_saas_info_id_fkey',
        source_table='pricing_plans',
        referent_table='saas_info',
        local_cols=['saas_info_id'],
        remote_cols=['id'],
        ondelete='CASCADE',
    )

    # leads.saas_info_id -> saas_info.id
    op.drop_constraint('leads_saas_info_id_fkey', 'leads', type_='foreignkey')
    op.create_foreign_key(
        'leads_saas_info_id_fkey',
        source_table='leads',
        referent_table='saas_info',
        local_cols=['saas_info_id'],
        remote_cols=['id'],
        ondelete='CASCADE',
    )

    # reddit_posts.lead_id -> leads.id
    op.drop_constraint('reddit_posts_lead_id_fkey', 'reddit_posts', type_='foreignkey')
    op.create_foreign_key(
        'reddit_posts_lead_id_fkey',
        source_table='reddit_posts',
        referent_table='leads',
        local_cols=['lead_id'],
        remote_cols=['id'],
        ondelete='CASCADE',
    )

    # reddit_comments.reddit_post_db_id -> reddit_posts.id
    op.drop_constraint('reddit_comments_reddit_post_db_id_fkey', 'reddit_comments', type_='foreignkey')
    op.create_foreign_key(
        'reddit_comments_reddit_post_db_id_fkey',
        source_table='reddit_comments',
        referent_table='reddit_posts',
        local_cols=['reddit_post_db_id'],
        remote_cols=['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    """Revert ON DELETE CASCADE from FK constraints."""
    op.drop_constraint('reddit_comments_reddit_post_db_id_fkey', 'reddit_comments', type_='foreignkey')
    op.create_foreign_key(
        'reddit_comments_reddit_post_db_id_fkey',
        source_table='reddit_comments',
        referent_table='reddit_posts',
        local_cols=['reddit_post_db_id'],
        remote_cols=['id'],
    )

    op.drop_constraint('reddit_posts_lead_id_fkey', 'reddit_posts', type_='foreignkey')
    op.create_foreign_key(
        'reddit_posts_lead_id_fkey',
        source_table='reddit_posts',
        referent_table='leads',
        local_cols=['lead_id'],
        remote_cols=['id'],
    )

    op.drop_constraint('leads_saas_info_id_fkey', 'leads', type_='foreignkey')
    op.create_foreign_key(
        'leads_saas_info_id_fkey',
        source_table='leads',
        referent_table='saas_info',
        local_cols=['saas_info_id'],
        remote_cols=['id'],
    )

    op.drop_constraint('pricing_plans_saas_info_id_fkey', 'pricing_plans', type_='foreignkey')
    op.create_foreign_key(
        'pricing_plans_saas_info_id_fkey',
        source_table='pricing_plans',
        referent_table='saas_info',
        local_cols=['saas_info_id'],
        remote_cols=['id'],
    )

    op.drop_constraint('features_saas_info_id_fkey', 'features', type_='foreignkey')
    op.create_foreign_key(
        'features_saas_info_id_fkey',
        source_table='features',
        referent_table='saas_info',
        local_cols=['saas_info_id'],
        remote_cols=['id'],
    )

