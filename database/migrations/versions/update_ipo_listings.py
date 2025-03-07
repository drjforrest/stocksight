"""Update ipo_listings table with missing columns

Revision ID: update_ipo_listings
Revises: enhance_biotech_schema
Create Date: 2024-03-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_ipo_listings'
down_revision = 'enhance_biotech_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing columns to ipo_listings table."""
    # Add new columns
    op.add_column('ipo_listings',
        sa.Column('expected_date', sa.DateTime),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('price_range_low', sa.Float),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('price_range_high', sa.Float),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('shares_offered', sa.Integer),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('initial_valuation', sa.Float),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('lead_underwriters', sa.String),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('status', sa.String),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('therapeutic_area', sa.String),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('pipeline_stage', sa.String),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('primary_indication', sa.String),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('use_of_proceeds', sa.String),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('lock_up_period_days', sa.Integer),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('quiet_period_end_date', sa.DateTime),
        schema='stocksight'
    )
    op.add_column('ipo_listings',
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()'), nullable=False),
        schema='stocksight'
    )

    # Add indexes
    op.create_index(
        'idx_ipo_listings_filing_date',
        'ipo_listings',
        ['filing_date'],
        schema='stocksight'
    )
    op.create_index(
        'idx_ipo_listings_expected_date',
        'ipo_listings',
        ['expected_date'],
        schema='stocksight'
    )
    op.create_index(
        'idx_ipo_listings_status',
        'ipo_listings',
        ['status'],
        schema='stocksight'
    )
    op.create_index(
        'idx_ipo_listings_therapeutic_area',
        'ipo_listings',
        ['therapeutic_area'],
        schema='stocksight'
    )


def downgrade() -> None:
    """Remove added columns from ipo_listings table."""
    # Drop indexes
    op.drop_index('idx_ipo_listings_filing_date', table_name='ipo_listings', schema='stocksight')
    op.drop_index('idx_ipo_listings_expected_date', table_name='ipo_listings', schema='stocksight')
    op.drop_index('idx_ipo_listings_status', table_name='ipo_listings', schema='stocksight')
    op.drop_index('idx_ipo_listings_therapeutic_area', table_name='ipo_listings', schema='stocksight')

    # Drop columns
    op.drop_column('ipo_listings', 'expected_date', schema='stocksight')
    op.drop_column('ipo_listings', 'price_range_low', schema='stocksight')
    op.drop_column('ipo_listings', 'price_range_high', schema='stocksight')
    op.drop_column('ipo_listings', 'shares_offered', schema='stocksight')
    op.drop_column('ipo_listings', 'initial_valuation', schema='stocksight')
    op.drop_column('ipo_listings', 'lead_underwriters', schema='stocksight')
    op.drop_column('ipo_listings', 'status', schema='stocksight')
    op.drop_column('ipo_listings', 'therapeutic_area', schema='stocksight')
    op.drop_column('ipo_listings', 'pipeline_stage', schema='stocksight')
    op.drop_column('ipo_listings', 'primary_indication', schema='stocksight')
    op.drop_column('ipo_listings', 'use_of_proceeds', schema='stocksight')
    op.drop_column('ipo_listings', 'lock_up_period_days', schema='stocksight')
    op.drop_column('ipo_listings', 'quiet_period_end_date', schema='stocksight')
    op.drop_column('ipo_listings', 'updated_at', schema='stocksight') 