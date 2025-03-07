from typing import Dict, Optional, List
import httpx
import os
from datetime import datetime
import asyncio
from dataclasses import dataclass

@dataclass
class CompanyFigures:
    symbol: str
    name: str
    competitor_score: float
    market_cap: Optional[str] = None
    price: Optional[float] = None
    volume: Optional[int] = None
    therapeutic_area: Optional[str] = None
    drug_applications: Optional[List[str]] = None
    patents: Optional[List[str]] = None

class CompanyDataService:
    def __init__(self):
        self.marketstack_key = os.getenv("MARKETSTACK_API_KEY")
        self.marketstack_url = "http://api.marketstack.com/v1"
        self.sec_url = "https://data.sec.gov/api/xbrl/companyfacts"
        self.fda_url = "https://api.fda.gov/drug"
        
        # Cache for company data (symbol -> data)
        self._cache: Dict[str, Dict] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        
    async def get_company_figures(self, symbol: str) -> CompanyFigures:
        """Get comprehensive company data from multiple sources."""
        # Check cache first
        if self._is_cache_valid(symbol):
            return self._create_figures_from_cache(symbol)
            
        # Fetch data from all sources concurrently
        market_data, sec_data, fda_data = await asyncio.gather(
            self._fetch_market_data(symbol),
            self._fetch_sec_data(symbol),
            self._fetch_fda_data(symbol)
        )
        
        # Combine and cache the data
        combined_data = {
            "market": market_data,
            "sec": sec_data,
            "fda": fda_data,
            "timestamp": datetime.utcnow()
        }
        self._cache[symbol] = combined_data
        self._cache_expiry[symbol] = datetime.utcnow()
        
        return self._create_figures_from_cache(symbol)
    
    async def _fetch_market_data(self, symbol: str) -> Dict:
        """Fetch market data from Marketstack."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.marketstack_url}/tickers/{symbol}/intraday/latest",
                    params={
                        "access_key": self.marketstack_key
                    }
                )
                data = response.json()
                return {
                    "price": data.get("close"),
                    "volume": data.get("volume"),
                    "name": data.get("symbol")  # Basic name from symbol
                }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {}

    async def _fetch_sec_data(self, symbol: str) -> Dict:
        """Fetch company data from SEC EDGAR."""
        try:
            # First get CIK number from symbol
            cik = await self._get_cik_from_symbol(symbol)
            if not cik:
                return {}
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.sec_url}/CIK{cik}.json",
                    headers={
                        "User-Agent": "StockSight research@stocksight.com"  # Required by SEC
                    }
                )
                data = response.json()
                
                # Extract relevant financial data
                return {
                    "market_cap": self._calculate_market_cap(data),
                    "industry": self._extract_industry(data)
                }
        except Exception as e:
            print(f"Error fetching SEC data: {e}")
            return {}

    async def _fetch_fda_data(self, symbol: str) -> Dict:
        """Fetch drug and therapeutic area data from OpenFDA."""
        try:
            async with httpx.AsyncClient() as client:
                # Search drug applications by company
                response = await client.get(
                    f"{self.fda_url}/drugsfda.json",
                    params={
                        "search": f"sponsor_name:{symbol}",
                        "limit": 100
                    }
                )
                data = response.json()
                
                # Process FDA data
                applications = data.get("results", [])
                therapeutic_areas = set()
                drug_applications = []
                
                for app in applications:
                    if "products" in app:
                        for product in app["products"]:
                            if "therapeutic_area" in product:
                                therapeutic_areas.add(product["therapeutic_area"])
                            drug_applications.append(product.get("trade_name"))
                
                return {
                    "therapeutic_areas": list(therapeutic_areas),
                    "drug_applications": drug_applications
                }
        except Exception as e:
            print(f"Error fetching FDA data: {e}")
            return {}

    async def _get_cik_from_symbol(self, symbol: str) -> Optional[str]:
        """Convert stock symbol to SEC CIK number."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.sec.gov/files/company_tickers.json"
                )
                data = response.json()
                
                # Find matching company
                for entry in data.values():
                    if entry["ticker"] == symbol.upper():
                        # Format CIK to 10 digits
                        return str(entry["cik_str"]).zfill(10)
                return None
        except Exception as e:
            print(f"Error getting CIK: {e}")
            return None

    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid (less than 1 hour old)."""
        if symbol not in self._cache_expiry:
            return False
        age = datetime.utcnow() - self._cache_expiry[symbol]
        return age.total_seconds() < 3600  # 1 hour cache

    def _create_figures_from_cache(self, symbol: str) -> CompanyFigures:
        """Create CompanyFigures object from cached data."""
        data = self._cache[symbol]
        market = data.get("market", {})
        sec = data.get("sec", {})
        fda = data.get("fda", {})
        
        # Calculate competitor score based on available data
        competitor_score = self._calculate_competitor_score(data)
        
        return CompanyFigures(
            symbol=symbol,
            name=market.get("name", symbol),
            competitor_score=competitor_score,
            market_cap=sec.get("market_cap"),
            price=market.get("price"),
            volume=market.get("volume"),
            therapeutic_area=", ".join(fda.get("therapeutic_areas", [])) or None,
            drug_applications=fda.get("drug_applications"),
            patents=[]  # TODO: Add patent data integration
        )

    def _calculate_competitor_score(self, data: Dict) -> float:
        """
        Calculate competitor score based on available data.
        Score is between 0 and 1, where 1 indicates strong competitor.
        """
        score = 0.0
        factors = 0
        
        # Market presence
        if data.get("market", {}).get("price"):
            score += 0.5
            factors += 1
            
        # FDA applications
        fda_data = data.get("fda", {})
        if fda_data.get("drug_applications"):
            score += len(fda_data["drug_applications"]) * 0.1  # More products = higher score
            factors += 1
            
        # Therapeutic areas
        if fda_data.get("therapeutic_areas"):
            score += len(fda_data["therapeutic_areas"]) * 0.2  # More areas = higher score
            factors += 1
            
        # Normalize score to 0-1 range
        return min(score / max(factors, 1), 1.0)

    def _calculate_market_cap(self, sec_data: Dict) -> Optional[str]:
        """Calculate market cap from SEC data."""
        try:
            if "facts" in sec_data:
                shares = sec_data["facts"].get("dei", {}).get("EntityCommonStockSharesOutstanding", [])
                if shares:
                    latest = max(shares, key=lambda x: x["end"])
                    return f"${latest['val']:,.0f}"
            return None
        except Exception:
            return None

    def _extract_industry(self, sec_data: Dict) -> Optional[str]:
        """Extract industry classification from SEC data."""
        try:
            if "facts" in sec_data:
                industry = sec_data["facts"].get("dei", {}).get("EntityIndustryClassification", [])
                if industry:
                    latest = max(industry, key=lambda x: x["end"])
                    return latest["val"]
            return None
        except Exception:
            return None 