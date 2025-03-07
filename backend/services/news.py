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
    """Service for fetching financial news articles using Serper.dev Google Search API."""
    
    def __init__(self):
        """Initialize NewsService with API configuration."""
        self.api_key = settings.serper_api_key
        self.base_url = "https://google.serper.dev/news"
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
                - link: URL to full article
                - snippet: Article snippet/description
                - source: Source name
                - date: Publication date
                - imageUrl: URL to article image (if available)
                
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

        # Format date range for Google search
        date_range = f"after:{from_date} before:{to_date}"
        search_query = f"{query} {date_range}"

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "q": search_query,
            "gl": "us",  # Set to US results
            "hl": language,
            "num": min(page_size, 100)  # Ensure we don't exceed API limit
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0  # 10 second timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # Transform Serper.dev response to our standard format
                articles = []
                for news in data.get("news", []):
                    article = {
                        "title": news.get("title"),
                        "url": news.get("link"),
                        "description": news.get("snippet"),
                        "source": news.get("source"),
                        "publishedAt": news.get("date"),
                        "imageUrl": news.get("imageUrl"),
                        "content": news.get("snippet")  # Use snippet as content
                    }
                    articles.append(article)
                
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

    async def fetch_industry_news(
        self,
        industry: str,
        from_date: str,
        to_date: str,
        language: str = "en",
        page_size: int = 100
    ) -> List[Dict[str, any]]:
        """Fetch industry-wide news articles.
        
        Args:
            industry: Industry sector (e.g., 'biotech', 'pharmaceutical')
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            language: Article language (default: "en")
            page_size: Number of articles to return (default: 100)
            
        Returns:
            List[Dict[str, any]]: Filtered list of relevant industry news
        """
        # Create an industry-focused search query
        search_terms = [
            f"{industry} industry news",
            "financial",
            "market",
            "-site:pinterest.com",  # Exclude certain sites
            "-site:facebook.com"
        ]
        query = " ".join(search_terms)
        
        articles = await self.fetch_news(query, from_date, to_date, language, page_size)
        
        # Filter articles for relevance
        filtered_articles = []
        relevant_terms = {
            industry.lower(),
            "market",
            "stock",
            "investor",
            "financial",
            "company",
            "research",
            "development"
        }
        
        for article in articles:
            title_lower = article["title"].lower()
            snippet_lower = article["description"].lower()
            
            # Check if article is relevant based on keyword matching
            if any(term in title_lower or term in snippet_lower for term in relevant_terms):
                filtered_articles.append(article)
        
        return filtered_articles

    async def fetch_company_news(
        self,
        company_name: str,
        ticker_symbol: str,
        from_date: str,
        to_date: str,
        language: str = "en",
        page_size: int = 100
    ) -> List[Dict[str, any]]:
        """Fetch company-specific news articles.
        
        Args:
            company_name: Company name
            ticker_symbol: Stock ticker symbol
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            language: Article language (default: "en")
            page_size: Number of articles to return (default: 100)
            
        Returns:
            List[Dict[str, any]]: Filtered list of relevant company news
        """
        # Create a company-focused search query
        search_terms = [
            f'"{company_name}"',  # Exact match for company name
            ticker_symbol,
            "(stock OR investor OR financial OR earnings OR research)",
            "-site:pinterest.com",
            "-site:facebook.com"
        ]
        query = " ".join(search_terms)
        
        articles = await self.fetch_news(query, from_date, to_date, language, page_size)
        
        # Filter articles for relevance
        filtered_articles = []
        company_terms = {
            company_name.lower(),
            ticker_symbol.lower(),
            "stock",
            "investor",
            "earnings",
            "research",
            "clinical",
            "trial",
            "fda",
            "approval",
            "pipeline"
        }
        
        for article in articles:
            title_lower = article["title"].lower()
            snippet_lower = article["description"].lower()
            
            # Check if article mentions company and is business/finance related
            if ((company_name.lower() in title_lower or ticker_symbol.lower() in title_lower) and
                any(term in title_lower or term in snippet_lower for term in company_terms)):
                filtered_articles.append(article)
        
        return filtered_articles

    @cache_result(prefix="news", expire=3600)  # Cache for 1 hour
    async def fetch_competitor_news(
        self,
        companies: List[Dict[str, str]],  # List of {name, symbol} dicts
        from_date: str,
        to_date: str,
        language: str = "en",
        page_size: int = 100
    ) -> Dict[str, List[Dict[str, any]]]:
        """Fetch news for multiple competing companies.
        
        Args:
            companies: List of company dictionaries with 'name' and 'symbol' keys
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            language: Article language (default: "en")
            page_size: Number of articles per company (default: 100)
            
        Returns:
            Dict[str, List[Dict[str, any]]]: Dictionary of company symbols to their news articles
        """
        results = {}
        
        for company in companies:
            company_news = await self.fetch_company_news(
                company["name"],
                company["symbol"],
                from_date,
                to_date,
                language,
                page_size
            )
            results[company["symbol"]] = company_news
        
        return results

    async def fetch_initial_company_news(
        self,
        db: Session,
        company_name: str,
        ticker_symbol: str,
        days_back: int = 30  # Get last 30 days of news by default
    ) -> List[NewsArticle]:
        """Fetch and store initial news articles when a company is tracked.
        
        Args:
            db: Database session
            company_name: Company name
            ticker_symbol: Stock ticker symbol
            days_back: Number of days of historical news to fetch
            
        Returns:
            List[NewsArticle]: Stored news articles
        """
        from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        to_date = datetime.utcnow().strftime('%Y-%m-%d')

        # Create focused search query for company
        search_terms = [
            f'"{company_name}"',  # Exact match for company name
            ticker_symbol,
            "(stock OR investor OR financial OR earnings OR research OR clinical OR trial OR FDA)",
            "when:30d",  # Last 30 days
            "-site:pinterest.com",
            "-site:facebook.com"
        ]
        query = " ".join(search_terms)

        try:
            # Fetch news articles
            articles = await self.fetch_news(query, from_date, to_date, page_size=50)
            
            # Store articles and create company mentions
            stored_articles = []
            for article in articles:
                # Check if article already exists
                existing_article = db.query(NewsArticle).filter(
                    NewsArticle.url == article["url"]
                ).first()
                
                if existing_article:
                    stored_articles.append(existing_article)
                    continue

                # Create new article
                news_item = NewsArticle(
                    title=article["title"],
                    url=article["url"],
                    source=article["source"],
                    published_at=datetime.fromisoformat(article["publishedAt"].replace('Z', '+00:00')),
                    content=article["content"]
                )
                db.add(news_item)
                
                # Create company mention
                mention = NewsCompanyMention(
                    article=news_item,
                    company_symbol=ticker_symbol
                )
                db.add(mention)
                
                stored_articles.append(news_item)

            db.commit()
            
            # Calculate sentiment scores for new articles
            for article in stored_articles:
                if not article.sentiment_score:  # Only if not already calculated
                    sentiment = self.analyze_sentiment(article)
                    if sentiment is not None:
                        article.sentiment_score = sentiment
            
            db.commit()
            
            logger.info(
                f"Stored {len(stored_articles)} initial news articles for {company_name} ({ticker_symbol})"
            )
            
            return stored_articles

        except Exception as e:
            logger.error(f"Error fetching initial news for {company_name}: {str(e)}")
            db.rollback()
            raise

    async def update_tracked_company_news(
        self,
        db: Session,
        company_name: str,
        ticker_symbol: str
    ) -> List[NewsArticle]:
        """Update news articles for a tracked company.
        
        Args:
            db: Database session
            company_name: Company name
            ticker_symbol: Stock ticker symbol
            
        Returns:
            List[NewsArticle]: Newly stored news articles
        """
        # Get the timestamp of the most recent article
        latest_article = db.query(NewsArticle)\
            .join(NewsCompanyMention)\
            .filter(NewsCompanyMention.company_symbol == ticker_symbol)\
            .order_by(NewsArticle.published_at.desc())\
            .first()

        from_date = latest_article.published_at.strftime('%Y-%m-%d') if latest_article else \
                   (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
        to_date = datetime.utcnow().strftime('%Y-%m-%d')

        # Only fetch if there might be new articles
        if from_date != to_date:
            return await self.fetch_initial_company_news(db, company_name, ticker_symbol, days_back=7)
        
        return []

    def analyze_sentiment(self, article: NewsArticle) -> Optional[float]:
        """Calculate sentiment score for an article.
        
        Args:
            article: NewsArticle object
            
        Returns:
            Optional[float]: Sentiment score between -1 and 1, or None if no content
        """
        if not article.content:
            return None
            
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(article.content)
        return sentiment["compound"] 