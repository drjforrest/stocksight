from sqlalchemy.orm import Session
from models.competitor import Competitor    
import numpy as np

class CompetitorService:
    def __init__(self, db: Session):
        self.db = db

    async def list_competitors(self, therapeutic_area=None, pipeline_stage=None, include_score=True):
        """Fetch competitors and compute competitiveness score if enabled."""
        query = self.db.query(Competitor)

        if therapeutic_area:
            query = query.filter(Competitor.therapeutic_area == therapeutic_area)
        if pipeline_stage:
            query = query.filter(Competitor.pipeline_stage == pipeline_stage)

        competitors = query.all()
        results = []

        for competitor in competitors:
            score = self._calculate_competitiveness(
                competitor.market_cap,
                competitor.ipo_performance,
                competitor.volatility,
                competitor.r_and_d_spend,
                competitor.patent_count
            ) if include_score else None

            results.append({
                "symbol": competitor.symbol,
                "name": competitor.name,
                "market_cap": competitor.market_cap,
                "ipo_performance": competitor.ipo_performance,
                "volatility": competitor.volatility,
                "r_and_d_spend": competitor.r_and_d_spend,
                "patent_count": competitor.patent_count,
                "competitiveness_score": score,
            })

        return sorted(results, key=lambda x: x["competitiveness_score"] or 0, reverse=True)

    def _calculate_competitiveness(self, market_cap, ipo_perf, volatility, r_and_d, patents):
        """Generate a Competitiveness Score (0-100)."""
        weight_market_cap = 0.3
        weight_ipo_perf = 0.2
        weight_volatility = 0.2
        weight_r_and_d = 0.2
        weight_patents = 0.1

        norm_market_cap = np.log(market_cap + 1) / 10  
        norm_ipo_perf = (ipo_perf + 1) / 2  
        norm_volatility = (1 - min(volatility / 0.5, 1))  
        norm_r_and_d = np.log(r_and_d + 1) / 10  
        norm_patents = np.log(patents + 1) / 5  

        score = (
            (norm_market_cap * weight_market_cap) +
            (norm_ipo_perf * weight_ipo_perf) +
            (norm_volatility * weight_volatility) +
            (norm_r_and_d * weight_r_and_d) +
            (norm_patents * weight_patents)
        ) * 100

        return round(score, 1)