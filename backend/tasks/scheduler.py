from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
from typing import List
from sqlalchemy.orm import Session

from services.marketstack_client import MarketStackClient
from config.settings import get_settings
from models.stock import StockPrice, CompanyInfo
from models.competitor import Competitor
from models.ipo import IPOListing, IPOStatus
from config.database import SessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()

async def update_stock_prices():
    """Update real-time stock prices every 5 minutes"""
    try:
        async with MarketStackClient(settings.marketstack_api_key) as client:
            # Get all tracked symbols
            symbols = [stock.symbol for stock in settings.tracked_stocks]
            
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
                # Add to database session
                settings.db.add(stock_price)
            
            settings.db.commit()
            logger.info(f"Updated prices for {len(symbols)} stocks")
            
    except Exception as e:
        logger.error(f"Error updating stock prices: {e}")

async def update_company_info():
    """Update company information daily"""
    try:
        async with MarketStackClient(settings.marketstack_api_key) as client:
            symbols = [comp.symbol for comp in settings.tracked_stocks]
            
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
                settings.db.merge(company)
            
            settings.db.commit()
            logger.info(f"Updated company info for {len(symbols)} companies")
            
    except Exception as e:
        logger.error(f"Error updating company information: {e}")

async def update_ipo_status():
    """Update IPO statuses daily"""
    try:
        # Get upcoming IPOs
        upcoming_ipos = settings.db.query(IPOListing)\
            .filter(IPOListing.status == IPOStatus.UPCOMING)\
            .all()
            
        for ipo in upcoming_ipos:
            if ipo.expected_date and ipo.expected_date <= datetime.utcnow():
                # Check if IPO completed
                # Update status accordingly
                ipo.status = IPOStatus.COMPLETED
                
        settings.db.commit()
        logger.info(f"Updated status for {len(upcoming_ipos)} IPOs")
        
    except Exception as e:
        logger.error(f"Error updating IPO statuses: {e}")

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