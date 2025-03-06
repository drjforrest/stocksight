import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import requests
from dotenv import load_dotenv
from .marketstack import MarketStackClient

load_dotenv()

class MarketDataService:
    """Service for handling market data operations."""

    def __init__(self):
        self.client = MarketStackClient()

    def _make_request(self, endpoint: str, params: Dict = None) -> Union[Dict, List, None]:
        """Make a request to the MarketStack API with error handling"""
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {str(e)}")
            return None

    async def get_intraday_data(
        self,
        symbol: str,
        interval: str = '1min',
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get intraday data for a symbol."""
        response = await self.client.get_intraday_data(
            symbols=[symbol],
            interval=interval,
            date_from=date_from,
            date_to=date_to
        )
        return response.get('data', [])

    async def get_eod_data(
        self,
        symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get end-of-day data for a symbol."""
        response = await self.client.get_eod_data(
            symbols=[symbol],
            date_from=date_from,
            date_to=date_to
        )
        return response.get('data', [])

    async def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information for a symbol."""
        response = await self.client.get_tickers(search=symbol)
        data = response.get('data', [])
        return next((item for item in data if item['symbol'] == symbol), None)

    async def get_exchanges(self) -> List[Dict[str, Any]]:
        """Get list of exchanges."""
        response = await self.client.get_exchanges()
        return response.get('data', [])

    async def get_index_data(
        self,
        index_symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get market index data."""
        response = await self.client.get_indices(
            symbols=[index_symbol],
            date_from=date_from,
            date_to=date_to
        )
        return response.get('data', [])

    async def get_dividends(
        self,
        symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get dividend information for a symbol."""
        response = await self.client.get_dividends(
            symbols=[symbol],
            date_from=date_from,
            date_to=date_to
        )
        return response.get('data', [])

    async def get_splits(
        self,
        symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get stock split information for a symbol."""
        response = await self.client.get_splits(
            symbols=[symbol],
            date_from=date_from,
            date_to=date_to
        )
        return response.get('data', []) 