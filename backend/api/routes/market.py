from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from services.market_data import MarketDataService
from api.schemas.market import MarketTrends, MarketMetrics, IPOInsights
from api.auth import get_current_user
from config.database import get_db

router = APIRouter(
    prefix="/market",
    tags=["market"],
    responses={
        404: {"description": "Resource not found"},
        429: {"description": "Too many requests to MarketStack API"}
    },
)

@router.get("/trends", response_model=MarketTrends)
async def get_market_trends(
    index: str = Query(..., description="Market index to analyze (e.g., BIOTECH)"),
    timeframe: str = Query("1m", description="Analysis timeframe (1d, 1w, 1m, 3m, 1y)")
):
    """Get market trends for a specific index and timeframe."""
    async with MarketDataService() as market_service:
        end_date = datetime.now()
        
        # Convert timeframe to days
        days = {
            "1d": 1,
            "1w": 7,
            "1m": 30,
            "3m": 90,
            "1y": 365
        }.get(timeframe, 30)
        
        start_date = end_date - timedelta(days=days)
        data = await market_service.get_index_data(index, start_date, end_date)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for index {index}")
        
        # Calculate trends
        return {
            "index": index,
            "timeframe": timeframe,
            "data": data,
            "trend_indicators": {
                "direction": "up" if data[-1]["close"] > data[0]["close"] else "down",
                "change_percent": ((data[-1]["close"] - data[0]["close"]) / data[0]["close"]) * 100,
                "volatility": calculate_volatility(data),
                "volume_trend": calculate_volume_trend(data)
            }
        }

@router.get("/metrics", response_model=MarketMetrics)
async def get_market_metrics(
    index: str = Query(..., description="Market index to analyze (e.g., BIOTECH)")
):
    """Get current market metrics for a specific index."""
    async with MarketDataService() as market_service:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Get last 30 days for calculations
        data = await market_service.get_index_data(index, start_date, end_date)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No metrics found for index {index}")
        
        return {
            "index": index,
            "timestamp": datetime.now(),
            "metrics": {
                "current_value": data[-1]["close"],
                "daily_change": data[-1]["close"] - data[-2]["close"],
                "daily_change_percent": ((data[-1]["close"] - data[-2]["close"]) / data[-2]["close"]) * 100,
                "volume": data[-1]["volume"],
                "moving_averages": calculate_moving_averages(data),
                "technical_indicators": calculate_technical_indicators(data)
            }
        }

@router.get("/ipo-insights", response_model=IPOInsights)
async def get_ipo_insights(
    timeframe: str = Query("90d", description="Analysis timeframe (30d, 90d, 180d, 1y)"),
    db: Session = Depends(get_db)
):
    """Get IPO insights and analysis for recent and upcoming IPOs."""
    async with MarketDataService() as market_service:
        # Convert timeframe to days
        days = {
            "30d": 30,
            "90d": 90,
            "180d": 180,
            "1y": 365
        }.get(timeframe.lower(), 90)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get IPO data from market service
        ipo_data = await market_service.get_ipo_data(start_date, end_date, db)
        
        if not ipo_data:
            raise HTTPException(status_code=404, detail="No IPO data found for the specified timeframe")
        
        return {
            "timeframe": timeframe,
            "recent_ipos": ipo_data.get("recent", []),
            "upcoming_ipos": ipo_data.get("upcoming", []),
            "market_analysis": {
                "total_offerings": len(ipo_data.get("recent", [])),
                "average_raise": calculate_average_raise(ipo_data.get("recent", [])),
                "sector_distribution": calculate_sector_distribution(ipo_data.get("recent", [])),
                "performance_metrics": calculate_ipo_performance(ipo_data.get("recent", []))
            }
        }

@router.get("/feature-flags")
async def get_feature_flags(current_user = Depends(get_current_user)):
    """Get feature flags configuration for the current user."""
    return {
        "features": {
            "advanced_charts": True,
            "real_time_data": True,
            "ai_insights": True,
            "beta_features": current_user.get("is_beta_user", False),
            "premium_features": current_user.get("is_premium", False)
        }
    }

# Helper functions for calculations
def calculate_volatility(data: List[dict]) -> float:
    """Calculate price volatility."""
    if not data:
        return 0.0
    prices = [d["close"] for d in data]
    returns = [(prices[i] - prices[i-1])/prices[i-1] for i in range(1, len(prices))]
    return (sum(r*r for r in returns) / len(returns)) ** 0.5 * 100

def calculate_volume_trend(data: List[dict]) -> str:
    """Calculate volume trend."""
    if not data:
        return "neutral"
    avg_volume = sum(d["volume"] for d in data) / len(data)
    recent_volume = sum(d["volume"] for d in data[-5:]) / 5
    if recent_volume > avg_volume * 1.1:
        return "increasing"
    elif recent_volume < avg_volume * 0.9:
        return "decreasing"
    return "neutral"

def calculate_moving_averages(data: List[dict]) -> dict:
    """Calculate various moving averages."""
    prices = [d["close"] for d in data]
    return {
        "ma_20": sum(prices[-20:]) / min(20, len(prices)),
        "ma_50": sum(prices[-50:]) / min(50, len(prices)),
        "ma_200": sum(prices[-200:]) / min(200, len(prices))
    }

def calculate_technical_indicators(data: List[dict]) -> dict:
    """Calculate basic technical indicators."""
    if not data:
        return {}
    
    prices = [d["close"] for d in data]
    return {
        "rsi": calculate_rsi(prices),
        "momentum": (prices[-1] - prices[0]) / prices[0] * 100 if prices[0] != 0 else 0,
        "price_range": {
            "high": max(d["high"] for d in data),
            "low": min(d["low"] for d in data)
        }
    }

def calculate_rsi(prices: List[float], periods: int = 14) -> float:
    """Calculate Relative Strength Index."""
    if len(prices) < periods + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-periods:]) / periods
    avg_loss = sum(losses[-periods:]) / periods
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_average_raise(ipos: List[dict]) -> float:
    """Calculate average IPO raise amount."""
    if not ipos:
        return 0.0
    return sum(ipo.get("raise_amount", 0) for ipo in ipos) / len(ipos)

def calculate_sector_distribution(ipos: List[dict]) -> dict:
    """Calculate sector distribution of IPOs."""
    sectors = {}
    for ipo in ipos:
        sector = ipo.get("sector", "Other")
        sectors[sector] = sectors.get(sector, 0) + 1
    return sectors

def calculate_ipo_performance(ipos: List[dict]) -> dict:
    """Calculate IPO performance metrics."""
    if not ipos:
        return {}
    
    return {
        "average_first_day_return": sum(ipo.get("first_day_return", 0) for ipo in ipos) / len(ipos),
        "above_offer_price": sum(1 for ipo in ipos if ipo.get("current_price", 0) > ipo.get("offer_price", 0)),
        "total_ipos": len(ipos)
    } 