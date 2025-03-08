export interface TrackedCompany {
  symbol: string;
  name: string;
  market_cap: number;
  price: number;
  change_percent: number;
  active_trials?: number;
  fda_submissions?: number;
}

export interface TrackedCompaniesListProps {
  trackedCompanies: TrackedCompany[];
  onRemoveCompany: (symbol: string) => Promise<void>;
}

export interface MarketOverviewData {
  biotechIndex: number;
  biotechIndexChange: number;
  totalMarketCap: number;
  avgTrialCount: number;
  fdaApprovals: number;
} 