-- Database Migration Script for StockSight
-- Adds tables for competitor analysis and IPO tracking

-- Competitor Table: Stores financial data of biotech competitors
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    market_cap BIGINT,
    revenue DECIMAL(15,2),
    net_income DECIMAL(15,2),
    pe_ratio DECIMAL(10,2),
    sector VARCHAR(100),
    industry VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- IPO Table: Stores IPO details for biotech sector
CREATE TABLE ipo_listings (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    exchange VARCHAR(50) NOT NULL,
    filing_date DATE,
    ipo_date DATE,
    offer_price DECIMAL(10,2),
    total_shares_offered BIGINT,
    valuation DECIMAL(20,2),
    lockup_period_end DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX idx_competitors_symbol ON competitors(symbol);
CREATE INDEX idx_ipo_symbol ON ipo_listings(symbol);
