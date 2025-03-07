import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import asyncio
from fastapi import HTTPException
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

def rate_limit(calls: int, period: int):
    """Rate limiting decorator"""
    timestamps = []
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            timestamps.append(now)
            
            # Remove timestamps outside the window
            while timestamps and timestamps[0] < now - period:
                timestamps.pop(0)
                
            if len(timestamps) > calls:
                sleep_time = timestamps[0] + period - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class MarketStackClient:
    def __init__(self, api_key: str, base_url: str = "http://api.marketstack.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @rate_limit(calls=5, period=1)  # 5 calls per second
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make a rate-limited API request"""
        if params is None:
            params = {}
        params['access_key'] = self.api_key

        try:
            response = await self.client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            if e.response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    async def get_real_time_price(self, symbol: str) -> Dict:
        """
        Get real-time stock price data
        
        Args:
            symbol: Stock symbol (e.g., 'MRNA')
            
        Returns:
            Dictionary containing current price data
        """
        return await self._make_request("intraday/latest", {"symbols": symbol})

    async def get_historical_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get historical stock data
        
        Args:
            symbol: Stock symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            limit: Maximum number of records to return
            
        Returns:
            List of historical price data points
        """
        params = {
            "symbols": symbol,
            "limit": limit
        }
        
        if start_date:
            params["date_from"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["date_to"] = end_date.strftime("%Y-%m-%d")

        return await self._make_request("eod", params)

    async def get_company_info(self, symbol: str) -> Dict:
        """
        Get company information
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Company information and metadata
        """
        return await self._make_request(f"tickers/{symbol}")

    async def get_market_cap(self, symbol: str) -> Dict:
        """
        Get company market capitalization
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Market capitalization data
        """
        return await self._make_request(f"tickers/{symbol}/market_cap")

    async def batch_real_time_prices(self, symbols: List[str]) -> Dict:
        """
        Get real-time prices for multiple stocks
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary of price data for all requested symbols
        """
        return await self._make_request("intraday/latest", {
            "symbols": ",".join(symbols)
        })

    async def get_splits_and_dividends(
        self,
        symbol: str,
        start_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get stock splits and dividend history
        
        Args:
            symbol: Stock symbol
            start_date: Optional start date for historical data
            
        Returns:
            Dictionary containing splits and dividends data
        """
        params = {"symbols": symbol}
        if start_date:
            params["date_from"] = start_date.strftime("%Y-%m-%d")
            
        return await self._make_request("splits", params) 