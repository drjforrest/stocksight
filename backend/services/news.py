from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
import httpx
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np
from fastapi import HTTPException
from .cache import CacheService, cache_result
import logging
from config.settings import get_settings

from models.news import NewsArticle, NewsCompanyMention, NewsImpactAnalysis
from api.schemas.news import NewsArticleCreate, NewsCompanyMentionCreate, NewsImpactAnalysisCreate

# Download VADER lexicon for sentiment analysis
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)
settings = get_settings()

class NewsFetcher:
    """Service for fetching financial news from external sources."""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"

    async def fetch_news(self, query: str, from_date: str, to_date: str) -> List[Dict]:
        """
        Fetch latest financial news articles.
        
        Args:
            query: Search query (e.g., company name or symbol)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of news articles
        """
        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "language": "en",
            "apiKey": self.api_key,
            "sortBy": "publishedAt"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("articles", [])

    async def store_news(self, db: Session, articles: List[Dict]) -> List[NewsArticle]:
        """
        Save news articles in the database.
        
        Args:
            db: Database session
            articles: List of news articles from the API
            
        Returns:
            List of created NewsArticle objects
        """
        stored_articles = []
        for article in articles:
            news_item = NewsArticle(
                title=article["title"],
                url=article["url"],
                source=article["source"]["name"],
                published_at=datetime.fromisoformat(article["publishedAt"].replace('Z', '+00:00')),
                content=article.get("content")
            )
            db.add(news_item)
            stored_articles.append(news_item)
        
        db.commit()
        return stored_articles

