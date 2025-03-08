import os
import json
import httpx
from datetime import datetime, timedelta
import redis.asyncio as aioredis
from typing import Optional, Dict, Any, List, Union, TypedDict, cast
from fastapi import HTTPException
import asyncio
from config.settings import get_settings

settings = get_settings()

# Initialize Redis for caching API responses
redis = aioredis.from_url(
    f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
    encoding="utf-8",
    decode_responses=True
)

class CacheData(TypedDict):
    data: Dict[str, Any]
    timestamp: float

class MarketStackClient:
    """Client for interacting with the MarketStack API with caching & rate handling."""

    def __init__(self, api_key: str):
        """Initialize the MarketStack client.
        
        Args:
            api_key (str): Your MarketStack API key
        """
        self.api_key = api_key
        self.base_url = "http://api.marketstack.com/v1"
        self.client = httpx.AsyncClient()

    async def cleanup(self):
        """Cleanup resources."""
        await self.client.aclose()
        await redis.close()

    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def _get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if available."""
        try:
            cached = await redis.get(key)
            if cached:
                cache_data = json.loads(cached)
                if isinstance(cache_data, dict) and 'data' in cache_data:
                    return cast(Dict[str, Any], cache_data['data'])
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    async def _cache_response(self, key: str, data: Dict[str, Any], ttl: int = 3600) -> None:
        """Store API response in cache for a given time-to-live (TTL)."""
        try:
            cache_data: CacheData = {
                'data': data,
                'timestamp': datetime.now().timestamp()
            }
            # Convert ttl to int to satisfy Redis type requirements
            await redis.setex(name=key, time=int(ttl), value=json.dumps(cache_data))
        except (TypeError, ValueError) as e:
            print(f"Error caching response: {e}")
            # Don't raise the error - just log it and continue
            pass

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        cache_ttl: int = 3600
    ) -> Dict[str, Any]:
        """Make a request to MarketStack with caching and rate limiting."""
        request_params = params.copy() if params is not None else {}
        request_params['access_key'] = self.api_key

        cache_key = f"marketstack:{endpoint}:{json.dumps(request_params, sort_keys=True)}"
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        try:
            response = await self.client.get(f"{self.base_url}/{endpoint}", params=request_params)
            response.raise_for_status()
            data = response.json()

            # Cache successful response
            await self._cache_response(cache_key, data, cache_ttl)
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit exceeded
                await asyncio.sleep(60)  # Wait and retry after 60s
                return await self._make_request(endpoint, params, cache_ttl)
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"MarketStack API Error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Request Error: {str(e)}"
            )

    async def get_eod_data(
        self,
        symbols: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        exchange: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get end-of-day data for specified symbols.
        
        Args:
            symbols (List[str]): List of stock symbols
            date_from (datetime, optional): Start date for historical data
            date_to (datetime, optional): End date for historical data
            exchange (str, optional): Exchange identifier (e.g., 'INDX' for indices)
            limit (int, optional): Number of results per page (max 1000)
            offset (int, optional): Pagination offset
            
        Returns:
            Dict: EOD data including open, high, low, close, and volume
        """
        params = {
            'symbols': ','.join(symbols),
            'limit': min(limit, 1000),
            'offset': offset
        }
        
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')
        if exchange:
            params['exchange'] = exchange

        return await self._make_request('eod', params)

    async def get_intraday_data(
        self,
        symbols: List[str],
        interval: str = '1min',
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get intraday data for specified symbols.
        
        Args:
            symbols (List[str]): List of stock symbols
            interval (str, optional): Time interval ('1min', '5min', etc.)
            date_from (datetime, optional): Start datetime
            date_to (datetime, optional): End datetime
            limit (int, optional): Number of results per page
            offset (int, optional): Pagination offset
            
        Returns:
            Dict: Intraday price data at specified intervals
        """
        params = {
            'symbols': ','.join(symbols),
            'interval': interval,
            'limit': limit,
            'offset': offset
        }
        
        if date_from:
            params['date_from'] = date_from.isoformat()
        if date_to:
            params['date_to'] = date_to.isoformat()

        return await self._make_request('intraday', params)

    async def get_tickers(
        self,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get information about available stock tickers.
        
        Args:
            search (str, optional): Search term for filtering tickers
            limit (int, optional): Number of results per page
            offset (int, optional): Pagination offset
            
        Returns:
            Dict: Ticker information including symbol, name, and exchange
        """
        params: Dict[str, Union[str, int]] = {'limit': limit, 'offset': offset}
        if search:
            params['search'] = search

        return await self._make_request('tickers', params)

    async def get_exchanges(
        self,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get information about supported stock exchanges.
        
        Args:
            search (str, optional): Search term for filtering exchanges
            limit (int, optional): Number of results per page
            offset (int, optional): Pagination offset
            
        Returns:
            Dict: Exchange information including name, MIC, and country
        """
        params: Dict[str, Union[str, int]] = {'limit': limit, 'offset': offset}
        if search:
            params['search'] = search

        return await self._make_request('exchanges', params)

    async def get_dividends(
        self,
        symbols: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get dividend information for specified symbols.
        
        Args:
            symbols (List[str]): List of stock symbols
            date_from (datetime, optional): Start date for dividend history
            date_to (datetime, optional): End date for dividend history
            limit (int, optional): Number of results per page
            offset (int, optional): Pagination offset
            
        Returns:
            Dict: Dividend data including amount, declaration date, and payment date
        """
        params = {
            'symbols': ','.join(symbols),
            'limit': limit,
            'offset': offset
        }
        
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')

        return await self._make_request('dividends', params)

    async def get_splits(
        self,
        symbols: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get stock split information for specified symbols.
        
        Args:
            symbols (List[str]): List of stock symbols
            date_from (datetime, optional): Start date for split history
            date_to (datetime, optional): End date for split history
            limit (int, optional): Number of results per page
            offset (int, optional): Pagination offset
            
        Returns:
            Dict: Split data including ratio and execution date
        """
        params = {
            'symbols': ','.join(symbols),
            'limit': limit,
            'offset': offset
        }
        
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')

        return await self._make_request('splits', params)

    async def get_index_data(
        self,
        symbols: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get market index data.
        
        Args:
            symbols (List[str]): List of index symbols (e.g., ['DJI.INDX'])
            date_from (datetime, optional): Start date for index history
            date_to (datetime, optional): End date for index history
            limit (int, optional): Number of results per page
            offset (int, optional): Pagination offset
            
        Returns:
            Dict: Index data including value, change, and volume
        """
        return await self.get_eod_data(
            symbols=symbols,
            date_from=date_from,
            date_to=date_to,
            exchange='INDX',
            limit=limit,
            offset=offset
        )