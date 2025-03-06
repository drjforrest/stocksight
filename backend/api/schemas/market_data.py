from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EODData(BaseModel):
    """End-of-day stock data."""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None

class EODResponse(BaseModel):
    """Response model for end-of-day data."""
    pagination: dict
    data: List[EODData]

class IntradayData(BaseModel):
    """Intraday stock data."""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    last: float
    close: float
    volume: int
    interval: str

class IntradayResponse(BaseModel):
    """Response model for intraday data."""
    pagination: dict
    data: List[IntradayData]

class Ticker(BaseModel):
    """Ticker information."""
    name: str
    symbol: str
    has_intraday: bool
    has_eod: bool
    country: Optional[str] = None
    stock_exchange: dict

class TickerResponse(BaseModel):
    """Response model for ticker data."""
    pagination: dict
    data: List[Ticker]

class Exchange(BaseModel):
    """Exchange information."""
    name: str
    acronym: str
    mic: str
    country: str
    country_code: str
    city: str
    website: Optional[str] = None
    timezone: dict

class ExchangeResponse(BaseModel):
    """Response model for exchange data."""
    pagination: dict
    data: List[Exchange]

class Dividend(BaseModel):
    """Dividend information."""
    symbol: str
    date: datetime
    dividend: float
    type: Optional[str] = None
    payment_date: Optional[datetime] = None

class DividendResponse(BaseModel):
    """Response model for dividend data."""
    pagination: dict
    data: List[Dividend]

class Split(BaseModel):
    """Stock split information."""
    symbol: str
    date: datetime
    split_factor: str
    before_shares: int
    after_shares: int

class SplitResponse(BaseModel):
    """Response model for split data."""
    pagination: dict
    data: List[Split]

class IndexData(BaseModel):
    """Index data."""
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class IndexResponse(BaseModel):
    """Response model for index data."""
    pagination: dict
    data: List[IndexData] 