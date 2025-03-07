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

export async function getMarketTrends(params?: {
  timeframe?: '1d' | '1w' | '1m' | '3m' | '1y';
  index?: string;
}): Promise<MarketTrendData[]> {
  try {
    const response = await api.get('/market-trends', { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching market trends:", error);
    throw error;
  }
}

export async function getMarketMetrics(index: string): Promise<MarketMetrics> {
  try {
    const response = await api.get('/market-metrics', {
      params: { index }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching market metrics:", error);
    throw error;
  }
}

// Batch data fetching
export async function getMarketData(index: string) {
  try {
    const [trends, metrics] = await Promise.all([
      getMarketTrends({ index }),
      getMarketMetrics(index)
    ]);
    return { trends, metrics };
  } catch (error) {
    console.error("Error fetching market data:", error);
    throw error;
  }
} 