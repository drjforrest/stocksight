from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict

class NewsArticleBase(BaseModel):
    title: str
    url: HttpUrl
    source: str
    author: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    companies_mentioned: Optional[List[str]] = None
    topics: Optional[List[str]] = None

class NewsArticleCreate(NewsArticleBase):
    published_at: datetime

class NewsArticleResponse(NewsArticleBase):
    id: int
    published_at: datetime
    sentiment_score: Optional[float] = None
    sentiment_magnitude: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NewsCompanyMentionBase(BaseModel):
    company_symbol: str
    mention_count: int = 1
    sentiment_context: Optional[str] = None

class NewsCompanyMentionCreate(NewsCompanyMentionBase):
    article_id: int

class NewsCompanyMentionResponse(NewsCompanyMentionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class NewsImpactAnalysisBase(BaseModel):
    company_symbol: str
    price_before: float
    price_after_1h: Optional[float] = None
    price_after_24h: Optional[float] = None
    volume_change_percent: Optional[float] = None
    correlation_score: Optional[float] = None

class NewsImpactAnalysisCreate(NewsImpactAnalysisBase):
    article_id: int

class NewsImpactAnalysisResponse(NewsImpactAnalysisBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 