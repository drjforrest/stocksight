from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

from config.database import get_db
from models.tracked_company import TrackedCompany, TrackedCompanyCreate, TrackedCompanyResponse
from services.news import NewsService
from services.market_data import MarketDataService
from services.cache import CacheService

router = APIRouter(
    prefix="/tracked",
    tags=["tracked"]
)

# Initialize cache service
cache = CacheService()

async def check_refresh_rate_limit(symbol: str) -> bool:
    """Check if we can refresh news for this symbol (limit: once per 12 hours)."""
    cache_key = f"news_refresh:{symbol}"
    last_refresh = await cache.aget(cache_key)
    
    if last_refresh:
        return False
        
    # Set refresh timestamp with 12-hour expiry
    await cache.aset(cache_key, datetime.utcnow().isoformat(), expire=43200)  # 12 hours
    return True

@router.post("/{user_id}/{symbol}", response_model=TrackedCompanyResponse)
async def add_tracked_company(
    user_id: int,
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Add a company to the user's tracked list and fetch initial news.
    
    Args:
        user_id: ID of the user
        symbol: Company stock symbol
        db: Database session
        
    Returns:
        TrackedCompanyResponse: The newly created tracked company entry
        
    Raises:
        HTTPException: If company is already being tracked
    """
    # Check if already tracking using select
    stmt = select(TrackedCompany).where(
        and_(
            TrackedCompany.user_id == user_id,  # type: ignore[reportGeneralTypeIssues]
            TrackedCompany.company_symbol == symbol  # type: ignore[reportGeneralTypeIssues]
        )
    )
    existing = db.execute(stmt).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Already tracking {symbol}"
        )
    
    # Get company info first
    async with MarketDataService() as market_service:
        company_info = await market_service.get_company_info(symbol)
        if not company_info:
            raise HTTPException(
                status_code=404,
                detail=f"Company {symbol} not found"
            )
    
    # Create tracked company using schema
    tracked_data = TrackedCompanyCreate(user_id=user_id, company_symbol=symbol)
    tracked = TrackedCompany(**tracked_data.model_dump())
    db.add(tracked)
    
    # Fetch initial news
    news_service = NewsService(db=db)
    try:
        await news_service.fetch_initial_company_news(
            db=db,
            company_name=company_info["name"],
            ticker_symbol=symbol
        )
    except Exception as e:
        # Log the error but don't fail the tracking
        print(f"Error fetching initial news for {symbol}: {e}")
    
    db.commit()
    db.refresh(tracked)
    return tracked

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
    stmt = select(TrackedCompany).where(
        and_(
            TrackedCompany.user_id == user_id,  # type: ignore[reportGeneralTypeIssues]
            TrackedCompany.company_symbol == symbol  # type: ignore[reportGeneralTypeIssues]
        )
    )
    tracked = db.execute(stmt).scalar_one_or_none()
    
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
    stmt = select(TrackedCompany.company_symbol).where(
        TrackedCompany.user_id == user_id  # type: ignore[reportGeneralTypeIssues]
    )
    companies = db.execute(stmt).scalars().all()
    
    return [company for company in companies]

@router.post("/{user_id}/{symbol}/refresh")
async def refresh_company_news(
    user_id: int,
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Manually refresh news for a tracked company.
    Rate limited to once per 12 hours per symbol.
    
    Args:
        user_id: ID of the user
        symbol: Company stock symbol
        db: Database session
    """
    # Check rate limit
    can_refresh = await check_refresh_rate_limit(symbol)
    if not can_refresh:
        return JSONResponse(
            status_code=429,
            content={
                "message": "News refresh rate limit reached. Try again later.",
                "new_articles": 0
            }
        )
    
    # Verify company is tracked using select
    stmt = select(TrackedCompany).where(
        and_(
            TrackedCompany.user_id == user_id,  # type: ignore[reportGeneralTypeIssues]
            TrackedCompany.company_symbol == symbol  # type: ignore[reportGeneralTypeIssues]
        )
    )
    tracked = db.execute(stmt).scalar_one_or_none()
    
    if not tracked:
        raise HTTPException(
            status_code=404,
            detail=f"Company {symbol} not found in tracking list"
        )
    
    # Get company info
    async with MarketDataService() as market_service:
        company_info = await market_service.get_company_info(symbol)
        if not company_info:
            raise HTTPException(
                status_code=404,
                detail=f"Company {symbol} not found"
            )
    
    # Update news
    news_service = NewsService(db=db)
    try:
        new_articles = await news_service.update_tracked_company_news(
            db=db,
            company_name=company_info["name"],
            ticker_symbol=symbol
        )
        return {
            "message": f"Successfully refreshed news for {symbol}",
            "new_articles": len(new_articles)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refreshing news: {str(e)}"
        )

@router.get("/test/news/{symbol}")
async def test_company_news(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Test route to fetch news for a specific company using Serper.dev.
    Optimized for biotech companies like Abcellera with specific industry terms.
    
    Args:
        symbol: Company symbol (e.g., 'ABCL' for Abcellera)
        db: Database session
    """
    news_service = NewsService(db=db)
    try:
        # Construct search query based on company profile
        search_terms = [
            '"AbCellera"',           # Exact company name
            '"AbCellera Biologics"', # Full legal name
            'ABCL',                  # Stock symbol
            # Core business terms
            '(antibody OR "drug discovery" OR "therapeutic antibodies")',
            # Industry-specific terms
            '(biotech OR pharmaceutical OR "clinical trials" OR FDA)',
            # Technology terms
            '("AI platform" OR "artificial intelligence" OR "drug development")',
            # Location/company specific
            '("Vancouver" OR "Carl Hansen" OR "antibody discovery platform")',
            # Exclude irrelevant sources
            '-site:pinterest.com',
            '-site:facebook.com',
            '-site:instagram.com',
            '-site:linkedin.com'
        ]
        
        # Join terms with proper spacing and operators
        query = " ".join(search_terms)

        # Get last 30 days of news
        from_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        to_date = datetime.utcnow().strftime('%Y-%m-%d')

        articles = await news_service.fetch_news(
            query=query,
            from_date=from_date,
            to_date=to_date,
            page_size=30
        )

        # Process articles and calculate sentiment
        processed_articles = []
        for article in articles:
            # Calculate sentiment
            sentiment = None
            if article.get("content"):
                sentiment = news_service.analyze_sentiment(article["content"])

            # Enhanced article processing
            processed_article = {
                "title": article["title"],
                "url": article["url"],
                "source": article["source"],
                "published_at": article["publishedAt"],
                "snippet": article["description"],
                "sentiment_score": sentiment,
                "relevance_score": calculate_relevance_score(article, "AbCellera", "ABCL")
            }
            processed_articles.append(processed_article)

        # Sort by relevance score
        processed_articles.sort(key=lambda x: x["relevance_score"], reverse=True)

        return {
            "company": "AbCellera",
            "symbol": "ABCL",
            "total_articles": len(processed_articles),
            "articles": processed_articles
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching news: {str(e)}"
        )

def calculate_relevance_score(article: dict, company_name: str, ticker: str) -> float:
    """
    Calculate a relevance score for an article based on various factors.
    
    Args:
        article: The article dictionary
        company_name: Name of the company
        ticker: Stock ticker symbol
        
    Returns:
        float: Relevance score between 0 and 1
    """
    score = 0.0
    text = f"{article.get('title', '')} {article.get('description', '')}"
    
    # Check for company name mentions (case insensitive)
    if company_name.lower() in text.lower():
        score += 0.4
    
    # Check for ticker symbol (case sensitive)
    if ticker in text:
        score += 0.3
    
    # Check for key business terms
    key_terms = ["antibody", "drug discovery", "therapeutic", "clinical", "FDA"]
    for term in key_terms:
        if term.lower() in text.lower():
            score += 0.06  # Up to 0.3 for all terms
            
    return min(1.0, score)  # Cap at 1.0 