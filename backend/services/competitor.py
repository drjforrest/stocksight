from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from backend.models.competitor import Competitor, CompetitorFinancials, CompetitorPatent
from backend.api.schemas.competitor import CompetitorCreate, CompetitorFinancialsCreate, CompetitorPatentCreate

class CompetitorService:
    def __init__(self, db: Session):
        self.db = db

    async def list_competitors(self, therapeutic_area: Optional[str], pipeline_stage: Optional[str]):
        query = self.db.query(Competitor)
        if therapeutic_area:
            query = query.filter(Competitor.therapeutic_area == therapeutic_area)
        if pipeline_stage:
            query = query.filter(Competitor.pipeline_stage == pipeline_stage)
        return query.all()

    async def get_competitor(self, symbol: str):
        competitor = self.db.query(Competitor).filter(Competitor.symbol == symbol).first()
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        return competitor

    async def get_financials(self, symbol: str, quarters: int):
        competitor = await self.get_competitor(symbol)
        return self.db.query(CompetitorFinancials)\
            .filter(CompetitorFinancials.competitor_id == competitor.id)\
            .order_by(CompetitorFinancials.period_end_date.desc())\
            .limit(quarters)\
            .all()

    async def get_patents(self, symbol: str, status: Optional[str]):
        competitor = await self.get_competitor(symbol)
        query = self.db.query(CompetitorPatent)\
            .filter(CompetitorPatent.competitor_id == competitor.id)
        if status:
            query = query.filter(CompetitorPatent.status == status)
        return query.all()

    async def create_competitor(self, competitor: CompetitorCreate):
        db_competitor = Competitor(**competitor.model_dump())
        self.db.add(db_competitor)
        self.db.commit()
        self.db.refresh(db_competitor)
        return db_competitor

    async def add_financials(self, symbol: str, financials: CompetitorFinancialsCreate):
        competitor = await self.get_competitor(symbol)
        db_financials = CompetitorFinancials(**financials.model_dump())
        self.db.add(db_financials)
        self.db.commit()
        self.db.refresh(db_financials)
        return db_financials

    async def add_patent(self, symbol: str, patent: CompetitorPatentCreate):
        competitor = await self.get_competitor(symbol)
        db_patent = CompetitorPatent(**patent.model_dump())
        self.db.add(db_patent)
        self.db.commit()
        self.db.refresh(db_patent)
        return db_patent

    async def analyze_market_share(self, therapeutic_area: Optional[str]):
        # Implementation for market share analysis
        pass

    async def compare_pipelines(self, symbols: List[str]):
        # Implementation for pipeline comparison
        pass 