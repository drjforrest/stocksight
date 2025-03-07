from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from models.news import NewsArticle, NewsCompanyMention, NewsImpactAnalysis
from api.schemas.news import NewsArticleCreate, NewsCompanyMentionCreate, NewsImpactAnalysisCreate

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