"""Enhance biotech schema with therapeutic areas and clinical trials

Revision ID: enhance_biotech_schema
Revises: ff21e9c24c9c
Create Date: 2024-03-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'enhance_biotech_schema'
down_revision = 'ff21e9c24c9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Enhance schema with therapeutic areas and clinical trials."""
    # Create therapeutic areas table
    op.create_table(
        'therapeutic_areas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='stocksight'
    )
    op.create_index(
        'idx_therapeutic_area_name',
        'therapeutic_areas',
        ['name'],
        unique=True,
        schema='stocksight'
    )

    # Create clinical trials table
    op.create_table(
        'clinical_trials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_symbol', sa.String(10), nullable=False),
        sa.Column('trial_id', sa.String(50), nullable=False),
        sa.Column('phase', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('therapeutic_area_id', sa.Integer()),
        sa.Column('start_date', sa.Date()),
        sa.Column('estimated_completion_date', sa.Date()),
        sa.Column('drug_name', sa.String(255)),
        sa.Column('indication', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trial_id'),
        sa.ForeignKeyConstraint(
            ['company_symbol'],
            ['stocksight.company_info.symbol'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['therapeutic_area_id'],
            ['stocksight.therapeutic_areas.id'],
            ondelete='SET NULL'
        ),
        sa.CheckConstraint('phase BETWEEN 1 AND 4', name='check_valid_phase'),
        schema='stocksight'
    )
    op.create_index(
        'idx_clinical_trials_company',
        'clinical_trials',
        ['company_symbol'],
        schema='stocksight'
    )
    op.create_index(
        'idx_clinical_trials_phase',
        'clinical_trials',
        ['phase'],
        schema='stocksight'
    )

    # Add competitor scoring fields to competitors table
    op.add_column('competitors',
        sa.Column('volatility', sa.Float()),
        schema='stocksight'
    )
    op.add_column('competitors',
        sa.Column('ipo_performance', sa.Float()),
        schema='stocksight'
    )
    op.add_column('competitors',
        sa.Column('patent_count', sa.Integer()),
        schema='stocksight'
    )

    # Add therapeutic_area_id to competitors table
    op.add_column('competitors',
        sa.Column('therapeutic_area_id', sa.Integer()),
        schema='stocksight'
    )
    op.create_foreign_key(
        'fk_competitors_therapeutic_area',
        'competitors',
        'therapeutic_areas',
        ['therapeutic_area_id'],
        ['id'],
        source_schema='stocksight',
        referent_schema='stocksight',
        ondelete='SET NULL'
    )

    # Create IPO updates table
    op.create_table(
        'ipo_updates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ipo_id', sa.Integer(), nullable=False),
        sa.Column('update_type', sa.String(50), nullable=False),
        sa.Column('update_date', sa.TIMESTAMP(), nullable=False),
        sa.Column('previous_value', sa.Text()),
        sa.Column('new_value', sa.Text()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['ipo_id'],
            ['stocksight.ipo_listings.id'],
            ondelete='CASCADE'
        ),
        schema='stocksight'
    )
    op.create_index(
        'idx_ipo_updates_date',
        'ipo_updates',
        ['update_date'],
        schema='stocksight'
    )


def downgrade() -> None:
    """Remove therapeutic areas and clinical trials enhancements."""
    # Drop IPO updates table
    op.drop_table('ipo_updates', schema='stocksight')

    # Remove competitor scoring fields and foreign key
    op.drop_constraint(
        'fk_competitors_therapeutic_area',
        'competitors',
        schema='stocksight',
        type_='foreignkey'
    )
    op.drop_column('competitors', 'therapeutic_area_id', schema='stocksight')
    op.drop_column('competitors', 'volatility', schema='stocksight')
    op.drop_column('competitors', 'ipo_performance', schema='stocksight')
    op.drop_column('competitors', 'patent_count', schema='stocksight')

    # Drop clinical trials table
    op.drop_table('clinical_trials', schema='stocksight')

    # Drop therapeutic areas table
    op.drop_table('therapeutic_areas', schema='stocksight') 