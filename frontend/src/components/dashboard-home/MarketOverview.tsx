"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card } from "../ui/card";

interface MarketOverviewData {
  total_market_cap: number;
  avg_ipo_performance: number;
  clinical_trials_active: number;
  mergers_acquisitions: number;
}

export default function MarketOverview() {
  const [marketData, setMarketData] = useState<MarketOverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMarketOverview();
  }, []);

  const fetchMarketOverview = async () => {
    try {
      const response = await axios.get("/api/market-overview");
      setMarketData(response.data);
      setError(null);
    } catch (err) {
      setError("Error fetching market overview data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return <Card className="bg-red-50 text-red-700 p-4 rounded">{error}</Card>;
  }

  if (!marketData) return null;

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value}`;
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Market Cap */}
      <Card className="p-6 bg-blue-50 border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-700">
          Total Market Cap
        </h3>
        <p className="text-2xl font-bold">
          {formatCurrency(marketData.total_market_cap)}
        </p>
      </Card>

      {/* IPO Performance */}
      <Card className="p-6 bg-green-50 border border-green-200">
        <h3 className="text-lg font-semibold text-green-700">
          Avg IPO Performance
        </h3>
        <p className="text-2xl font-bold">
          {(marketData.avg_ipo_performance * 100).toFixed(1)}%
        </p>
      </Card>

      {/* Active Clinical Trials */}
      <Card className="p-6 bg-yellow-50 border border-yellow-200">
        <h3 className="text-lg font-semibold text-yellow-700">
          Active Clinical Trials
        </h3>
        <p className="text-2xl font-bold">
          {marketData.clinical_trials_active.toLocaleString()}
        </p>
      </Card>

      {/* M&A Activity */}
      <Card className="p-6 bg-purple-50 border border-purple-200">
        <h3 className="text-lg font-semibold text-purple-700">
          Mergers & Acquisitions
        </h3>
        <p className="text-2xl font-bold">{marketData.mergers_acquisitions}</p>
      </Card>
    </div>
  );
}
