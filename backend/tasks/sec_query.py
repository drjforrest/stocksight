import asyncio
import os
from datetime import datetime
import httpx
import asyncpg
from typing import List, Dict, Any

# Database Connection
DB_URL = os.getenv("DATABASE_URL", "postgresql://stocksight_user:stocksight_password@localhost/stocksight")

# API Keys
SEC_API_URL = "https://www.sec.gov/some-endpoint"  # Replace with actual SEC API URL
FDA_API_URL = "https://api.fda.gov/drug/drugsfda.json"  # Replace with actual FDA API URL

# Market Cap Filters (in USD)
MARKET_CAP_MIN = 50_000_000  # $50M minimum to include nano-caps
TRADING_VOLUME_MIN = 100_000  # Avoid low-liquidity stocks
EXCHANGES_ALLOWED = {"NASDAQ", "NYSE"}  # Focus on major biotech exchanges


async def fetch_sec_companies() -> List[Dict[str, Any]]:
    """Fetch biotech companies from the SEC API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(SEC_API_URL)
        response.raise_for_status()
        return response.json()["companies"]  # Adjust based on API response


async def fetch_fda_trials() -> Dict[str, Dict[str, Any]]:
    """Fetch biotech clinical trial data from the FDA API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(FDA_API_URL, params={"limit": 1000})
        response.raise_for_status()
        trials = response.json()["results"]

        # Create a dictionary of {company_symbol: trial_data}
        return {
            trial["sponsor"]: {
                "approved_drugs": trial.get("products", []),
                "clinical_trials": trial.get("clinical_stages", {}),
            }
            for trial in trials
        }


async def filter_biotech_companies(companies: List[Dict[str, Any]], fda_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter companies based on biotech relevance, liquidity, and activity."""
    filtered = []
    
    for company in companies:
        market_cap = company.get("market_cap", 0)
        volume = company.get("daily_volume", 0)
        symbol = company["symbol"]
        exchange = company.get("exchange", "")

        # Apply filters
        if market_cap < MARKET_CAP_MIN and volume < TRADING_VOLUME_MIN:
            continue
        if exchange not in EXCHANGES_ALLOWED:
            continue

        # Check FDA trial data
        fda_info = fda_data.get(symbol, {})
        if not fda_info:  # Skip if the company has no biotech presence
            continue

        filtered.append({
            "symbol": symbol,
            "name": company["name"],
            "market_cap": market_cap,
            "exchange": exchange,
            "approved_drugs": len(fda_info.get("approved_drugs", [])),
            "clinical_trials": fda_info.get("clinical_trials", {}),
            "updated_at": datetime.utcnow(),
        })

    return filtered


async def store_companies_in_db(companies: List[Dict[str, Any]]):
    """Insert biotech companies into the database."""
    if not companies:
        print("No biotech companies matched criteria.")
        return

    conn = await asyncpg.connect(DB_URL)
    try:
        query = """
        INSERT INTO company_info (symbol, name, market_cap, exchange, approved_drugs, clinical_trials, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (symbol) DO UPDATE 
        SET market_cap = EXCLUDED.market_cap,
            exchange = EXCLUDED.exchange,
            approved_drugs = EXCLUDED.approved_drugs,
            clinical_trials = EXCLUDED.clinical_trials,
            updated_at = EXCLUDED.updated_at;
        """
        for company in companies:
            await conn.execute(
                query,
                company["symbol"],
                company["name"],
                company["market_cap"],
                company["exchange"],
                company["approved_drugs"],
                str(company["clinical_trials"]),
                company["updated_at"],
            )
        print(f"✅ Successfully inserted {len(companies)} companies into the database.")

    finally:
        await conn.close()


async def main():
    """Main script execution."""
    print("🔍 Fetching biotech companies from SEC...")
    sec_companies = await fetch_sec_companies()

    print("💊 Fetching biotech clinical trial data from FDA...")
    fda_data = await fetch_fda_trials()

    print("🧪 Filtering relevant biotech companies...")
    biotech_companies = await filter_biotech_companies(sec_companies, fda_data)

    print(f"📊 {len(biotech_companies)} biotech companies selected for storage.")
    await store_companies_in_db(biotech_companies)


if __name__ == "__main__":
    asyncio.run(main())