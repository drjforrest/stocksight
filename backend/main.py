from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from config.database import get_db
from services.market_data import MarketDataService
from models.stock import StockPrice, CompanyInfo

app = FastAPI(title="StockSight API")
market_service = MarketDataService()

@app.get("/")
def read_root():
    return {"message": "Welcome to StockSight API"}

@app.get("/stocks/{symbol}/price")
def get_stock_price(symbol: str, db: Session = Depends(get_db)):
    """Get current stock price"""
    data = market_service.get_intraday_data(symbol, interval='1min')
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

@app.get("/stocks/{symbol}/history")
def get_stock_history(
    symbol: str,
    days: int = Query(30, gt=0, le=365),
    db: Session = Depends(get_db)
):
    """Get historical stock data"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    return market_service.get_eod_data(symbol, start_date, end_date)

@app.get("/stocks/{symbol}/info")
def get_stock_info(symbol: str, db: Session = Depends(get_db)):
    """Get company information"""
    db_info = db.query(CompanyInfo).filter(CompanyInfo.symbol == symbol).first()
    
    if db_info and (datetime.utcnow() - db_info.updated_at).days < 7:
        return db_info
    
    company_data = market_service.get_company_info(symbol)
    if not company_data:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if db_info:
        for key, value in company_data.items():
            setattr(db_info, key, value)
        db_info.updated_at = datetime.utcnow()
    else:
        db_info = CompanyInfo(**company_data)
        db.add(db_info)
    
    db.commit()
    return company_data

@app.get("/stocks/exchanges")
def get_exchanges():
    """Get list of stock exchanges"""
    exchanges = market_service.get_exchanges()
    if not exchanges:
        raise HTTPException(status_code=404, detail="No exchanges found")
    return exchanges

@app.get("/stocks/indices/{index_symbol}")
def get_index_data(
    index_symbol: str,
    days: int = Query(30, gt=0, le=365)
):
    """Get market index data"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    data = market_service.get_index_data(index_symbol, start_date, end_date)
    if not data:
        raise HTTPException(status_code=404, detail="Index data not found")
    return data

@app.get("/stocks/{symbol}/dividends")
def get_dividends(
    symbol: str,
    days: Optional[int] = Query(365, gt=0)
):
    """Get dividend information"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    data = market_service.get_dividends(symbol, start_date, end_date)
    if not data:
        raise HTTPException(status_code=404, detail="Dividend data not found")
    return data

@app.get("/stocks/{symbol}/splits")
def get_splits(
    symbol: str,
    days: Optional[int] = Query(365, gt=0)
):
    """Get stock split information"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    data = market_service.get_splits(symbol, start_date, end_date)
    if not data:
        raise HTTPException(status_code=404, detail="Split data not found")
    return data
