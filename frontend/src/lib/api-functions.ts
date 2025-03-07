import axios from 'axios';
import { api } from "./api";

// Base API URL
const API_BASE = '/api';

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
export const getStockPrices = async (symbol: string) => {
  const response = await axios.get(`${API_BASE}/stocks/${symbol}/prices`);
  return response.data;
};

export const getIPOListings = async () => {
  const response = await axios.get(`${API_BASE}/ipos`);
  return response.data;
};

export const getIPOInsights = async (timeframe: string, therapeuticArea?: string) => {
  const response = await axios.get(`${API_BASE}/ipos/insights`, {
    params: {
      timeframe,
      therapeutic_area: therapeuticArea
    }
  });
  return response.data;
};

export const getFeatureFlags = async () => {
  const response = await axios.get(`${API_BASE}/feature-flags`);
  return response.data;
};

export const getMarketTrends = async (index: string, timeframe: string) => {
  const response = await axios.get(`${API_BASE}/market/trends/${index}`, {
    params: { timeframe }
  });
  return response.data;
};

export const getMarketMetrics = async (index: string) => {
  const response = await axios.get(`${API_BASE}/market/metrics/${index}`);
  return response.data;
};

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
      getMarketTrends(index, '1m'),
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

