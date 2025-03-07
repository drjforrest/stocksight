from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from config.database import get_db
from services.company_data import CompanyDataService

router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)

# Initialize company data service
company_service = CompanyDataService()

@router.get("/{symbol}/figures")
async def get_company_figures(
    symbol: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get comprehensive company figures including:
    - Market data (price, volume)
    - Company information (market cap, industry)
    - FDA data (therapeutic areas, drug applications)
    - Competitor score
    
    Args:
        symbol: Company stock symbol
        db: Database session
    """
    try:
        figures = await company_service.get_company_figures(symbol)
        return {
            "symbol": figures.symbol,
            "name": figures.name,
            "competitor_score": figures.competitor_score,
            "market_cap": figures.market_cap,
            "price": figures.price,
            "volume": figures.volume,
            "therapeutic_area": figures.therapeutic_area,
            "drug_applications": figures.drug_applications
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching company figures: {str(e)}"
        ) 