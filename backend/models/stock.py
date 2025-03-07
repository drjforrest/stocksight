from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class StockPrice(Base):
    """Model for storing stock price data."""
    __tablename__ = "stock_prices"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    company = relationship("CompanyInfo", back_populates="prices", foreign_keys=[symbol],
                         primaryjoin="StockPrice.symbol == CompanyInfo.symbol")

    def __repr__(self):
        return f"<StockPrice(symbol='{self.symbol}', price={self.price}, timestamp='{self.timestamp}')>"


class CompanyInfo(Base):
    """Model for storing company information."""
    __tablename__ = "company_info"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    country = Column(String)
    sector = Column(String)
    industry = Column(String)
    market_cap = Column(Float)
    employees = Column(Integer)
    website = Column(String)
    description = Column(String)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    prices = relationship("StockPrice", back_populates="company",
                        primaryjoin="CompanyInfo.symbol == StockPrice.symbol")
    dividends = relationship("DividendHistory", back_populates="company")
    splits = relationship("StockSplit", back_populates="company")

    def __repr__(self):
        return f"<CompanyInfo(symbol='{self.symbol}', name='{self.name}')>"


class DividendHistory(Base):
    """Model for storing dividend history."""
    __tablename__ = "dividend_history"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    symbol = Column(String, ForeignKey('stocksight.company_info.symbol'), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    company = relationship("CompanyInfo", back_populates="dividends")

    def __repr__(self):
        return f"<DividendHistory(symbol='{self.symbol}', amount={self.amount}, date='{self.date}')>"


class StockSplit(Base):
    """Model for storing stock split information."""
    __tablename__ = "stock_splits"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    symbol = Column(String, ForeignKey('stocksight.company_info.symbol'), index=True, nullable=False)
    ratio = Column(String, nullable=False)  # Stored as string (e.g., "2:1")
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    company = relationship("CompanyInfo", back_populates="splits")

    def __repr__(self):
        return f"<StockSplit(symbol='{self.symbol}', ratio='{self.ratio}', date='{self.date}')>"


class Exchange(Base):
    """Model for storing exchange information."""
    __tablename__ = "exchanges"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    country = Column(String)
    city = Column(String)
    timezone = Column(String)
    currency = Column(String)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Exchange(code='{self.code}', name='{self.name}')>"


# Create indexes
Index('idx_stock_price_symbol_timestamp', StockPrice.symbol, StockPrice.timestamp)
Index('idx_dividend_symbol_date', DividendHistory.symbol, DividendHistory.date)
Index('idx_split_symbol_date', StockSplit.symbol, StockSplit.date)
Index('idx_company_sector', CompanyInfo.sector)
Index('idx_company_country', CompanyInfo.country)
Index('idx_exchange_country', Exchange.country) 