from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional

from models.stock import StockPrice, CompanyInfo, DividendHistory, StockSplit, Exchange
from api.schemas.stock import (
    StockPriceCreate, CompanyInfoCreate, DividendCreate,
    StockSplitCreate, ExchangeCreate, EODData, IntradayData,
    SymbolSearchResult
)
from services.market_data import MarketDataService

class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data = MarketDataService()

    async def cleanup(self):
        """Cleanup resources."""
        await self.market_data.cleanup()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def create_stock_price(self, price_data: StockPriceCreate) -> StockPrice:
        """Create a new stock price entry."""
        db_price = StockPrice(**price_data.model_dump())
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price

    async def get_stock_prices(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[StockPrice]:
        """Get stock prices for a symbol within a date range."""
        query = self.db.query(StockPrice).filter(StockPrice.symbol == symbol)
        
        if start_date:
            query = query.filter(StockPrice.timestamp >= start_date)
        if end_date:
            query = query.filter(StockPrice.timestamp <= end_date)
        
        return query.order_by(StockPrice.timestamp.desc()).all()

    async def create_company_info(self, company_data: CompanyInfoCreate) -> CompanyInfo:
        """Create or update company information."""
        db_company = self.db.query(CompanyInfo).filter(
            CompanyInfo.symbol == company_data.symbol
        ).first()

        if db_company:
            for key, value in company_data.model_dump().items():
                setattr(db_company, key, value)
        else:
            db_company = CompanyInfo(**company_data.model_dump())
            self.db.add(db_company)

        self.db.commit()
        self.db.refresh(db_company)
        return db_company

    async def get_company_info(self, symbol: str) -> CompanyInfo:
        """Get company information by symbol."""
        return self.db.query(CompanyInfo).filter(CompanyInfo.symbol == symbol).first()

    async def list_companies(
        self,
        sector: Optional[str] = None,
        country: Optional[str] = None
    ) -> List[CompanyInfo]:
        """List companies with optional filters."""
        query = self.db.query(CompanyInfo)
        
        if sector:
            query = query.filter(CompanyInfo.sector == sector)
        if country:
            query = query.filter(CompanyInfo.country == country)
        
        return query.order_by(CompanyInfo.symbol).all()

    async def create_dividend(self, dividend_data: DividendCreate) -> DividendHistory:
        """Create a new dividend record."""
        db_dividend = DividendHistory(**dividend_data.model_dump())
        self.db.add(db_dividend)
        self.db.commit()
        self.db.refresh(db_dividend)
        return db_dividend

    async def get_dividends(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[DividendHistory]:
        """Get dividend history for a symbol."""
        query = self.db.query(DividendHistory).filter(DividendHistory.symbol == symbol)
        
        if start_date:
            query = query.filter(DividendHistory.date >= start_date)
        if end_date:
            query = query.filter(DividendHistory.date <= end_date)
        
        return query.order_by(DividendHistory.date.desc()).all()

    async def create_stock_split(self, split_data: StockSplitCreate) -> StockSplit:
        """Create a new stock split record."""
        db_split = StockSplit(**split_data.model_dump())
        self.db.add(db_split)
        self.db.commit()
        self.db.refresh(db_split)
        return db_split

    async def get_stock_splits(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[StockSplit]:
        """Get stock split history for a symbol."""
        query = self.db.query(StockSplit).filter(StockSplit.symbol == symbol)
        
        if start_date:
            query = query.filter(StockSplit.date >= start_date)
        if end_date:
            query = query.filter(StockSplit.date <= end_date)
        
        return query.order_by(StockSplit.date.desc()).all()

    async def create_exchange(self, exchange_data: ExchangeCreate) -> Exchange:
        """Create or update exchange information."""
        db_exchange = self.db.query(Exchange).filter(
            Exchange.code == exchange_data.code
        ).first()

        if db_exchange:
            for key, value in exchange_data.model_dump().items():
                setattr(db_exchange, key, value)
        else:
            db_exchange = Exchange(**exchange_data.model_dump())
            self.db.add(db_exchange)

        self.db.commit()
        self.db.refresh(db_exchange)
        return db_exchange

    async def get_exchange(self, code: str) -> Exchange:
        """Get exchange information by code."""
        return self.db.query(Exchange).filter(Exchange.code == code).first()

    async def list_exchanges(self, country: Optional[str] = None) -> List[Exchange]:
        """List exchanges with optional country filter."""
        query = self.db.query(Exchange)
        
        if country:
            query = query.filter(Exchange.country == country)
        
        return query.order_by(Exchange.code).all()

    # Market Data Integration Methods
    async def get_eod_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[EODData]:
        """Get end-of-day data for a symbol."""
        return await self.market_data.get_eod_data(symbol, start_date, end_date)

    async def get_intraday_data(
        self,
        symbol: str,
        interval: str = "1min"
    ) -> List[IntradayData]:
        """Get intraday data for a symbol."""
        return await self.market_data.get_intraday_data(symbol, interval)

    async def search_symbols(
        self,
        query: str,
        limit: int = 10
    ) -> List[SymbolSearchResult]:
        """Search for symbols and companies."""
        # Search in local database first
        db_results = self.db.query(CompanyInfo).filter(
            or_(
                CompanyInfo.symbol.ilike(f"%{query}%"),
                CompanyInfo.name.ilike(f"%{query}%")
            )
        ).limit(limit).all()

        if db_results:
            return [
                SymbolSearchResult(
                    symbol=r.symbol,
                    name=r.name,
                    exchange=r.exchange,
                    type="stock",
                    currency="USD",  # You might want to get this from the exchange info
                    country=r.country
                ) for r in db_results
            ]

        # If no local results, search via MarketStack API
        return await self.market_data.search_symbols(query, limit) 