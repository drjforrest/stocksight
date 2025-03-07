from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class CompanyBrowseResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[Dict]

class CompanyInfoBase(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None
    therapeutic_area: Optional[str] = None

class CompanyInfoCreate(CompanyInfoBase):
    pass

class CompanyInfo(CompanyInfoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 