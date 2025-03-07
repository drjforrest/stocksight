from typing import List, Dict, Optional
import httpx
from datetime import datetime
from .cache import CacheService, cache_result, SEARCH_RESULTS_EXPIRY
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.company import CompanyInfo
from api.schemas.company import CompanyBrowseResponse

class CompanyBrowseService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = CacheService()
        self.fda_url = "https://api.fda.gov/drug/drugsfda.json"
        self.sec_url = "https://data.sec.gov/api/xbrl/companyfacts"

    @cache_result("browse:therapeutic", SEARCH_RESULTS_EXPIRY)
    async def get_therapeutic_areas(self) -> List[str]:
        """Get list of all therapeutic areas from FDA data."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.fda_url}",
                    params={
                        "search": "products.therapeutic_area:*",
                        "limit": 1000,
                        "count": "products.therapeutic_area"
                    }
                )
                data = response.json()
                return sorted(list(set(
                    term["term"] for term in data.get("results", [])
                )))
        except Exception as e:
            print(f"Error fetching therapeutic areas: {e}")
            return []

    @cache_result("browse:companies", SEARCH_RESULTS_EXPIRY)
    async def browse_companies(
        self,
        therapeutic_area: Optional[str] = None,
        market_cap_min: Optional[float] = None,
        market_cap_max: Optional[float] = None,
        has_approved_drugs: Optional[bool] = None,
        phase: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Browse companies with filters.
        
        Args:
            therapeutic_area: Filter by therapeutic area
            market_cap_min: Minimum market cap (in billions)
            market_cap_max: Maximum market cap (in billions)
            has_approved_drugs: Filter for companies with approved drugs
            phase: Filter by clinical trial phase
            page: Page number
            page_size: Items per page
        """
        try:
            # Get companies from SEC that match market cap criteria
            sec_companies = await self._get_sec_companies(market_cap_min, market_cap_max)
            
            # Get FDA data for filtering
            fda_data = await self._get_fda_data(
                therapeutic_area=therapeutic_area,
                has_approved_drugs=has_approved_drugs,
                phase=phase
            )
            
            # Combine and filter results
            results = []
            for company in sec_companies:
                symbol = company["symbol"]
                if symbol in fda_data or not any([therapeutic_area, has_approved_drugs, phase]):
                    company_data = {
                        "symbol": symbol,
                        "name": company["name"],
                        "market_cap": company["market_cap"],
                        "therapeutic_areas": fda_data.get(symbol, {}).get("therapeutic_areas", []),
                        "approved_drugs": fda_data.get(symbol, {}).get("approved_drugs", []),
                        "clinical_trials": fda_data.get(symbol, {}).get("clinical_trials", {})
                    }
                    results.append(company_data)
            
            # Sort by market cap
            results.sort(key=lambda x: x["market_cap"], reverse=True)
            
            # Paginate
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_results = results[start_idx:end_idx]
            
            return {
                "total": len(results),
                "page": page,
                "page_size": page_size,
                "results": paginated_results
            }
            
        except Exception as e:
            print(f"Error browsing companies: {e}")
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "results": []
            }

    async def _get_sec_companies(
        self,
        market_cap_min: Optional[float],
        market_cap_max: Optional[float]
    ) -> List[Dict]:
        """Get companies from SEC that match market cap criteria."""
        try:
            # Get company tickers and CIK numbers
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.sec.gov/files/company_tickers.json",
                    headers={"User-Agent": "StockSight research@stocksight.com"}
                )
                companies = response.json()
            
            results = []
            for company in companies.values():
                # Get detailed company data including market cap
                market_cap = await self._get_company_market_cap(company["cik_str"])
                if market_cap:
                    market_cap_billions = market_cap / 1_000_000_000  # Convert to billions
                    
                    # Apply market cap filters
                    if market_cap_min and market_cap_billions < market_cap_min:
                        continue
                    if market_cap_max and market_cap_billions > market_cap_max:
                        continue
                    
                    results.append({
                        "symbol": company["ticker"],
                        "name": company["title"],
                        "market_cap": market_cap_billions
                    })
            
            return results
            
        except Exception as e:
            print(f"Error getting SEC companies: {e}")
            return []

    @cache_result("sec:market_cap", SEARCH_RESULTS_EXPIRY)
    async def _get_company_market_cap(self, cik: str) -> Optional[float]:
        """Get company market cap from SEC data."""
        try:
            cik = str(cik).zfill(10)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.sec_url}/CIK{cik}.json",
                    headers={"User-Agent": "StockSight research@stocksight.com"}
                )
                data = response.json()
                
                if "facts" in data:
                    shares = data["facts"].get("dei", {}).get(
                        "EntityCommonStockSharesOutstanding",
                        []
                    )
                    if shares:
                        latest = max(shares, key=lambda x: x["end"])
                        return latest["val"]
            return None
        except Exception:
            return None

    async def _get_fda_data(
        self,
        therapeutic_area: Optional[str],
        has_approved_drugs: Optional[bool],
        phase: Optional[str]
    ) -> Dict:
        """Get FDA data for filtering companies."""
        try:
            params = {
                "limit": 1000
            }
            
            # Add therapeutic area filter
            if therapeutic_area:
                params["search"] = f"products.therapeutic_area:\"{therapeutic_area}\""
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.fda_url,
                    params=params
                )
                data = response.json()
            
            results = {}
            for application in data.get("results", []):
                company = application.get("sponsor_name")
                if not company:
                    continue
                
                if company not in results:
                    results[company] = {
                        "therapeutic_areas": set(),
                        "approved_drugs": [],
                        "clinical_trials": {
                            "phase1": [],
                            "phase2": [],
                            "phase3": [],
                            "phase4": []
                        }
                    }
                
                # Process products
                for product in application.get("products", []):
                    if "therapeutic_area" in product:
                        results[company]["therapeutic_areas"].add(
                            product["therapeutic_area"]
                        )
                    
                    # Track approved drugs
                    if product.get("marketing_status") == "Prescription":
                        results[company]["approved_drugs"].append(
                            product.get("trade_name")
                        )
                    
                    # Track clinical trials
                    if "phase" in product:
                        phase_key = f"phase{product['phase']}"
                        if phase_key in results[company]["clinical_trials"]:
                            results[company]["clinical_trials"][phase_key].append(
                                product.get("trade_name")
                            )
            
            # Convert sets to lists for JSON serialization
            for company in results:
                results[company]["therapeutic_areas"] = list(
                    results[company]["therapeutic_areas"]
                )
            
            # Apply filters
            if has_approved_drugs is not None:
                results = {
                    k: v for k, v in results.items()
                    if bool(v["approved_drugs"]) == has_approved_drugs
                }
            
            if phase:
                results = {
                    k: v for k, v in results.items()
                    if v["clinical_trials"].get(f"phase{phase}")
                }
            
            return results
            
        except Exception as e:
            print(f"Error getting FDA data: {e}")
            return {} 