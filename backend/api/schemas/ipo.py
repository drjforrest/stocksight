from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.ipo import IPOStatus

class IPOListingBase(BaseModel):
    company_name: str
    symbol: Optional[str] = None
    filing_date: datetime
    expected_date: Optional[datetime] = None
    price_range_low: Optional[float] = None
    price_range_high: Optional[float] = None
    shares_offered: Optional[int] = None
    initial_valuation: Optional[float] = None
    lead_underwriters: Optional[str] = None
    status: IPOStatus
    therapeutic_area: Optional[str] = None
    pipeline_stage: Optional[str] = None
    primary_indication: Optional[str] = None
    use_of_proceeds: Optional[str] = None
    lock_up_period_days: Optional[int] = None
    quiet_period_end_date: Optional[datetime] = None

class IPOListingCreate(IPOListingBase):
    pass

class IPOListingResponse(IPOListingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IPOFinancialsBase(BaseModel):
    revenue_ttm: Optional[float] = None
    net_income_ttm: Optional[float] = None
    r_and_d_expense_ttm: Optional[float] = None
    cash_position: Optional[float] = None
    burn_rate: Optional[float] = None
    total_assets: Optional[float] = None
    total_debt: Optional[float] = None

class IPOFinancialsCreate(IPOFinancialsBase):
    ipo_id: int

class IPOFinancialsResponse(IPOFinancialsBase):
    id: int
    ipo_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class IPOUpdateBase(BaseModel):
    update_date: datetime
    previous_status: Optional[IPOStatus] = None
    new_status: IPOStatus
    price_range_change: Optional[str] = None
    shares_offered_change: Optional[str] = None
    notes: Optional[str] = None

class IPOUpdateCreate(IPOUpdateBase):
    ipo_id: int

class IPOUpdateResponse(IPOUpdateBase):
    id: int
    ipo_id: int
    created_at: datetime

    class Config:
        from_attributes = True 