export interface Competitor {
  id: number;
  symbol: string;
  name: string;
  market_cap: number;
  therapeutic_area: string;
  pipeline_stage: string;
  competitiveness_score?: number;
}

export interface FeatureFlags {
  competitor_score: boolean;
  competitorScoring: boolean;
} 