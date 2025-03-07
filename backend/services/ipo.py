from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException

from backend.models.ipo import IPOListing, IPOFinancials, IPOUpdate, IPOStatus
from backend.api.schemas.ipo import IPOListingCreate, IPOFinancialsCreate, IPOUpdateCreate

class IPOService:
    def __init__(self, db: Session):
        self.db = db

    async def list_ipos(self, status: Optional[IPOStatus], therapeutic_area: Optional[str], days_range: int):
        query = self.db.query(IPOListing)
        if status:
            query = query.filter(IPOListing.status == status)
        if therapeutic_area:
            query = query.filter(IPOListing.therapeutic_area == therapeutic_area)
        date_range = datetime.utcnow() - timedelta(days=days_range)
        return query.filter(IPOListing.filing_date >= date_range).all()

    async def get_upcoming_ipos(self, days: int, therapeutic_area: Optional[str]):
        query = self.db.query(IPOListing).filter(IPOListing.status == IPOStatus.UPCOMING)
        if therapeutic_area:
            query = query.filter(IPOListing.therapeutic_area == therapeutic_area)
        future_date = datetime.utcnow() + timedelta(days=days)
        return query.filter(IPOListing.expected_date <= future_date).all()

    async def get_ipo_details(self, company_name: str):
        ipo = self.db.query(IPOListing).filter(IPOListing.company_name == company_name).first()
        if not ipo:
            raise HTTPException(status_code=404, detail="IPO not found")
        return ipo

    async def create_ipo_listing(self, ipo: IPOListingCreate):
        db_ipo = IPOListing(**ipo.model_dump())
        self.db.add(db_ipo)
        self.db.commit()
        self.db.refresh(db_ipo)
        return db_ipo

    async def add_financials(self, company_name: str, financials: IPOFinancialsCreate):
        ipo = await self.get_ipo_details(company_name)
        db_financials = IPOFinancials(**financials.model_dump())
        self.db.add(db_financials)
        self.db.commit()
        self.db.refresh(db_financials)
        return db_financials

    async def add_update(self, company_name: str, update: IPOUpdateCreate):
        ipo = await self.get_ipo_details(company_name)
        db_update = IPOUpdate(**update.model_dump())
        self.db.add(db_update)
        self.db.commit()
        self.db.refresh(db_update)
        return db_update

    async def analyze_success_rate(self, timeframe_days: int, therapeutic_area: Optional[str]):
        # Implementation for success rate analysis
        pass

    async def analyze_pricing_trends(self, therapeutic_area: Optional[str]):
        # Implementation for pricing trends analysis
        pass 