from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from api.schemas.stock import (
    StockPriceCreate, StockPriceResponse,
    CompanyInfoCreate, CompanyInfoResponse,
    DividendCreate, DividendResponse,
    StockSplitCreate, StockSplitResponse,
    ExchangeCreate, ExchangeResponse
)
from services.stock import StockService
from config.database import get_db
from services.market_data import MarketDataService
from models.stock import StockPrice, CompanyInfo
from api.auth import get_current_user

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"},
        429: {"description": "Too many requests to MarketStack API"}
    },
)

# Stock Prices Endpoints
@router.post("/prices", response_model=StockPriceResponse)
async def create_stock_price(
    price: StockPriceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new stock price entry.

    Parameters:
    - **price**: Stock price data including symbol, price, and timestamp

    Returns:
    - Created stock price entry with ID and timestamp

    Raises:
    - **422**: Validation error if price data is invalid
    - **500**: Database error
    """
    async with StockService(db) as stock_service:
        return await stock_service.create_stock_price(price)

@router.get("/prices/{symbol}", response_model=List[StockPriceResponse])
async def get_stock_prices(
    symbol: str = Path(..., description="Stock symbol to fetch prices for"),
    start_date: Optional[datetime] = Query(None, description="Start date for price range (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="End date for price range (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get historical stock prices for a symbol within a date range.

    Parameters:
    - **symbol**: Stock symbol (e.g., AAPL, GOOGL)
    - **start_date**: Optional start date to filter prices
    - **end_date**: Optional end date to filter prices

    Returns:
    - List of stock prices with timestamps

    Examples:
    ```
    /stocks/prices/AAPL
    /stocks/prices/GOOGL?start_date=2024-01-01&end_date=2024-02-01
    ```
    """
    async with StockService(db) as stock_service:
        return await stock_service.get_stock_prices(symbol, start_date, end_date)

@router.get("/{symbol}/price")
async def get_current_price(
    symbol: str = Path(..., description="Stock symbol to fetch current price for"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current stock price and save to database.

    Parameters:
    - **symbol**: Stock symbol (e.g., AAPL, GOOGL)

    Returns:
    - Latest stock price data including:
        - open, high, low, close prices
        - volume
        - timestamp

    Raises:
    - **404**: Stock symbol not found
    - **429**: MarketStack API rate limit exceeded
    """
    async with MarketDataService() as market_service:
        data = await market_service.get_intraday_data(symbol, interval='1min')
        if not data:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        latest_price = data[0]
        db_price = StockPrice(
            symbol=symbol,
            price=latest_price["close"],
            timestamp=datetime.fromisoformat(latest_price["date"].replace('Z', '+00:00'))
        )
        db.add(db_price)
        db.commit()
        
        return latest_price

@router.get("/{symbol}/history")
async def get_stock_history(
    symbol: str = Path(..., description="Stock symbol to fetch history for"),
    days: int = Query(30, gt=0, le=365, description="Number of days of historical data to fetch")
):
    """
    Get historical stock data for the specified number of days.

    Parameters:
    - **symbol**: Stock symbol (e.g., AAPL, GOOGL)
    - **days**: Number of days of historical data (1-365, default: 30)

    Returns:
    - List of daily stock data including:
        - open, high, low, close prices
        - volume
        - adjusted close
        - date

    Examples:
    ```
    /stocks/AAPL/history
    /stocks/GOOGL/history?days=90
    ```

    Raises:
    - **404**: Stock symbol not found
    - **422**: Invalid days parameter
    - **429**: MarketStack API rate limit exceeded
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    async with MarketDataService() as market_service:
        return await market_service.get_eod_data(symbol, start_date, end_date)

# Company Info Endpoints
@router.post("/companies", response_model=CompanyInfoResponse)
async def create_company_info(
    company: CompanyInfoCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update company information.

    Parameters:
    - **company**: Company data including:
        - symbol (required)
        - name (required)
        - exchange (required)
        - country
        - sector
        - industry
        - market_cap
        - employees
        - website
        - description

    Returns:
    - Created/updated company information

    Raises:
    - **422**: Validation error if company data is invalid
    - **500**: Database error
    """
    async with StockService(db) as stock_service:
        return await stock_service.create_company_info(company)

@router.get("/companies/{symbol}", response_model=CompanyInfoResponse)
async def get_company_info(
    symbol: str = Path(..., description="Stock symbol to fetch company info for"),
    db: Session = Depends(get_db)
):
    """
    Get company information by symbol.

    Parameters:
    - **symbol**: Stock symbol (e.g., AAPL, GOOGL)

    Returns:
    - Company information including:
        - basic details (name, symbol, exchange)
        - sector and industry
        - financial metrics
        - contact information

    Notes:
    - Data is cached for 7 days to minimize API calls
    - Returns cached data if available and not expired

    Raises:
    - **404**: Company not found
    - **429**: MarketStack API rate limit exceeded
    """
    db_info = db.query(CompanyInfo).filter(CompanyInfo.symbol == symbol).first()
    
    if db_info and (datetime.utcnow() - db_info.updated_at).days < 7:
        return db_info
    
    async with MarketDataService() as market_service:
        company_data = await market_service.get_company_info(symbol)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if db_info:
            for key, value in company_data.items():
                setattr(db_info, key, value)
            db_info.updated_at = datetime.utcnow()  # type: ignore[reportGeneralTypeIssues]
        else:
            db_info = CompanyInfo(**company_data)
            db.add(db_info)
        
        db.commit()
        return company_data

@router.get("/companies", response_model=List[CompanyInfoResponse])
async def list_companies(
    sector: Optional[str] = Query(None, description="Filter companies by sector"),
    country: Optional[str] = Query(None, description="Filter companies by country"),
    db: Session = Depends(get_db)
):
    """
    List companies with optional filters.

    Parameters:
    - **sector**: Optional sector filter (e.g., Technology, Healthcare)
    - **country**: Optional country filter (e.g., US, GB)

    Returns:
    - List of companies matching the filters

    Examples:
    ```
    /stocks/companies
    /stocks/companies?sector=Technology
    /stocks/companies?country=US
    /stocks/companies?sector=Healthcare&country=GB
    ```
    """
    async with StockService(db) as stock_service:
        return await stock_service.list_companies(sector, country)

# Dividend History Endpoints
@router.post("/dividends", response_model=DividendResponse)
async def create_dividend(
    dividend: DividendCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new dividend record.

    Parameters:
    - **dividend**: Dividend data including:
        - symbol (required)
        - amount (required)
        - date (required)
        - type
        - payment_date

    Returns:
    - Created dividend record

    Raises:
    - **422**: Validation error if dividend data is invalid
    - **500**: Database error
    """
    async with StockService(db) as stock_service:
        return await stock_service.create_dividend(dividend)

@router.get("/{symbol}/dividends")
async def get_symbol_dividends(
    symbol: str = Path(..., description="Stock symbol to fetch dividends for"),
    days: Optional[int] = Query(365, gt=0, description="Number of days of dividend history")
):
    """
    Get dividend information for the specified number of days.

    Parameters:
    - **symbol**: Stock symbol (e.g., AAPL, MSFT)
    - **days**: Number of days of dividend history (default: 365)

    Returns:
    - List of dividend records including:
        - amount
        - declaration date
        - payment date
        - type

    Examples:
    ```
    /stocks/AAPL/dividends
    /stocks/MSFT/dividends?days=180
    ```

    Raises:
    - **404**: No dividend data found
    - **429**: MarketStack API rate limit exceeded
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days or 365)  # Default to 365 if None
    
    async with MarketDataService() as market_service:
        data = await market_service.get_dividends(symbol, start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail="Dividend data not found")
        return data

# Stock Splits Endpoints
@router.post("/splits", response_model=StockSplitResponse)
async def create_stock_split(
    split: StockSplitCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new stock split record.

    Parameters:
    - **split**: Stock split data including:
        - symbol (required)
        - ratio (required)
        - date (required)

    Returns:
    - Created stock split record

    Raises:
    - **422**: Validation error if split data is invalid
    - **500**: Database error
    """
    async with StockService(db) as stock_service:
        return await stock_service.create_stock_split(split)

@router.get("/{symbol}/splits")
async def get_symbol_splits(
    symbol: str = Path(..., description="Stock symbol to fetch splits for"),
    days: Optional[int] = Query(365, gt=0, description="Number of days of split history")
):
    """
    Get stock split information for the specified number of days.

    Parameters:
    - **symbol**: Stock symbol (e.g., AAPL, TSLA)
    - **days**: Number of days of split history (default: 365)

    Returns:
    - List of stock split records including:
        - ratio
        - date
        - before/after share counts

    Examples:
    ```
    /stocks/AAPL/splits
    /stocks/TSLA/splits?days=180
    ```

    Raises:
    - **404**: No split data found
    - **429**: MarketStack API rate limit exceeded
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days or 365)  # Default to 365 if None
    
    async with MarketDataService() as market_service:
        data = await market_service.get_splits(symbol, start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail="Split data not found")
        return data

# Exchange Endpoints
@router.post("/exchanges", response_model=ExchangeResponse)
async def create_exchange(
    exchange: ExchangeCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update exchange information.

    Parameters:
    - **exchange**: Exchange data including:
        - code (required)
        - name (required)
        - country
        - city
        - timezone
        - currency

    Returns:
    - Created/updated exchange information

    Raises:
    - **422**: Validation error if exchange data is invalid
    - **500**: Database error
    """
    async with StockService(db) as stock_service:
        return await stock_service.create_exchange(exchange)

@router.get("/exchanges/{code}", response_model=ExchangeResponse)
async def get_exchange(
    code: str = Path(..., description="Exchange code to fetch info for"),
    db: Session = Depends(get_db)
):
    """
    Get exchange information by code.

    Parameters:
    - **code**: Exchange code (e.g., NYSE, NASDAQ)

    Returns:
    - Exchange information including:
        - name
        - country
        - city
        - timezone
        - currency

    Raises:
    - **404**: Exchange not found
    """
    async with StockService(db) as stock_service:
        return await stock_service.get_exchange(code)

@router.get("/exchanges")
async def list_exchanges():
    """
    Get list of all exchanges.

    Returns:
    - List of exchanges with basic information:
        - code
        - name
        - country
        - timezone

    Examples:
    ```json
    [
        {
            "code": "NYSE",
            "name": "New York Stock Exchange",
            "country": "United States",
            "timezone": "America/New_York"
        },
        {
            "code": "LSE",
            "name": "London Stock Exchange",
            "country": "United Kingdom",
            "timezone": "Europe/London"
        }
    ]
    ```

    Raises:
    - **404**: No exchanges found
    - **429**: MarketStack API rate limit exceeded
    """
    async with MarketDataService() as market_service:
        exchanges = await market_service.get_exchanges()
        if not exchanges:
            raise HTTPException(status_code=404, detail="No exchanges found")
        return exchanges

# Market Data Endpoints
@router.get("/market/search")
async def search_symbols(
    query: str = Query(..., description="Search query for symbols or company names"),
    limit: Optional[int] = Query(10, gt=0, le=100, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
):
    """
    Search for symbols and companies.

    Parameters:
    - **query**: Search term (company name or symbol)
    - **limit**: Maximum number of results (1-100, default: 10)

    Returns:
    - List of matching companies and symbols:
        - symbol
        - name
        - exchange
        - type
        - region

    Examples:
    ```
    /stocks/market/search?query=Apple
    /stocks/market/search?query=GOOG&limit=5
    ```

    Notes:
    - Searches both company names and symbols
    - Results are ordered by relevance
    - Includes partial matches

    Raises:
    - **422**: Invalid query parameter
    - **429**: MarketStack API rate limit exceeded
    """
    async with StockService(db) as stock_service:
        return await stock_service.search_symbols(query, limit or 10)  # Default to 10 if None

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days or 365)  # Default to 365 if None
    
    async with MarketDataService() as market_service:
        data = await market_service.get_dividends(symbol, start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail="Dividend data not found")
        return data

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days or 365)  # Default to 365 if None
    
    async with MarketDataService() as market_service:
        data = await market_service.get_splits(symbol, start_date, end_date)
        if not data:
            raise HTTPException(status_code=404, detail="Split data not found")
        return data 