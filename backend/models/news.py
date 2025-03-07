from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models.base import Base  

class NewsArticle(Base):
    """Model for storing biotech news articles with sentiment analysis."""
    __tablename__ = "news_articles"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)
    author = Column(String)
    published_at = Column(DateTime, nullable=False)
    content = Column(String)
    summary = Column(String)
    sentiment_score = Column(Float)  # Range from -1 (negative) to 1 (positive)
    sentiment_magnitude = Column(Float)  # Strength of sentiment
    companies_mentioned = Column(JSON)  # List of company symbols mentioned
    topics = Column(JSON)  # List of topics/categories
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    company_mentions = relationship("NewsCompanyMention", back_populates="article")
    impact_analyses = relationship("NewsImpactAnalysis", back_populates="article")

    def __repr__(self):
        return f"<NewsArticle(title='{self.title}', sentiment_score={self.sentiment_score})>"


class NewsCompanyMention(Base):
    """Model for tracking company mentions in news articles."""
    __tablename__ = "news_company_mentions"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('stocksight.news_articles.id'), nullable=False)
    company_symbol = Column(String, nullable=False)
    mention_count = Column(Integer, default=1)
    sentiment_context = Column(String)  # Context of the mention
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    article = relationship("NewsArticle", back_populates="company_mentions")

    def __repr__(self):
        return f"<NewsCompanyMention(company_symbol='{self.company_symbol}', mention_count={self.mention_count})>"


class NewsImpactAnalysis(Base):
    """Model for analyzing news impact on stock performance."""
    __tablename__ = "news_impact_analyses"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('stocksight.news_articles.id'), nullable=False)
    company_symbol = Column(String, nullable=False)
    price_before = Column(Float)
    price_after_1h = Column(Float)
    price_after_24h = Column(Float)
    volume_change_percent = Column(Float)
    correlation_score = Column(Float)  # Correlation between news and price movement
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    article = relationship("NewsArticle", back_populates="impact_analyses")

    def __repr__(self):
        return f"<NewsImpactAnalysis(company_symbol='{self.company_symbol}', correlation_score={self.correlation_score})>"


# Create indexes
Index('idx_news_published_at', NewsArticle.published_at)
Index('idx_news_sentiment_score', NewsArticle.sentiment_score)
Index('idx_news_company_mention', NewsCompanyMention.company_symbol)
Index('idx_news_impact_company', NewsImpactAnalysis.company_symbol)
Index('idx_news_impact_correlation', NewsImpactAnalysis.correlation_score) 