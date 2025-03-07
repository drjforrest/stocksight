import { api } from "./api";

// Types
export interface StockPrice {
  symbol: string;
  price: number;
  timestamp: string;
  change_percent?: number;
}

export interface IPOInsightsData {
  date: string;
  completion_rate: number;
  withdrawal_rate: number;
  avg_price_performance: number;
  therapeutic_area?: string;
  total_ipos: number;
  statistical_analysis?: {
    t_statistic: number;
    p_value: number;
    significant: boolean;
  };
}

export interface MarketTrendData {
  date: string;
  index_value: number;
  volume: number;
  change_percent: number;
}

export interface MarketMetrics {
  volatility: number;
  moving_average: number;
  trend: 'up' | 'down' | 'neutral';
}

export interface Competitor {
  symbol: string;
  name: string;
  therapeutic_area: string;
  market_cap: number;
}

export interface PipelineData {
  stages: {
    preclinical: number;
    phase_1: number;
    phase_2: number;
    phase_3: number;
  }[];
}

export interface MarketShareData {
  competitors: {
    name: string;
    market_share: number;
  }[];
}

export type TimeframeType = '1d' | '1w' | '1m' | '3m' | '1y';
export type IndexType = 'BIOTECH' | 'PHARMA' | 'HEALTHCARE';

// Tracked Companies Types
export interface TrackedCompany {
  id: number;
  user_id: number;
  company_symbol: string;
  added_at: string;
}

// API Functions
export async function getStockPrice(symbol: string): Promise<StockPrice> {
  try {
    const response = await api.get(`/stocks/${symbol}/price`);
    return response.data;
  } catch (error) {
    console.error("Error fetching stock price:", error);
    throw error;
  }
}

export async function getIPOInsights(params?: {
  timeframe?: '30d' | '90d' | '180d' | '365d';
  therapeutic_area?: string;
}): Promise<IPOInsightsData> {
  try {
    const response = await api.get('/ipo-insights', { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching IPO insights:", error);
    throw error;
  }
}

export async function getMarketTrends(params: {
  timeframe: TimeframeType;
  index: IndexType;
}): Promise<MarketTrendData[]> {
  try {
    const response = await api.get('/market/trends', { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching market trends:", error);
    throw error;
  }
}

export async function getMarketMetrics(index: IndexType): Promise<MarketMetrics> {
  try {
    const response = await api.get('/market/metrics', { params: { index } });
    return response.data;
  } catch (error) {
    console.error("Error fetching market metrics:", error);
    throw error;
  }
}

// Competitor Analysis Functions
export async function searchCompetitors(query: string): Promise<Competitor[]> {
  try {
    const response = await api.get('/competitors', { params: { query } });
    return response.data;
  } catch (error) {
    console.error("Error searching competitors:", error);
    throw error;
  }
}

export async function getPipelineComparison(symbols: string[]): Promise<PipelineData> {
  try {
    const response = await api.get('/competitors/analysis/pipeline-comparison', {
      params: { symbols }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching pipeline comparison:", error);
    throw error;
  }
}

export async function getMarketShare(therapeuticArea?: string): Promise<MarketShareData> {
  try {
    const response = await api.get('/competitors/analysis/market-share', {
      params: { therapeutic_area: therapeuticArea }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching market share data:", error);
    throw error;
  }
}

// Report Generation
export interface ReportRequest {
  selected_charts: string[];
  email?: string | null;
}

export interface ReportResponse {
  message: string;
  report_id?: string;
  download_url?: string;
}

export async function generateReport(data: ReportRequest): Promise<ReportResponse> {
  try {
    const response = await api.post('/generate-report', data);
    return response.data;
  } catch (error) {
    console.error("Error generating report:", error);
    throw error;
  }
}

// Batch data fetching
export async function getMarketData(index: IndexType) {
  try {
    const [trends, metrics] = await Promise.all([
      getMarketTrends({ index, timeframe: '1m' }),
      getMarketMetrics(index)
    ]);
    return { trends, metrics };
  } catch (error) {
    console.error("Error fetching market data:", error);
    throw error;
  }
}

// Tracked Companies Functions
export async function getTrackedCompanies(userId: number): Promise<string[]> {
  try {
    const response = await api.get(`/tracked/${userId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching tracked companies:", error);
    throw error;
  }
}

export async function addTrackedCompany(userId: number, symbol: string): Promise<TrackedCompany> {
  try {
    const response = await api.post(`/tracked/${userId}/${symbol}`);
    return response.data;
  } catch (error) {
    console.error("Error adding tracked company:", error);
    throw error;
  }
}

export async function removeTrackedCompany(userId: number, symbol: string): Promise<void> {
  try {
    await api.delete(`/tracked/${userId}/${symbol}`);
  } catch (error) {
    console.error("Error removing tracked company:", error);
    throw error;
  }
}

