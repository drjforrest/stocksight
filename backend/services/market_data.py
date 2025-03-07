"""Service for handling market data operations through the MarketStack API.

This service provides methods to fetch various types of financial market data including:
- Real-time and historical stock prices
- Company information
- Market indices
- Corporate actions (dividends and splits)
- Exchange information

All methods are asynchronous and return structured data from the MarketStack API.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import requests
from dotenv import load_dotenv
from .marketstack import MarketStackClient

load_dotenv()

class MarketDataService:
    """Service for handling market data operations through the MarketStack API.
    
    This service encapsulates all market data operations and provides a clean interface
    for fetching various types of financial data. It handles API communication,
    error handling, and data formatting.

    Attributes:
        client (MarketStackClient): Instance of MarketStack API client
    """

    def __init__(self):
        """Initialize the MarketDataService with a MarketStack client."""
        self.client = MarketStackClient()

    def _make_request(self, endpoint: str, params: Dict = None) -> Union[Dict, List, None]:
        """Make a request to the MarketStack API with error handling.
        
        Args:
            endpoint (str): API endpoint to call
            params (Dict, optional): Query parameters for the request
            
        Returns:
            Union[Dict, List, None]: API response data or None if request fails
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
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
        """Get intraday price data for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            interval (str, optional): Time interval between data points. Defaults to '1min'
            date_from (datetime, optional): Start date for historical data
            date_to (datetime, optional): End date for historical data
            
        Returns:
            List[Dict[str, Any]]: List of intraday price data points containing:
                - timestamp: Datetime of the price point
                - open: Opening price
                - high: Highest price during interval
                - low: Lowest price during interval
                - close: Closing price
                - volume: Trading volume
        """
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
        """Get end-of-day price data for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            date_from (datetime, optional): Start date for historical data
            date_to (datetime, optional): End date for historical data
            
        Returns:
            List[Dict[str, Any]]: List of daily price data points containing:
                - date: Trading date
                - open: Opening price
                - high: Day's highest price
                - low: Day's lowest price
                - close: Closing price
                - volume: Daily trading volume
                - adj_close: Adjusted closing price
        """
        response = await self.client.get_eod_data(
            symbols=[symbol],
            date_from=date_from,
            date_to=date_to
        )
        return response.get('data', [])

    async def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get detailed company information for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            
        Returns:
            Optional[Dict[str, Any]]: Company information including:
                - name: Company name
                - symbol: Stock symbol
                - exchange: Listed exchange
                - market_cap: Market capitalization
                - country: Country of incorporation
                - sector: Business sector
                - industry: Industry classification
                Or None if company not found
        """
        response = await self.client.get_tickers(search=symbol)
        data = response.get('data', [])
        return next((item for item in data if item['symbol'] == symbol), None)

    async def get_exchanges(self) -> List[Dict[str, Any]]:
        """Get list of supported stock exchanges.
        
        Returns:
            List[Dict[str, Any]]: List of exchanges containing:
                - name: Exchange name
                - acronym: Exchange acronym
                - mic: Market Identifier Code
                - country: Country of operation
                - city: City of operation
                - timezone: Exchange timezone
                - currency: Trading currency
        """
        response = await self.client.get_exchanges()
        return response.get('data', [])

    async def get_index_data(
        self,
        index_symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get historical data for a market index.
        
        Args:
            index_symbol (str): Index symbol (e.g., '^GSPC' for S&P 500)
            date_from (datetime, optional): Start date for historical data
            date_to (datetime, optional): End date for historical data
            
        Returns:
            List[Dict[str, Any]]: List of index data points containing:
                - date: Trading date
                - value: Index value
                - change: Daily change
                - change_percent: Daily change percentage
        """
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
        """Get dividend history for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            date_from (datetime, optional): Start date for dividend history
            date_to (datetime, optional): End date for dividend history
            
        Returns:
            List[Dict[str, Any]]: List of dividend events containing:
                - date: Dividend date
                - amount: Dividend amount
                - type: Dividend type (regular, special, etc.)
                - currency: Dividend currency
        """
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
        """Get stock split history for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            date_from (datetime, optional): Start date for split history
            date_to (datetime, optional): End date for split history
            
        Returns:
            List[Dict[str, Any]]: List of split events containing:
                - date: Split date
                - split_factor: Split ratio (e.g., 2:1, 3:1)
                - type: Split type (forward, reverse)
        """
        response = await self.client.get_splits(
            symbols=[symbol],
            date_from=date_from,
            date_to=date_to
        )
        return response.get('data', []) 