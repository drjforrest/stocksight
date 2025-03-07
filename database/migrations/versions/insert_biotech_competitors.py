"""Insert initial biotech competitor data

Revision ID: insert_biotech_competitors
Revises: 21816d8c715f
Create Date: 2024-03-20
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'insert_biotech_competitors'
down_revision = '21816d8c715f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Insert initial biotech competitor data."""
    competitors_table = sa.table('competitors',
        sa.column('symbol', sa.String),
        sa.column('name', sa.String),
        sa.column('therapeutic_area', sa.String),
        sa.column('pipeline_stage', sa.String),
        sa.column('updated_at', sa.DateTime)
    )

    # Insert competitor data
    op.bulk_insert(competitors_table, [
        {
            'symbol': 'BIIB',
            'name': 'Biogen',
            'therapeutic_area': 'Neurology',
            'pipeline_stage': 'FDA Approved',
            'updated_at': datetime.now()
        },
        {
            'symbol': 'REGN',
            'name': 'Regeneron Pharmaceuticals',
            'therapeutic_area': 'Immunology',
            'pipeline_stage': 'FDA Approved',
            'updated_at': datetime.now()
        },
        {
            'symbol': 'VRTX',
            'name': 'Vertex Pharmaceuticals',
            'therapeutic_area': 'Rare Diseases',
            'pipeline_stage': 'FDA Approved',
            'updated_at': datetime.now()
        },
        {
            'symbol': 'CRSP',
            'name': 'CRISPR Therapeutics',
            'therapeutic_area': 'Gene Editing',
            'pipeline_stage': 'Phase 3',
            'updated_at': datetime.now()
        },
        {
            'symbol': 'EDIT',
            'name': 'Editas Medicine',
            'therapeutic_area': 'Gene Editing',
            'pipeline_stage': 'Phase 2',
            'updated_at': datetime.now()
        }
    ])


def downgrade() -> None:
    """Remove inserted biotech competitor data."""
    op.execute("""
        DELETE FROM competitors 
        WHERE symbol IN ('BIIB', 'REGN', 'VRTX', 'CRSP', 'EDIT')
    """)