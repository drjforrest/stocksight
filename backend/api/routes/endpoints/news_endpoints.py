from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, Column, select, inspect
from sqlalchemy.sql.expression import true
from typing import List
from datetime import datetime, timedelta

from config.database import get_db
from services.news import NewsFetcher, NewsImpactService
from models.news import (
    NewsArticle as NewsArticleModel,  # Rename to avoid conflict with Pydantic model
    NewsArticleCreate, NewsCompanyMention,
    NewsCompanyMentionCreate, NewsImpactAnalysis
)

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

@router.get("/latest/{symbol}")
async def get_latest_news(
    symbol: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Fetch and store latest news for a company symbol.
    
    Args:
        symbol: Company stock symbol
        days: Number of days to look back (default: 7)
        db: Database session
    """
    news_fetcher = NewsFetcher()
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    try:
        # Fetch news from external API
        articles = await news_fetcher.fetch_news(
            query=symbol,
            from_date=start_date.strftime("%Y-%m-%d"),
            to_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Store articles in database
        stored_articles = await news_fetcher.store_news(db, articles)
        
        # Create company mentions
        for article in stored_articles:
            mention = NewsCompanyMentionCreate(
                article_id=inspect(article).identity[0],
                company_symbol=symbol,
                relevance_score=1.0  # Default full relevance for direct symbol searches
            )
            db_mention = NewsCompanyMention(**mention.dict())
            db.add(db_mention)
        
        db.commit()
        
        return {"status": "success", "articles_count": len(stored_articles)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/impact/{symbol}")
def get_news_impact(
    symbol: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get news impact analysis for a company.
    
    Args:
        symbol: Company stock symbol
        days: Number of days to analyze (default: 7)
        db: Database session
    """
    impact_service = NewsImpactService(db)
    result = impact_service.calculate_news_impact(symbol, days)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Not enough data for impact analysis"
        )
    
    return result

@router.get("/articles/{symbol}")
def get_company_articles(
    symbol: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get all news articles for a company.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Build the query using SQLAlchemy's expression language
    # type: ignore[reportGeneralTypeIssues]
    stmt = (
        select(NewsArticleModel)
        .join(NewsCompanyMention)
        .where(
            NewsCompanyMention.company_symbol == symbol,  # type: ignore[reportGeneralTypeIssues]
            NewsArticleModel.published_at >= cutoff_date  # type: ignore[reportGeneralTypeIssues]
        )
        .order_by(NewsArticleModel.published_at.desc())  # type: ignore[reportGeneralTypeIssues]
    )
    
    # Execute the query
    articles = db.execute(stmt).scalars().all()
    return articles 