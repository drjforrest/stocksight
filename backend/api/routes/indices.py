from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional

from ...services.market_data import MarketDataService

router = APIRouter(
    prefix="/indices",
    tags=["indices"],
    responses={404: {"description": "Not found"}},
)

# Create market data service instance
market_service = MarketDataService()

@router.get("/{index_symbol}")
async def get_index_data(
    index_symbol: str,
    days: int = Query(30, gt=0, le=365)
):
    """
    Get market index data.
    
    Analyze sector-wide performance by monitoring indices like the NASDAQ Biotechnology Index.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = await market_service.get_index_data(index_symbol, start_date, end_date)
    if not data:
        raise HTTPException(status_code=404, detail="Index data not found")
    return data 