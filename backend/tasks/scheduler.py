from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.sql import expression

from services.marketstack_client import MarketStackClient
from config.settings import get_settings
from models.stock import StockPrice, CompanyInfo
from models.competitor import Competitor
from models.ipo import IPOListing, IPOStatus
from config.database import SessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()

def get_db() -> Session:
    """Get a new database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

async def update_stock_prices():
    """Update real-time stock prices every 5 minutes"""
    db = get_db()
    try:
        async with MarketStackClient(settings.marketstack_api_key) as client:
            # Get all tracked stocks from settings
            tracked_stocks = settings.tracked_stocks
            if not isinstance(tracked_stocks, list):
                tracked_stocks = []
            
            symbols = [str(stock) for stock in tracked_stocks]
            
            # Fetch batch price updates
            price_data = await client.batch_real_time_prices(symbols)
            
            # Update database
            for symbol, data in price_data.items():
                stock_price = StockPrice(
                    symbol=symbol,
                    price=data['price'],
                    volume=data['volume'],
                    timestamp=datetime.fromisoformat(data['timestamp'])
                )
                db.add(stock_price)
            
            db.commit()
            logger.info(f"Updated prices for {len(symbols)} stocks")
            
    except Exception as e:
        logger.error(f"Error updating stock prices: {e}")
    finally:
        db.close()

async def update_company_info():
    """Update company information daily"""
    db = get_db()
    try:
        async with MarketStackClient(settings.marketstack_api_key) as client:
            tracked_stocks = settings.tracked_stocks
            if not isinstance(tracked_stocks, list):
                tracked_stocks = []
            
            symbols = [str(stock) for stock in tracked_stocks]
            
            for symbol in symbols:
                info = await client.get_company_info(symbol)
                company = CompanyInfo(
                    symbol=symbol,
                    name=info['name'],
                    market_cap=info['market_cap'],
                    sector=info['sector'],
                    industry=info['industry'],
                    # Add other relevant fields
                )
                db.merge(company)
            
            db.commit()
            logger.info(f"Updated company info for {len(symbols)} companies")
            
    except Exception as e:
        logger.error(f"Error updating company information: {e}")
    finally:
        db.close()

async def update_ipo_status():
    """Update IPO statuses daily"""
    db = get_db()
    try:
        # Get upcoming IPOs using select
        stmt = select(IPOListing).where(
            IPOListing.status == str(IPOStatus.UPCOMING)
        )
        upcoming_ipos = db.scalars(stmt).all()
            
        for ipo in upcoming_ipos:
            # Use select to get the expected_date value
            expected_date = db.scalar(select(ipo.expected_date))
            if expected_date is not None and expected_date <= datetime.utcnow():
                # Update status using update statement
                db.execute(
                    IPOListing.__table__.update()
                    .where(IPOListing.id == ipo.id)
                    .values(status=str(IPOStatus.COMPLETED))
                )
        
        db.commit()
        logger.info(f"Updated status for {len(upcoming_ipos)} IPOs")
        
    except Exception as e:
        logger.error(f"Error updating IPO statuses: {e}")
    finally:
        db.close()

def init_scheduler():
    """Initialize the scheduler with all tasks"""
    # Update stock prices every 5 minutes
    scheduler.add_job(
        update_stock_prices,
        CronTrigger(minute="*/5"),
        id="stock_price_update",
        replace_existing=True
    )
    
    # Update company info daily at midnight
    scheduler.add_job(
        update_company_info,
        CronTrigger(hour="0"),
        id="company_info_update",
        replace_existing=True
    )
    
    # Update IPO status daily at 1 AM
    scheduler.add_job(
        update_ipo_status,
        CronTrigger(hour="1"),
        id="ipo_status_update",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler initialized with all tasks") 