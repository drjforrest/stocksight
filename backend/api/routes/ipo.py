from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.api.schemas.ipo import (
    IPOListingCreate, IPOListingResponse,
    IPOFinancialsCreate, IPOFinancialsResponse,
    IPOUpdateCreate, IPOUpdateResponse
)
from backend.services.ipo import IPOService
from backend.config.database import get_db
from backend.models.ipo import IPOStatus

router = APIRouter(
    prefix="/ipos",
    tags=["ipos"],
    responses={
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"}
    },
)

@router.get("/", response_model=List[IPOListingResponse])
async def list_ipos(
    status: Optional[IPOStatus] = Query(None, description="Filter by IPO status"),
    therapeutic_area: Optional[str] = Query(None, description="Filter by therapeutic area"),
    days_range: int = Query(90, gt=0, le=365, description="Number of days to look ahead/behind"),
    db: Session = Depends(get_db)
):
    """
    List biotech IPOs with optional filters.

    Parameters:
    - **status**: Optional filter by IPO status
    - **therapeutic_area**: Optional filter by therapeutic area
    - **days_range**: Days to look ahead/behind (1-365, default: 90)

    Returns:
    - List of IPO listings matching the criteria
    """
    return await IPOService(db).list_ipos(status, therapeutic_area, days_range)

@router.get("/upcoming", response_model=List[IPOListingResponse])
async def get_upcoming_ipos(
    days: int = Query(30, gt=0, le=180, description="Days to look ahead"),
    therapeutic_area: Optional[str] = Query(None, description="Filter by therapeutic area"),
    db: Session = Depends(get_db)
):
    """
    Get upcoming biotech IPOs.

    Parameters:
    - **days**: Number of days to look ahead (1-180, default: 30)
    - **therapeutic_area**: Optional filter by therapeutic area

    Returns:
    - List of upcoming IPOs with details
    """
    return await IPOService(db).get_upcoming_ipos(days, therapeutic_area)

@router.get("/{company_name}", response_model=IPOListingResponse)
async def get_ipo_details(
    company_name: str = Path(..., description="Name of the company"),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific IPO.

    Parameters:
    - **company_name**: Company name

    Returns:
    - Detailed IPO information including financials and updates
    """
    return await IPOService(db).get_ipo_details(company_name)

@router.post("/", response_model=IPOListingResponse)
async def create_ipo_listing(
    ipo: IPOListingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new IPO listing.

    Parameters:
    - **ipo**: IPO listing data including company details and offering information

    Returns:
    - Created IPO listing
    """
    return await IPOService(db).create_ipo_listing(ipo)

@router.post("/{company_name}/financials", response_model=IPOFinancialsResponse)
async def add_ipo_financials(
    company_name: str,
    financials: IPOFinancialsCreate,
    db: Session = Depends(get_db)
):
    """
    Add financial information for an IPO.

    Parameters:
    - **company_name**: Company name
    - **financials**: Financial data including revenue, R&D expenses, etc.

    Returns:
    - Created financial record
    """
    return await IPOService(db).add_financials(company_name, financials)

@router.post("/{company_name}/updates", response_model=IPOUpdateResponse)
async def add_ipo_update(
    company_name: str,
    update: IPOUpdateCreate,
    db: Session = Depends(get_db)
):
    """
    Add an update to an IPO listing.

    Parameters:
    - **company_name**: Company name
    - **update**: Update information including status changes, amendments

    Returns:
    - Created update record
    """
    return await IPOService(db).add_update(company_name, update)

@router.get("/analysis/success-rate")
async def analyze_ipo_success(
    timeframe_days: int = Query(365, gt=0, description="Analysis timeframe in days"),
    therapeutic_area: Optional[str] = Query(None, description="Filter by therapeutic area"),
    db: Session = Depends(get_db)
):
    """
    Analyze IPO success rates and performance metrics.

    Parameters:
    - **timeframe_days**: Analysis timeframe in days
    - **therapeutic_area**: Optional filter by therapeutic area

    Returns:
    - Success rate analysis including:
        - Completion rate
        - Average price performance
        - Market conditions correlation
    """
    return await IPOService(db).analyze_success_rate(timeframe_days, therapeutic_area)

@router.get("/analysis/pricing-trends")
async def analyze_pricing_trends(
    therapeutic_area: Optional[str] = Query(None, description="Filter by therapeutic area"),
    db: Session = Depends(get_db)
):
    """
    Analyze IPO pricing trends and valuation metrics.

    Parameters:
    - **therapeutic_area**: Optional filter by therapeutic area

    Returns:
    - Pricing trend analysis including:
        - Average valuation metrics
        - Price range trends
        - Market condition impacts
    """
    return await IPOService(db).analyze_pricing_trends(therapeutic_area) 