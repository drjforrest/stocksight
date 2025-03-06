from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.config.database import Base

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class CompanyInfo(Base):
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    exchange = Column(String)
    country = Column(String)
    sector = Column(String)
    industry = Column(String)
    market_cap = Column(Float)
    employees = Column(Integer)
    website = Column(String)
    description = Column(String)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class DividendHistory(Base):
    __tablename__ = "dividend_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    amount = Column(Float)
    date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class StockSplit(Base):
    __tablename__ = "stock_splits"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    ratio = Column(String)  # Stored as string (e.g., "2:1")
    date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    country = Column(String)
    city = Column(String)
    timezone = Column(String)
    currency = Column(String)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 