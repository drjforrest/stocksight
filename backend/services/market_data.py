"""Service for handling market data operations through the MarketStack API.

This service provides methods to fetch various types of financial market data including:
- Real-time and historical stock prices
- Company information
- Market indices
- Corporate actions (dividends and splits)
- Exchange information
- IPO data

All methods are asynchronous and return structured data from the MarketStack API.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv
from .marketstack import MarketStackClient
from config.settings import get_settings
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.ipo import IPOListing, IPOStatus

load_dotenv()
settings = get_settings()

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
        self.client = MarketStackClient(api_key=settings.marketstack_api_key)

    async def cleanup(self):
        """Cleanup resources."""
        await self.client.cleanup()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def get_intraday_data(
        self,
        symbol: str,
        interval: str = '1min',
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get intraday price data for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            interval (str, optional): Time interval between data points. Defaults to '1min'
            date_from (datetime, optional): Start date for historical data
            date_to (datetime, optional): End date for historical data
            limit (int, optional): Maximum number of results to return
            
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
            date_to=date_to,
            limit=limit
        )
        return response.get('data', [])

    async def get_eod_data(
        self,
        symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get end-of-day price data for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            date_from (datetime, optional): Start date for historical data
            date_to (datetime, optional): End date for historical data
            limit (int, optional): Maximum number of results to return
            
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
            date_to=date_to,
            limit=limit
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
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get historical data for a market index.
        
        Args:
            index_symbol (str): Index symbol (e.g., '^GSPC' for S&P 500)
            date_from (datetime, optional): Start date for historical data
            date_to (datetime, optional): End date for historical data
            limit (int, optional): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of index data points containing:
                - date: Trading date
                - value: Index value
                - change: Daily change
                - change_percent: Daily change percentage
        """
        response = await self.client.get_index_data(
            symbols=[index_symbol],
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        return response.get('data', [])

    async def get_dividends(
        self,
        symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get dividend history for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            date_from (datetime, optional): Start date for dividend history
            date_to (datetime, optional): End date for dividend history
            limit (int, optional): Maximum number of results to return
            
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
            date_to=date_to,
            limit=limit
        )
        return response.get('data', [])

    async def get_splits(
        self,
        symbol: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get stock split history for a given symbol.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            date_from (datetime, optional): Start date for split history
            date_to (datetime, optional): End date for split history
            limit (int, optional): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of split events containing:
                - date: Split date
                - split_factor: Split ratio (e.g., 2:1, 3:1)
                - type: Split type (forward, reverse)
        """
        response = await self.client.get_splits(
            symbols=[symbol],
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        return response.get('data', [])

    async def search_symbols(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for stock symbols and companies.
        
        Args:
            query (str): Search term for company name or symbol
            limit (int, optional): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of matching companies and symbols
        """
        response = await self.client.get_tickers(
            search=query,
            limit=limit
        )
        return response.get('data', [])

    async def get_ipo_data(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Optional[Session] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get IPO data for a specified date range.
        
        Args:
            start_date (datetime): Start date for IPO data
            end_date (datetime): End date for IPO data
            db (Optional[Session]): Database session for querying IPO data
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing:
                - recent: List of recently completed IPOs
                - upcoming: List of upcoming IPOs
        """
        if not db:
            return {
                "recent": [],
                "upcoming": []
            }

        # Query recent IPOs
        recent_stmt = (
            select(IPOListing)
            .where(
                IPOListing.status == IPOStatus.COMPLETED,  # type: ignore[reportGeneralTypeIssues]
                IPOListing.filing_date >= start_date,  # type: ignore[reportGeneralTypeIssues]
                IPOListing.filing_date <= end_date  # type: ignore[reportGeneralTypeIssues]
            )
        )
        recent_ipos = db.execute(recent_stmt).scalars().all()

        # Query upcoming IPOs
        upcoming_stmt = (
            select(IPOListing)
            .where(
                IPOListing.status.in_([IPOStatus.FILED, IPOStatus.UPCOMING]),  # type: ignore[reportGeneralTypeIssues]
                IPOListing.expected_date >= start_date,  # type: ignore[reportGeneralTypeIssues]
                IPOListing.expected_date <= end_date  # type: ignore[reportGeneralTypeIssues]
            )
        )
        upcoming_ipos = db.execute(upcoming_stmt).scalars().all()

        # Convert to dictionaries
        recent = [
            {
                "company_name": ipo.company_name,
                "symbol": ipo.symbol,
                "filing_date": ipo.filing_date,
                "price_range": (
                    f"${db.scalar(select(ipo.price_range_low))}-${db.scalar(select(ipo.price_range_high))}"
                    if db.scalar(select(ipo.price_range_low)) is not None and 
                       db.scalar(select(ipo.price_range_high)) is not None 
                    else None
                ) if db else None,
                "shares_offered": ipo.shares_offered,
                "initial_valuation": ipo.initial_valuation,
                "lead_underwriters": ipo.lead_underwriters,
                "therapeutic_area": ipo.therapeutic_area,
                "pipeline_stage": ipo.pipeline_stage,
                "primary_indication": ipo.primary_indication
            }
            for ipo in recent_ipos
        ]

        upcoming = [
            {
                "company_name": ipo.company_name,
                "symbol": ipo.symbol,
                "filing_date": ipo.filing_date,
                "expected_date": ipo.expected_date,
                "price_range": (
                    f"${db.scalar(select(ipo.price_range_low))}-${db.scalar(select(ipo.price_range_high))}"
                    if db.scalar(select(ipo.price_range_low)) is not None and 
                       db.scalar(select(ipo.price_range_high)) is not None 
                    else None
                ) if db else None,
                "shares_offered": ipo.shares_offered,
                "initial_valuation": ipo.initial_valuation,
                "lead_underwriters": ipo.lead_underwriters,
                "therapeutic_area": ipo.therapeutic_area,
                "pipeline_stage": ipo.pipeline_stage,
                "primary_indication": ipo.primary_indication
            }
            for ipo in upcoming_ipos
        ]

        return {
            "recent": recent,
            "upcoming": upcoming
        } 