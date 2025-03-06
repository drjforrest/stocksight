from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

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
    """
    Get the current stock price for a given symbol
    """
    price_data = market_service.get_stock_price(symbol)
    if not price_data:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Save to database
    db_price = StockPrice(
        symbol=symbol,
        price=price_data["price"],
        timestamp=datetime.fromisoformat(price_data["timestamp"].replace('Z', '+00:00'))
    )
    db.add(db_price)
    db.commit()
    
    return price_data

@app.get("/stocks/{symbol}/history")
def get_stock_history(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get historical stock data for the specified number of days
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    historical_data = market_service.get_historical_data(symbol, start_date, end_date)
    return historical_data

@app.get("/stocks/{symbol}/info")
def get_stock_info(symbol: str, db: Session = Depends(get_db)):
    """
    Get company information for a given stock symbol
    """
    # Check if we have recent company info in database
    db_info = db.query(CompanyInfo).filter(CompanyInfo.symbol == symbol).first()
    
    if db_info and (datetime.utcnow() - db_info.updated_at).days < 7:
        return db_info
    
    # Fetch new data from API
    company_data = market_service.get_company_info(symbol)
    if not company_data:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Update or create company info in database
    if db_info:
        db_info.name = company_data.get("name")
        db_info.exchange = company_data.get("exchange")
        db_info.country = company_data.get("country")
        db_info.sector = company_data.get("sector")
        db_info.updated_at = datetime.utcnow()
    else:
        db_info = CompanyInfo(
            symbol=symbol,
            name=company_data.get("name"),
            exchange=company_data.get("exchange"),
            country=company_data.get("country"),
            sector=company_data.get("sector")
        )
        db.add(db_info)
    
    db.commit()
    return company_data
