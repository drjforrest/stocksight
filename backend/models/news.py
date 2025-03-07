from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from config.database import Base

# SQLAlchemy Models
class NewsArticle(Base):
    """Model for storing biotech news articles with sentiment analysis."""
    __tablename__ = "news_articles"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)
    author = Column(String)
    published_at = Column(DateTime, nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(String)
    sentiment_score = Column(Float, nullable=True)
    sentiment_magnitude = Column(Float)  # Strength of sentiment
    companies_mentioned = Column(JSON)  # List of company symbols mentioned
    topics = Column(JSON)  # List of topics/categories
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    mentions = relationship("NewsCompanyMention", back_populates="article")
    impact_analyses = relationship("NewsImpactAnalysis", back_populates="article")

    def __repr__(self):
        return f"<NewsArticle(title='{self.title}', sentiment_score={self.sentiment_score})>"


class NewsCompanyMention(Base):
    """Model for tracking company mentions in news articles."""
    __tablename__ = "news_company_mentions"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"))
    company_symbol = Column(String, nullable=False)
    relevance_score = Column(Float, nullable=False)
    mention_count = Column(Integer, default=1)
    sentiment_context = Column(String)  # Context of the mention
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    article = relationship("NewsArticle", back_populates="mentions")

    def __repr__(self):
        return f"<NewsCompanyMention(company_symbol='{self.company_symbol}', mention_count={self.mention_count})>"


class NewsImpactAnalysis(Base):
    """Model for analyzing news impact on stock performance."""
    __tablename__ = "news_impact_analysis"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True, index=True)
    company_symbol = Column(String, nullable=False)
    avg_sentiment = Column(Float, nullable=False)
    price_impact_correlation = Column(Float, nullable=False)
    impact_score = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    article = relationship("NewsArticle", back_populates="impact_analyses")

    def __repr__(self):
        return f"<NewsImpactAnalysis(company_symbol='{self.company_symbol}', avg_sentiment={self.avg_sentiment})>"


# Create indexes
Index('idx_news_published_at', NewsArticle.published_at)
Index('idx_news_sentiment_score', NewsArticle.sentiment_score)
Index('idx_news_company_mention', NewsCompanyMention.company_symbol)
Index('idx_news_impact_company', NewsImpactAnalysis.company_symbol)
Index('idx_news_impact_correlation', NewsImpactAnalysis.price_impact_correlation)

# Pydantic Schemas
class NewsArticleBase(BaseModel):
    title: str
    url: str
    source: str
    published_at: datetime
    content: Optional[str] = None
    sentiment_score: Optional[float] = None

class NewsArticleCreate(NewsArticleBase):
    pass

class NewsArticle(NewsArticleBase):
    id: int

    class Config:
        from_attributes = True

class NewsCompanyMentionBase(BaseModel):
    article_id: int
    company_symbol: str
    relevance_score: float

class NewsCompanyMentionCreate(NewsCompanyMentionBase):
    pass

class NewsCompanyMention(NewsCompanyMentionBase):
    id: int

    class Config:
        from_attributes = True

class NewsImpactAnalysisBase(BaseModel):
    company_symbol: str
    avg_sentiment: float
    price_impact_correlation: float
    impact_score: float

class NewsImpactAnalysisCreate(NewsImpactAnalysisBase):
    pass

class NewsImpactAnalysis(NewsImpactAnalysisBase):
    id: int

    class Config:
        from_attributes = True 