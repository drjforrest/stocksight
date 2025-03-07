from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class TrendIndicators(BaseModel):
    direction: str
    change_percent: float
    volatility: float
    volume_trend: str

class MarketTrends(BaseModel):
    index: str
    timeframe: str
    data: List[Dict]
    trend_indicators: TrendIndicators

class MovingAverages(BaseModel):
    ma_20: float
    ma_50: float
    ma_200: float

class PriceRange(BaseModel):
    high: float
    low: float

class TechnicalIndicators(BaseModel):
    rsi: float
    momentum: float
    price_range: PriceRange

class MarketMetrics(BaseModel):
    index: str
    timestamp: datetime
    metrics: Dict[str, float | Dict | int]

class IPOPerformanceMetrics(BaseModel):
    average_first_day_return: float
    above_offer_price: int
    total_ipos: int

class MarketAnalysis(BaseModel):
    total_offerings: int
    average_raise: float
    sector_distribution: Dict[str, int]
    performance_metrics: IPOPerformanceMetrics

class IPOInsights(BaseModel):
    timeframe: str
    recent_ipos: List[Dict]
    upcoming_ipos: List[Dict]
    market_analysis: MarketAnalysis

class FeatureFlags(BaseModel):
    features: Dict[str, bool] 