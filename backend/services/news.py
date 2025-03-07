from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os
import httpx
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np

from models.news import NewsArticle, NewsCompanyMention, NewsImpactAnalysis
from api.schemas.news import NewsArticleCreate, NewsCompanyMentionCreate, NewsImpactAnalysisCreate

# Download VADER lexicon for sentiment analysis
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

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
    def __init__(self, db: Session):
        self.db = db

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