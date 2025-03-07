-- StockSight Database Maintenance Script
-- Run this as a database administrator to perform maintenance tasks

-- 1. Schema Cleanup
-- Backup public schema tables if they exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'stock_prices') THEN
        CREATE TABLE IF NOT EXISTS public.stock_prices_backup AS 
        SELECT * FROM public.stock_prices;
        
        -- Log the backup
        RAISE NOTICE 'Backed up public.stock_prices to public.stock_prices_backup';
    END IF;
END$$;

-- Drop duplicate tables from public schema
DROP TABLE IF EXISTS public.stock_prices;

-- 2. Schema Verification
-- Ensure stocksight schema exists
CREATE SCHEMA IF NOT EXISTS stocksight;

-- 3. Permissions
-- Grant necessary permissions to application user
DO $$
BEGIN
    EXECUTE format(
        'GRANT USAGE ON SCHEMA stocksight TO %I',
        current_user
    );
    EXECUTE format(
        'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA stocksight TO %I',
        current_user
    );
    EXECUTE format(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA stocksight GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO %I',
        current_user
    );
END$$;

-- 4. Index Verification
-- Ensure primary key indexes exist
DO $$
BEGIN
    -- company_info
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'stocksight' AND tablename = 'company_info' AND indexdef LIKE '%company_info_pkey%') THEN
        ALTER TABLE stocksight.company_info ADD PRIMARY KEY (id);
    END IF;
    
    -- stock_prices
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'stocksight' AND tablename = 'stock_prices' AND indexdef LIKE '%stock_prices_pkey%') THEN
        ALTER TABLE stocksight.stock_prices ADD PRIMARY KEY (id);
    END IF;
END$$;

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_company_info_symbol ON stocksight.company_info(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stocksight.stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stocksight.stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_clinical_trials_company_id ON stocksight.clinical_trials(company_id);
CREATE INDEX IF NOT EXISTS idx_competitors_company_id ON stocksight.competitors(company_id);
CREATE INDEX IF NOT EXISTS idx_ipo_listings_symbol ON stocksight.ipo_listings(symbol);

-- 5. Foreign Key Verification
-- Add any missing foreign keys
DO $$
BEGIN
    -- clinical_trials -> company_info
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_schema = 'stocksight' 
        AND table_name = 'clinical_trials' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name = 'fk_clinical_trials_company'
    ) THEN
        ALTER TABLE stocksight.clinical_trials
        ADD CONSTRAINT fk_clinical_trials_company
        FOREIGN KEY (company_id) REFERENCES stocksight.company_info(id);
    END IF;
    
    -- competitors -> company_info
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_schema = 'stocksight' 
        AND table_name = 'competitors' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name = 'fk_competitors_company'
    ) THEN
        ALTER TABLE stocksight.competitors
        ADD CONSTRAINT fk_competitors_company
        FOREIGN KEY (company_id) REFERENCES stocksight.company_info(id);
    END IF;
END$$;

-- 6. Table Optimization
-- Update table statistics
ANALYZE stocksight.company_info;
ANALYZE stocksight.stock_prices;
ANALYZE stocksight.clinical_trials;
ANALYZE stocksight.competitors;
ANALYZE stocksight.ipo_listings;

-- 7. Cleanup old data (optional, uncomment if needed)
-- DELETE FROM stocksight.stock_prices WHERE date < NOW() - INTERVAL '5 years';
-- DELETE FROM stocksight.clinical_trials WHERE updated_at < NOW() - INTERVAL '2 years';

-- 8. Add updated_at triggers
CREATE OR REPLACE FUNCTION stocksight.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DO $$
BEGIN
    -- company_info
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_at_company_info') THEN
        CREATE TRIGGER set_updated_at_company_info
            BEFORE UPDATE ON stocksight.company_info
            FOR EACH ROW
            EXECUTE FUNCTION stocksight.update_updated_at_column();
    END IF;
    
    -- clinical_trials
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_at_clinical_trials') THEN
        CREATE TRIGGER set_updated_at_clinical_trials
            BEFORE UPDATE ON stocksight.clinical_trials
            FOR EACH ROW
            EXECUTE FUNCTION stocksight.update_updated_at_column();
    END IF;
END$$;

-- 9. Verify all tables are in the correct schema
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;

-- 10. Show table sizes and index usage
SELECT
    schemaname || '.' || tablename as table_full_name,
    pg_size_pretty(pg_total_relation_size('"' || schemaname || '"."' || tablename || '"')) as total_size,
    pg_size_pretty(pg_relation_size('"' || schemaname || '"."' || tablename || '"')) as table_size,
    pg_size_pretty(pg_total_relation_size('"' || schemaname || '"."' || tablename || '"') - 
                  pg_relation_size('"' || schemaname || '"."' || tablename || '"')) as index_size
FROM pg_tables
WHERE schemaname = 'stocksight'
ORDER BY pg_total_relation_size('"' || schemaname || '"."' || tablename || '"') DESC; 