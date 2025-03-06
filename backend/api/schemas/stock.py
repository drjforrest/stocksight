from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Stock Price Schemas
class StockPriceBase(BaseModel):
    symbol: str
    price: float
    timestamp: datetime

class StockPriceCreate(StockPriceBase):
    pass

class StockPriceResponse(StockPriceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Company Info Schemas
class CompanyInfoBase(BaseModel):
    symbol: str
    name: str
    exchange: str
    country: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    employees: Optional[int] = None
    website: Optional[str] = None
    description: Optional[str] = None

class CompanyInfoCreate(CompanyInfoBase):
    pass

class CompanyInfoResponse(CompanyInfoBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Dividend History Schemas
class DividendBase(BaseModel):
    symbol: str
    amount: float
    date: datetime

class DividendCreate(DividendBase):
    pass

class DividendResponse(DividendBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Stock Split Schemas
class StockSplitBase(BaseModel):
    symbol: str
    ratio: str
    date: datetime

class StockSplitCreate(StockSplitBase):
    pass

class StockSplitResponse(StockSplitBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Exchange Schemas
class ExchangeBase(BaseModel):
    code: str
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None

class ExchangeCreate(ExchangeBase):
    pass

class ExchangeResponse(ExchangeBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Market Data Response Schemas
class EODData(BaseModel):
    symbol: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None

class IntradayData(BaseModel):
    symbol: str
    timestamp: datetime
    price: float
    volume: int

class SymbolSearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str
    type: str = Field(description="Type of the security (e.g., stock, etf)")
    currency: str
    country: Optional[str] = None 