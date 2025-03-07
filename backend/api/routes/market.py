from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta
import numpy as np
from ...models.market import MarketTrend, MarketMetric
from ...services.market_data import MarketDataService

router = APIRouter(prefix="/market", tags=["Market Data"])
market_service = MarketDataService()

@router.get("/trends")
async def get_market_trends(
    timeframe: str = Query("1m", regex="^(1d|1w|1m|3m|1y)$"),
    index: str = Query("BIOTECH", regex="^(BIOTECH|PHARMA|HEALTHCARE)$")
) -> List[MarketTrend]:
    """
    Get market trend data for specified timeframe and index.
    Timeframes: 1d (1 day), 1w (1 week), 1m (1 month), 3m (3 months), 1y (1 year)
    """
    end_date = datetime.now()
    start_date = end_date - {
        "1d": timedelta(days=1),
        "1w": timedelta(weeks=1),
        "1m": timedelta(days=30),
        "3m": timedelta(days=90),
        "1y": timedelta(days=365),
    }[timeframe]
    
    return await market_service.get_market_trends(index, start_date, end_date)

@router.get("/metrics")
async def get_market_metrics(
    index: str = Query("BIOTECH", regex="^(BIOTECH|PHARMA|HEALTHCARE)$")
) -> MarketMetric:
    """
    Get market metrics including volatility, moving average, and trend direction.
    """
    trends = await market_service.get_market_trends(
        index, 
        datetime.now() - timedelta(days=30),
        datetime.now()
    )
    
    # Calculate metrics
    values = [t.index_value for t in trends]
    
    volatility = np.std(values) / np.mean(values) * 100
    moving_avg = np.mean(values[-5:])  # 5-day moving average
    
    # Determine trend
    recent_change = (values[-1] - values[-5]) / values[-5] * 100
    trend = "up" if recent_change > 1 else "down" if recent_change < -1 else "neutral"
    
    return MarketMetric(
        volatility=volatility,
        moving_average=moving_avg,
        trend=trend
    ) 