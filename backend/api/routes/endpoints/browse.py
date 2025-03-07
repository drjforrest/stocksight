from typing import Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from services.company_browse import CompanyBrowseService
from config.database import get_db

router = APIRouter()

@router.get("/therapeutic-areas")
async def get_therapeutic_areas(db: Session = Depends(get_db)):
    """Get list of all therapeutic areas."""
    browse_service = CompanyBrowseService(db)
    return await browse_service.get_therapeutic_areas()

@router.get("/companies")
async def browse_companies(
    therapeutic_area: Optional[str] = None,
    market_cap_min: Optional[float] = Query(None, description="Minimum market cap in billions"),
    market_cap_max: Optional[float] = Query(None, description="Maximum market cap in billions"),
    has_approved_drugs: Optional[bool] = None,
    phase: Optional[str] = Query(None, regex="^[1-4]$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Browse companies with filters.
    
    - **therapeutic_area**: Filter by therapeutic area
    - **market_cap_min**: Minimum market cap in billions
    - **market_cap_max**: Maximum market cap in billions
    - **has_approved_drugs**: Filter for companies with approved drugs
    - **phase**: Filter by clinical trial phase (1-4)
    - **page**: Page number (starts at 1)
    - **page_size**: Items per page (max 100)
    """
    browse_service = CompanyBrowseService(db)
    return await browse_service.browse_companies(
        therapeutic_area=therapeutic_area,
        market_cap_min=market_cap_min,
        market_cap_max=market_cap_max,
        has_approved_drugs=has_approved_drugs,
        phase=phase,
        page=page,
        page_size=page_size
    ) 