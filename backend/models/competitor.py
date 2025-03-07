from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base

class Competitor(Base):
    """Model for storing biotech competitor information."""
    __tablename__ = "competitors"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    market_cap = Column(Float)
    revenue_ttm = Column(Float)  # Trailing twelve months revenue
    r_and_d_expense = Column(Float)  # Research and development expense
    cash_position = Column(Float)
    burn_rate = Column(Float)  # Monthly cash burn rate
    pipeline_stage = Column(String)  # e.g., "Phase 1", "Phase 2", "FDA Approved"
    therapeutic_area = Column(String)
    primary_indication = Column(String)
    key_products = Column(String)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    financials = relationship("CompetitorFinancials", back_populates="competitor")
    patents = relationship("CompetitorPatent", back_populates="competitor")

    def __repr__(self):
        return f"<Competitor(symbol='{self.symbol}', name='{self.name}')>"


class CompetitorFinancials(Base):
    """Model for storing detailed competitor financial metrics."""
    __tablename__ = "competitor_financials"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('stocksight.competitors.id'), nullable=False)
    period_end_date = Column(DateTime, nullable=False)
    revenue = Column(Float)
    r_and_d_expense = Column(Float)
    operating_income = Column(Float)
    net_income = Column(Float)
    eps = Column(Float)
    cash_and_equivalents = Column(Float)
    total_assets = Column(Float)
    total_debt = Column(Float)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    competitor = relationship("Competitor", back_populates="financials")

    def __repr__(self):
        return f"<CompetitorFinancials(competitor_id={self.competitor_id}, period_end_date='{self.period_end_date}')>"


class CompetitorPatent(Base):
    """Model for storing competitor patent information."""
    __tablename__ = "competitor_patents"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    competitor_id = Column(Integer, ForeignKey('stocksight.competitors.id'), nullable=False)
    patent_number = Column(String, nullable=False)
    title = Column(String, nullable=False)
    filing_date = Column(DateTime, nullable=False)
    grant_date = Column(DateTime)
    expiration_date = Column(DateTime)
    status = Column(String)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    competitor = relationship("Competitor", back_populates="patents")

    def __repr__(self):
        return f"<CompetitorPatent(patent_number='{self.patent_number}', title='{self.title}')>"

# Create indexes
Index('idx_competitor_therapeutic_area', Competitor.therapeutic_area)
Index('idx_competitor_pipeline_stage', Competitor.pipeline_stage)
Index('idx_competitor_financials_date', CompetitorFinancials.period_end_date)
Index('idx_patent_filing_date', CompetitorPatent.filing_date)
Index('idx_patent_expiration_date', CompetitorPatent.expiration_date) 