import os
import json
import aioredis
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from functools import wraps
import asyncio

# Initialize Redis for caching API responses
redis = aioredis.from_url("redis://localhost", decode_responses=True)

class MarketStackClient:
    """Client for interacting with the MarketStack API with caching & rate handling."""

    def __init__(self):
        self.api_key = os.getenv('MARKETSTACK_API_KEY')
        if not self.api_key:
            raise ValueError("MARKETSTACK_API_KEY environment variable is not set")
        self.base_url = "http://api.marketstack.com/v1"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _get_cached_response(self, key: str) -> Optional[Dict]:
        """Retrieve cached response if available."""
        cached = await redis.get(key)
        return json.loads(cached) if cached else None

    async def _cache_response(self, key: str, data: Dict, ttl: int = 3600):
        """Store API response in cache for a given time-to-live (TTL)."""
        await redis.set(key, json.dumps(data), ex=ttl)

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None, cache_ttl: int = 3600) -> Dict:
        """Make a request to MarketStack with caching and rate limiting."""
        if params is None:
            params = {}
        params['access_key'] = self.api_key

        cache_key = f"marketstack:{endpoint}:{json.dumps(params, sort_keys=True)}"
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        try:
            response = await self.client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()

            # Cache successful response
            await self._cache_response(cache_key, data, cache_ttl)
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit exceeded
                await asyncio.sleep(60)  # Wait and retry after 60s
                return await self._make_request(endpoint, params, cache_ttl)
            raise HTTPException(status_code=e.response.status_code, detail="MarketStack API Error")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail="MarketStack service unavailable")

    async def get_eod_data(self, symbols: List[str], date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, limit: int = 100) -> Dict:
        """Get end-of-day data for specified symbols."""
        params = {'symbols': ','.join(symbols), 'limit': limit}
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')

        return await self._make_request('eod', params)

    async def get_intraday_data(self, symbols: List[str], interval: str = '1min', date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, limit: int = 100) -> Dict:
        """Get intraday data for specified symbols."""
        params = {'symbols': ','.join(symbols), 'interval': interval, 'limit': limit}
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')

        return await self._make_request('intraday', params)

    async def get_tickers(self, search: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict:
        """Get ticker information."""
        params = {'limit': limit, 'offset': offset}
        if search:
            params['search'] = search

        return await self._make_request('tickers', params)

    async def get_exchanges(self, search: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict:
        """Get exchange information."""
        params = {'limit': limit, 'offset': offset}
        if search:
            params['search'] = search

        return await self._make_request('exchanges', params)

    async def get_dividends(self, symbols: List[str], date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, limit: int = 100) -> Dict:
        """Get dividend information for specified symbols."""
        params = {'symbols': ','.join(symbols), 'limit': limit}
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')

        return await self._make_request('dividends', params)

    async def get_splits(self, symbols: List[str], date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, limit: int = 100) -> Dict:
        """Get stock split information for specified symbols."""
        params = {'symbols': ','.join(symbols), 'limit': limit}
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')

        return await self._make_request('splits', params)

    async def get_indices(self, symbols: List[str], date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, limit: int = 100) -> Dict:
        """Get index data for specified symbols."""
        return await self.get_eod_data(symbols, date_from, date_to, limit)