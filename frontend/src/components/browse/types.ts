export interface Company {
  symbol: string;
  name: string;
  market_cap: number;
  price: number;
  change_percent: number;
  active_trials?: number;
  fda_submissions?: number;
  approved_drugs: string[];
  therapeutic_areas?: string[];
}

export interface SearchFilters {
  marketCap?: string;
  hasApprovedDrugs?: boolean;
  therapeuticArea?: string;
  trialPhase?: string;
}

export interface CompareCompaniesProps {
  selectedCompanies: Company[];
  onRemoveCompany: (symbol: string) => void;
  onResetComparison: () => void;
}

export interface SearchBrowseProps {
  onAddToCompare: (company: Company) => void;
} 