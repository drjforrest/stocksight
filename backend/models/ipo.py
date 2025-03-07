from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from models.base import Base  

class IPOStatus(enum.Enum):
    """Enumeration for IPO status."""
    FILED = "Filed"
    UPCOMING = "Upcoming"
    COMPLETED = "Completed"
    WITHDRAWN = "Withdrawn"
    POSTPONED = "Postponed"

class IPOListing(Base):
    """Model for storing biotech IPO information."""
    __tablename__ = "ipo_listings"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    symbol = Column(String, unique=True, index=True)
    filing_date = Column(DateTime, nullable=False)
    expected_date = Column(DateTime)
    price_range_low = Column(Float)
    price_range_high = Column(Float)
    shares_offered = Column(Integer)
    initial_valuation = Column(Float)
    lead_underwriters = Column(String)
    status = Column(Enum(IPOStatus), nullable=False)
    therapeutic_area = Column(String)
    pipeline_stage = Column(String)
    primary_indication = Column(String)
    use_of_proceeds = Column(String)
    lock_up_period_days = Column(Integer)
    quiet_period_end_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    financials = relationship("IPOFinancials", back_populates="ipo", uselist=False)
    updates = relationship("IPOUpdate", back_populates="ipo")

    def __repr__(self):
        return f"<IPOListing(company_name='{self.company_name}', status='{self.status}')>"


class IPOFinancials(Base):
    """Model for storing IPO financial details."""
    __tablename__ = "ipo_financials"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    ipo_id = Column(Integer, ForeignKey('stocksight.ipo_listings.id'), unique=True, nullable=False)
    revenue_ttm = Column(Float)  # Trailing twelve months revenue
    net_income_ttm = Column(Float)
    r_and_d_expense_ttm = Column(Float)
    cash_position = Column(Float)
    burn_rate = Column(Float)
    total_assets = Column(Float)
    total_debt = Column(Float)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    ipo = relationship("IPOListing", back_populates="financials")

    def __repr__(self):
        return f"<IPOFinancials(ipo_id={self.ipo_id})>"


class IPOUpdate(Base):
    """Model for storing IPO status updates and amendments."""
    __tablename__ = "ipo_updates"
    __table_args__ = {'schema': 'stocksight'}

    id = Column(Integer, primary_key=True)
    ipo_id = Column(Integer, ForeignKey('stocksight.ipo_listings.id'), nullable=False)
    update_date = Column(DateTime, nullable=False)
    previous_status = Column(Enum(IPOStatus))
    new_status = Column(Enum(IPOStatus), nullable=False)
    price_range_change = Column(String)
    shares_offered_change = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    ipo = relationship("IPOListing", back_populates="updates")

    def __repr__(self):
        return f"<IPOUpdate(ipo_id={self.ipo_id}, update_date='{self.update_date}')>"

# Create indexes
Index('idx_ipo_filing_date', IPOListing.filing_date)
Index('idx_ipo_expected_date', IPOListing.expected_date)
Index('idx_ipo_status', IPOListing.status)
Index('idx_ipo_therapeutic_area', IPOListing.therapeutic_area)
Index('idx_ipo_update_date', IPOUpdate.update_date) 