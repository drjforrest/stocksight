from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.config.database import get_db
from backend.models.tracked_company import TrackedCompany, TrackedCompanyCreate
from backend.services.news import NewsFetcher

router = APIRouter(
    prefix="/tracked",
    tags=["tracked"]
)

@router.post("/{user_id}/{symbol}")
async def add_tracked_company(
    user_id: int,
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Add a company to the user's tracked list.
    
    Args:
        user_id: ID of the user
        symbol: Company stock symbol
        db: Database session
    """
    # Check if already tracking
    existing = db.query(TrackedCompany).filter(
        TrackedCompany.user_id == user_id,
        TrackedCompany.company_symbol == symbol
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Already tracking {symbol}"
        )
    
    # Add to tracked companies
    tracked = TrackedCompany(user_id=user_id, company_symbol=symbol)
    db.add(tracked)
    
    # Fetch initial news
    news_fetcher = NewsFetcher()
    try:
        articles = await news_fetcher.fetch_news(
            query=symbol,
            from_date="2024-01-01",  # TODO: Make configurable
            to_date="2024-12-31"
        )
        await news_fetcher.store_news(db, articles)
    except Exception as e:
        # Log the error but don't fail the tracking
        print(f"Error fetching initial news for {symbol}: {e}")
    
    db.commit()
    return {"message": f"{symbol} added to tracked list"}

@router.delete("/{user_id}/{symbol}")
async def remove_tracked_company(
    user_id: int,
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Remove a company from the tracked list.
    
    Args:
        user_id: ID of the user
        symbol: Company stock symbol
        db: Database session
    """
    tracked = db.query(TrackedCompany).filter(
        TrackedCompany.user_id == user_id,
        TrackedCompany.company_symbol == symbol
    ).first()
    
    if not tracked:
        raise HTTPException(
            status_code=404,
            detail=f"Company {symbol} not found in tracking list"
        )
    
    db.delete(tracked)
    db.commit()
    return {"message": f"{symbol} removed from tracked list"}

@router.get("/{user_id}")
async def get_tracked_companies(
    user_id: int,
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Retrieve all companies the user is tracking.
    
    Args:
        user_id: ID of the user
        db: Database session
        
    Returns:
        List of company symbols
    """
    companies = db.query(TrackedCompany.company_symbol).filter(
        TrackedCompany.user_id == user_id
    ).all()
    
    return [company[0] for company in companies] 