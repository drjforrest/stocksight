from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from api.schemas.competitor import (
    CompetitorCreate, CompetitorResponse,
    CompetitorFinancialsCreate, CompetitorFinancialsResponse,
    CompetitorPatentCreate, CompetitorPatentResponse
)
from services.competitor import CompetitorService
from config.database import get_db

router = APIRouter(
    prefix="/competitors",
    tags=["competitors"],
    responses={
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"}
    },
)

@router.get("/", response_model=List[CompetitorResponse])
async def list_competitors(
    therapeutic_area: Optional[str] = Query(None, description="Filter by therapeutic area"),
    pipeline_stage: Optional[str] = Query(None, description="Filter by pipeline stage"),
    db: Session = Depends(get_db)
):
    """
    List biotech competitors with optional filters.

    Parameters:
    - **therapeutic_area**: Optional filter by therapeutic area
    - **pipeline_stage**: Optional filter by pipeline stage

    Returns:
    - List of competitors with basic information
    """
    return await CompetitorService(db).list_competitors(therapeutic_area, pipeline_stage)

@router.get("/{symbol}", response_model=CompetitorResponse)
async def get_competitor(
    symbol: str = Path(..., description="Stock symbol of the competitor"),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific competitor.

    Parameters:
    - **symbol**: Stock symbol (e.g., MRNA, BNTX)

    Returns:
    - Detailed competitor information including financials and patents
    """
    return await CompetitorService(db).get_competitor(symbol)

@router.get("/{symbol}/financials", response_model=List[CompetitorFinancialsResponse])
async def get_competitor_financials(
    symbol: str = Path(..., description="Stock symbol of the competitor"),
    quarters: int = Query(4, gt=0, le=20, description="Number of quarters of data to return"),
    db: Session = Depends(get_db)
):
    """
    Get historical financial data for a competitor.

    Parameters:
    - **symbol**: Stock symbol
    - **quarters**: Number of quarters of data (1-20, default: 4)

    Returns:
    - List of quarterly financial metrics
    """
    return await CompetitorService(db).get_financials(symbol, quarters)

@router.get("/{symbol}/patents", response_model=List[CompetitorPatentResponse])
async def get_competitor_patents(
    symbol: str = Path(..., description="Stock symbol of the competitor"),
    status: Optional[str] = Query(None, description="Filter by patent status"),
    db: Session = Depends(get_db)
):
    """
    Get patent information for a competitor.

    Parameters:
    - **symbol**: Stock symbol
    - **status**: Optional filter by patent status

    Returns:
    - List of patents and their details
    """
    return await CompetitorService(db).get_patents(symbol, status)

@router.post("/", response_model=CompetitorResponse)
async def create_competitor(
    competitor: CompetitorCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new competitor entry.

    Parameters:
    - **competitor**: Competitor data including symbol, name, and other details

    Returns:
    - Created competitor information
    """
    return await CompetitorService(db).create_competitor(competitor)

@router.post("/{symbol}/financials", response_model=CompetitorFinancialsResponse)
async def add_competitor_financials(
    symbol: str,
    financials: CompetitorFinancialsCreate,
    db: Session = Depends(get_db)
):
    """
    Add financial data for a competitor.

    Parameters:
    - **symbol**: Stock symbol
    - **financials**: Financial data for a specific period

    Returns:
    - Created financial record
    """
    return await CompetitorService(db).add_financials(symbol, financials)

@router.post("/{symbol}/patents", response_model=CompetitorPatentResponse)
async def add_competitor_patent(
    symbol: str,
    patent: CompetitorPatentCreate,
    db: Session = Depends(get_db)
):
    """
    Add patent information for a competitor.

    Parameters:
    - **symbol**: Stock symbol
    - **patent**: Patent data including number, title, and dates

    Returns:
    - Created patent record
    """
    return await CompetitorService(db).add_patent(symbol, patent)

@router.get("/analysis/market-share")
async def analyze_market_share(
    therapeutic_area: Optional[str] = Query(None, description="Filter by therapeutic area"),
    db: Session = Depends(get_db)
):
    """
    Analyze market share distribution among competitors.

    Parameters:
    - **therapeutic_area**: Optional filter by therapeutic area

    Returns:
    - Market share analysis including:
        - Revenue distribution
        - R&D investment comparison
        - Market cap distribution
    """
    return await CompetitorService(db).analyze_market_share(therapeutic_area)

@router.get("/analysis/pipeline-comparison")
async def compare_pipelines(
    symbols: List[str] = Query(..., description="List of competitor symbols to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare drug pipelines between competitors.

    Parameters:
    - **symbols**: List of stock symbols to compare

    Returns:
    - Pipeline comparison including:
        - Development stages
        - Therapeutic areas
        - Success rates
    """
    return await CompetitorService(db).compare_pipelines(symbols) 