import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
from fastapi import HTTPException

class MarketStackClient:
    """Client for interacting with the MarketStack API."""
    
    def __init__(self):
        self.api_key = os.getenv('MARKETSTACK_API_KEY')
        if not self.api_key:
            raise ValueError("MARKETSTACK_API_KEY environment variable is not set")
        self.base_url = "http://api.marketstack.com/v1"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make a request to the MarketStack API."""
        if params is None:
            params = {}
        params['access_key'] = self.api_key

        try:
            response = await self.client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_eod_data(
        self, 
        symbols: List[str], 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict:
        """Get end-of-day data for specified symbols."""
        params = {
            'symbols': ','.join(symbols),
            'limit': limit
        }
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')
        
        return await self._make_request('eod', params)

    async def get_intraday_data(
        self,
        symbols: List[str],
        interval: str = '1min',
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict:
        """Get intraday data for specified symbols."""
        params = {
            'symbols': ','.join(symbols),
            'interval': interval,
            'limit': limit
        }
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')
        
        return await self._make_request('intraday', params)

    async def get_tickers(
        self,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get ticker information."""
        params = {
            'limit': limit,
            'offset': offset
        }
        if search:
            params['search'] = search
        
        return await self._make_request('tickers', params)

    async def get_exchanges(
        self,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """Get exchange information."""
        params = {
            'limit': limit,
            'offset': offset
        }
        if search:
            params['search'] = search
        
        return await self._make_request('exchanges', params)

    async def get_dividends(
        self,
        symbols: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict:
        """Get dividend information for specified symbols."""
        params = {
            'symbols': ','.join(symbols),
            'limit': limit
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
        limit: int = 100
    ) -> Dict:
        """Get stock split information for specified symbols."""
        params = {
            'symbols': ','.join(symbols),
            'limit': limit
        }
        if date_from:
            params['date_from'] = date_from.strftime('%Y-%m-%d')
        if date_to:
            params['date_to'] = date_to.strftime('%Y-%m-%d')
        
        return await self._make_request('splits', params)

    async def get_indices(
        self,
        symbols: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> Dict:
        """Get index data for specified symbols."""
        # Using EOD endpoint with index symbols
        return await self.get_eod_data(symbols, date_from, date_to, limit) 