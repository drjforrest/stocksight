from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21816d8c715f'
down_revision = 'fe394cb06589'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Existing auto-generated constraints
    op.drop_constraint('fk_dividend_history_symbol_company_info', 'dividend_history', type_='foreignkey')
    op.create_foreign_key(op.f('fk_dividend_history_symbol_company_info'), 'dividend_history', 'company_info', ['symbol'], ['symbol'], source_schema='stocksight', referent_schema='stocksight')
    op.drop_constraint('fk_stock_splits_symbol_company_info', 'stock_splits', type_='foreignkey')
    op.create_foreign_key(op.f('fk_stock_splits_symbol_company_info'), 'stock_splits', 'company_info', ['symbol'], ['symbol'], source_schema='stocksight', referent_schema='stocksight')

    # Manually add competitors table
    op.create_table(
        'competitors',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('symbol', sa.String(10), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('market_cap', sa.BigInteger),
        sa.Column('revenue', sa.Numeric(15,2)),
        sa.Column('net_income', sa.Numeric(15,2)),
        sa.Column('pe_ratio', sa.Numeric(10,2)),
        sa.Column('sector', sa.String(100)),
        sa.Column('industry', sa.String(255)),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # Manually add ipo_listings table
    op.create_table(
        'ipo_listings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('symbol', sa.String(10), nullable=False, unique=True),
        sa.Column('exchange', sa.String(50), nullable=False),
        sa.Column('filing_date', sa.Date),
        sa.Column('ipo_date', sa.Date),
        sa.Column('offer_price', sa.Numeric(10,2)),
        sa.Column('total_shares_offered', sa.BigInteger),
        sa.Column('valuation', sa.Numeric(20,2)),
        sa.Column('lockup_period_end', sa.Date),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Drop manually added tables
    op.drop_table('competitors')
    op.drop_table('ipo_listings')

    # Existing auto-generated foreign key constraints
    op.drop_constraint(op.f('fk_stock_splits_symbol_company_info'), 'stock_splits', schema='stocksight', type_='foreignkey')
    op.create_foreign_key('fk_stock_splits_symbol_company_info', 'stock_splits', 'company_info', ['symbol'], ['symbol'])
    op.drop_constraint(op.f('fk_dividend_history_symbol_company_info'), 'dividend_history', schema='stocksight', type_='foreignkey')
    op.create_foreign_key('fk_dividend_history_symbol_company_info', 'dividend_history', 'company_info', ['symbol'], ['symbol'])
    # ### end Alembic commands ###
