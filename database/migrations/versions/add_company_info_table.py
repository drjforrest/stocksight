"""add company info table

Revision ID: add_company_info_table
Revises: enhance_biotech_schema
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'add_company_info_table'
down_revision = 'enhance_biotech_schema'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Check if the table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names(schema='stocksight')
    
    if 'company_info' not in tables:
        op.create_table(
            'company_info',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('symbol', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('exchange', sa.String(), nullable=True),
            sa.Column('market_cap', sa.Float(), nullable=True),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('therapeutic_area', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            schema='stocksight'
        )
        
        # Add indexes
        op.create_index(op.f('ix_company_info_id'), 'company_info', ['id'], unique=False, schema='stocksight')
        op.create_index(op.f('ix_company_info_symbol'), 'company_info', ['symbol'], unique=True, schema='stocksight')
    else:
        # Check for missing columns and add them if needed
        existing_columns = {col['name'] for col in inspector.get_columns('company_info', schema='stocksight')}
        
        if 'therapeutic_area' not in existing_columns:
            op.add_column('company_info', sa.Column('therapeutic_area', sa.String(), nullable=True), schema='stocksight')
        
        if 'created_at' not in existing_columns:
            op.add_column('company_info', 
                         sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                         schema='stocksight')
        
        if 'updated_at' not in existing_columns:
            op.add_column('company_info',
                         sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                         schema='stocksight')

def downgrade() -> None:
    # We don't want to drop the table in downgrade since it existed before
    # Just remove any columns we added
    try:
        op.drop_column('company_info', 'therapeutic_area', schema='stocksight')
        op.drop_column('company_info', 'created_at', schema='stocksight')
        op.drop_column('company_info', 'updated_at', schema='stocksight')
    except Exception:
        pass  # Ignore errors if columns don't exist 