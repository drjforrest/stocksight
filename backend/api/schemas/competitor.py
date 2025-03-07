from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CompetitorBase(BaseModel):
    symbol: str
    name: str
    market_cap: Optional[float] = None
    revenue_ttm: Optional[float] = None
    r_and_d_expense: Optional[float] = None
    cash_position: Optional[float] = None
    burn_rate: Optional[float] = None
    pipeline_stage: Optional[str] = None
    therapeutic_area: Optional[str] = None
    primary_indication: Optional[str] = None
    key_products: Optional[str] = None

class CompetitorCreate(CompetitorBase):
    pass

class CompetitorResponse(CompetitorBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class CompetitorFinancialsBase(BaseModel):
    period_end_date: datetime
    revenue: Optional[float] = None
    r_and_d_expense: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    total_assets: Optional[float] = None
    total_debt: Optional[float] = None

class CompetitorFinancialsCreate(CompetitorFinancialsBase):
    competitor_id: int

class CompetitorFinancialsResponse(CompetitorFinancialsBase):
    id: int
    competitor_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CompetitorPatentBase(BaseModel):
    patent_number: str
    title: str
    filing_date: datetime
    grant_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    status: Optional[str] = None
    description: Optional[str] = None

class CompetitorPatentCreate(CompetitorPatentBase):
    competitor_id: int

class CompetitorPatentResponse(CompetitorPatentBase):
    id: int
    competitor_id: int
    created_at: datetime

    class Config:
        from_attributes = True 