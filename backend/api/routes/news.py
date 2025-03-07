from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from api.schemas.news import (
    NewsArticleCreate, NewsArticleResponse,
    NewsCompanyMentionCreate, NewsCompanyMentionResponse,
    NewsImpactAnalysisCreate, NewsImpactAnalysisResponse
)
from services.news import NewsService
from config.database import get_db

router = APIRouter(
    prefix="/news",
    tags=["news"],
    responses={
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"}
    },
)

@router.get("/", response_model=List[NewsArticleResponse])
async def list_news(
    days: int = Query(7, gt=0, le=90, description="Number of days of news to return"),
    company_symbol: Optional[str] = Query(None, description="Filter by company symbol"),
    min_sentiment: Optional[float] = Query(None, ge=-1, le=1, description="Minimum sentiment score"),
    db: Session = Depends(get_db)
):
    """
    List biotech news articles with optional filters.

    Parameters:
    - **days**: Number of days of news (1-90, default: 7)
    - **company_symbol**: Optional filter by company
    - **min_sentiment**: Optional minimum sentiment score (-1 to 1)

    Returns:
    - List of news articles with sentiment analysis
    """
    return await NewsService(db).list_news(days, company_symbol, min_sentiment)

@router.get("/sentiment-trends", response_model=List[dict])
async def get_sentiment_trends(
    company_symbol: Optional[str] = Query(None, description="Filter by company symbol"),
    days: int = Query(30, gt=0, le=365, description="Analysis timeframe in days"),
    db: Session = Depends(get_db)
):
    """
    Get sentiment trends over time.

    Parameters:
    - **company_symbol**: Optional company symbol to analyze
    - **days**: Analysis timeframe (1-365, default: 30)

    Returns:
    - Daily sentiment trends including:
        - Average sentiment score
        - Sentiment volatility
        - Article volume
    """
    return await NewsService(db).get_sentiment_trends(company_symbol, days)

@router.get("/company-mentions", response_model=List[NewsCompanyMentionResponse])
async def get_company_mentions(
    company_symbol: str = Query(..., description="Company symbol to analyze"),
    days: int = Query(30, gt=0, le=365, description="Analysis timeframe in days"),
    db: Session = Depends(get_db)
):
    """
    Get news mentions for a specific company.

    Parameters:
    - **company_symbol**: Company symbol
    - **days**: Analysis timeframe (1-365, default: 30)

    Returns:
    - List of news mentions with context
    """
    return await NewsService(db).get_company_mentions(company_symbol, days)

@router.get("/impact-analysis", response_model=List[NewsImpactAnalysisResponse])
async def analyze_news_impact(
    company_symbol: str = Query(..., description="Company symbol to analyze"),
    days: int = Query(30, gt=0, le=365, description="Analysis timeframe in days"),
    db: Session = Depends(get_db)
):
    """
    Analyze the impact of news on stock performance.

    Parameters:
    - **company_symbol**: Company symbol
    - **days**: Analysis timeframe (1-365, default: 30)

    Returns:
    - News impact analysis including:
        - Price movement correlation
        - Volume changes
        - Sentiment correlation
    """
    return await NewsService(db).analyze_news_impact(company_symbol, days)

@router.post("/", response_model=NewsArticleResponse)
async def create_news_article(
    article: NewsArticleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new news article entry with sentiment analysis.

    Parameters:
    - **article**: News article data including URL, content, and metadata

    Returns:
    - Created article with sentiment analysis
    """
    return await NewsService(db).create_article(article)

@router.get("/topics")
async def analyze_news_topics(
    days: int = Query(30, gt=0, le=365, description="Analysis timeframe in days"),
    company_symbol: Optional[str] = Query(None, description="Filter by company symbol"),
    db: Session = Depends(get_db)
):
    """
    Analyze trending topics in biotech news.

    Parameters:
    - **days**: Analysis timeframe (1-365, default: 30)
    - **company_symbol**: Optional company filter

    Returns:
    - Topic analysis including:
        - Trending topics
        - Topic sentiment
        - Related companies
    """
    return await NewsService(db).analyze_topics(days, company_symbol)

@router.get("/sentiment-comparison")
async def compare_company_sentiment(
    symbols: List[str] = Query(..., description="List of company symbols to compare"),
    days: int = Query(30, gt=0, le=365, description="Analysis timeframe in days"),
    db: Session = Depends(get_db)
):
    """
    Compare sentiment analysis between companies.

    Parameters:
    - **symbols**: List of company symbols
    - **days**: Analysis timeframe (1-365, default: 30)

    Returns:
    - Sentiment comparison including:
        - Average sentiment scores
        - Sentiment trends
        - News volume comparison
    """
    return await NewsService(db).compare_sentiment(symbols, days) 