class NewsImpactService:
    """Service for analyzing sentiment and correlating with stock price changes."""

    def __init__(self, db: Session):
        self.db = db
        self.sia = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, article: NewsArticle) -> Optional[float]:
        """
        Calculate sentiment score of a news article.
        
        Args:
            article: NewsArticle object
            
        Returns:
            Compound sentiment score between -1 and 1, or None if no content
        """
        if not article.content:
            return None
        
        sentiment = self.sia.polarity_scores(article.content)
        return sentiment["compound"]

    def calculate_news_impact(self, company_symbol: str, days: int = 7) -> Optional[NewsImpactAnalysis]:
        """
        Compute impact score by correlating sentiment with stock price changes.
        
        Args:
            company_symbol: Stock symbol to analyze
            days: Number of days to look back
            
        Returns:
            NewsImpactAnalysis object or None if insufficient data
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get relevant news articles
        news_articles = self.db.query(NewsArticle)\
            .join(NewsArticle.mentions)\
            .filter(NewsArticle.published_at >= cutoff_date)\
            .all()

        if not news_articles:
            return None

        # Calculate sentiment scores
        sentiment_scores = [
            score for article in news_articles
            if (score := self.analyze_sentiment(article)) is not None
        ]

        if len(sentiment_scores) < 3:  # Need minimum data points for correlation
            return None

        # TODO: Add stock price correlation when price data is available
        # For now, we'll just use the average sentiment as the impact score
        avg_sentiment = np.mean(sentiment_scores)
        
        # Create and store the analysis
        analysis = NewsImpactAnalysis(
            company_symbol=company_symbol,
            avg_sentiment=avg_sentiment,
            price_impact_correlation=0.0,  # Will be updated when price data is available
            impact_score=abs(avg_sentiment) * 100  # Scale to 0-100 range
        )
        
        self.db.add(analysis)
        self.db.commit()
        
        return analysis

class NewsService:
    """Service for fetching financial news articles from NewsAPI."""
    
    def __init__(self):
        """Initialize NewsService with API configuration."""
        self.api_key = settings.newsapi_key
        self.base_url = "https://newsapi.org/v2/everything"
        self.cache = CacheService()

    def _validate_dates(self, from_date: str, to_date: str) -> tuple[datetime, datetime]:
        """Validate and parse date strings.
        
        Args:
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            Tuple of parsed datetime objects
            
        Raises:
            HTTPException: If dates are invalid or if to_date is before from_date
        """
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            
            if to_dt < from_dt:
                raise HTTPException(
                    status_code=400,
                    detail="End date must be after start date"
                )
                
            return from_dt, to_dt
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    @cache_result(prefix="news", expire=3600)  # Cache for 1 hour
    async def fetch_news(
        self,
        query: str,
        from_date: str,
        to_date: str,
        language: str = "en",
        page_size: int = 100
    ) -> List[Dict[str, any]]:
        """Fetch financial news articles with caching and error handling.
        
        Args:
            query: Search query (e.g., company name or symbol)
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            language: Article language (default: "en")
            page_size: Number of articles to return (default: 100, max: 100)
            
        Returns:
            List[Dict[str, any]]: List of news articles, each containing:
                - title: Article title
                - description: Article description or summary
                - url: URL to full article
                - urlToImage: URL to article image (if available)
                - publishedAt: Publication date and time
                - source: Dictionary containing source name and id
                - author: Article author (if available)
                - content: Partial article content
                
        Raises:
            HTTPException: On API errors or invalid parameters
        """
        # Validate dates
        self._validate_dates(from_date, to_date)
        
        # Validate query
        if not query.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty"
            )

        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "language": language,
            "apiKey": self.api_key,
            "sortBy": "publishedAt",
            "pageSize": min(page_size, 100)  # Ensure we don't exceed API limit
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=10.0  # 10 second timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # Check for API-level errors
                if data.get("status") == "error":
                    raise HTTPException(
                        status_code=500,
                        detail=data.get("message", "News API error")
                    )
                
                articles = data.get("articles", [])
                
                # Log article count for monitoring
                logger.info(
                    f"Retrieved {len(articles)} articles for query '{query}' "
                    f"from {from_date} to {to_date}"
                )
                
                return articles

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching news for query '{query}'")
            raise HTTPException(
                status_code=504,
                detail="News API request timed out"
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} fetching news: {str(e)}")
            if e.response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="News API error"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )

    async def store_news(self, db: Session, articles: List[Dict]) -> List[NewsArticle]:
        """
        Save news articles in the database.
        
        Args:
            db: Database session
            articles: List of news articles from the API
            
        Returns:
            List of created NewsArticle objects
        """
        stored_articles = []
        for article in articles:
            news_item = NewsArticle(
                title=article["title"],
                url=article["url"],
                source=article["source"]["name"],
                published_at=datetime.fromisoformat(article["publishedAt"].replace('Z', '+00:00')),
                content=article.get("content")
            )
            db.add(news_item)
            stored_articles.append(news_item)
        
        db.commit()
        return stored_articles

    async def list_news(self, days: int, company_symbol: Optional[str], min_sentiment: Optional[float]):
        query = self.db.query(NewsArticle)
        if company_symbol:
            query = query.join(NewsCompanyMention).filter(NewsCompanyMention.company_symbol == company_symbol)
        if min_sentiment is not None:
            query = query.filter(NewsArticle.sentiment_score >= min_sentiment)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return query.filter(NewsArticle.published_at >= cutoff_date).all()

    async def get_sentiment_trends(self, company_symbol: Optional[str], days: int):
        # Implementation for sentiment trends analysis
        pass

    async def get_company_mentions(self, company_symbol: str, days: int):
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(NewsCompanyMention)\
            .join(NewsArticle)\
            .filter(NewsCompanyMention.company_symbol == company_symbol)\
            .filter(NewsArticle.published_at >= cutoff_date)\
            .all()

    async def analyze_news_impact(self, company_symbol: str, days: int):
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(NewsImpactAnalysis)\
            .join(NewsArticle)\
            .filter(NewsImpactAnalysis.company_symbol == company_symbol)\
            .filter(NewsArticle.published_at >= cutoff_date)\
            .all()

    async def create_article(self, article: NewsArticleCreate):
        db_article = NewsArticle(**article.model_dump())
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article

    async def analyze_topics(self, days: int, company_symbol: Optional[str]):
        # Implementation for topic analysis
        pass

    async def compare_sentiment(self, symbols: List[str], days: int):
        # Implementation for sentiment comparison
        pass 