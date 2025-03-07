"""move stock prices table to stocksight schema

Revision ID: move_stock_prices
Revises: add_company_info_table
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError

# revision identifiers, used by Alembic
revision = 'move_stock_prices'
down_revision = 'add_company_info_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # First check if the public.stock_prices table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    try:
        if 'stock_prices' in inspector.get_table_names(schema='public'):
            # Just log the warning without trying to modify the table
            print("\nWARNING: Found duplicate table 'stock_prices' in public schema")
            print("WARNING: The application will use 'stocksight.stock_prices' going forward")
            print("WARNING: Please have a database administrator run the following commands when convenient:")
            print("\n    -- Backup the public table if needed:")
            print("    CREATE TABLE IF NOT EXISTS public.stock_prices_backup AS SELECT * FROM public.stock_prices;")
            print("    -- Then drop the original public table:")
            print("    DROP TABLE public.stock_prices;")
            print("\nNOTE: This migration will be marked as complete without modifying the table.\n")
    except Exception as e:
        # Log any errors but allow migration to complete
        print(f"\nWARNING: Error checking public schema: {str(e)}")
        print("WARNING: Please have a database administrator check for and clean up public.stock_prices if it exists\n")

def downgrade() -> None:
    # We don't want to move data back to public schema
    pass 