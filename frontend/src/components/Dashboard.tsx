'use client';

import React, { useState, useEffect } from "react";
import StockChart from "./StockChart";
import MarketTrends from "./MarketTrends";
import IPOInsights from "./IPOInsights";
import { Card, CardContent } from "./ui/card";
import { getMarketTrends, getStockPrices, getIPOListings, getFeatureFlags } from "@/lib/api-functions";
import { mockLogin } from "@/lib/auth";

type TabType = 'overview' | 'market' | 'ipo';

interface MarketData {
  trends: any[];
  loading: boolean;
  error: string | null;
}

interface StockData {
  prices: any[];
  loading: boolean;
  error: string | null;
}

interface IPOData {
  listings: any[];
  loading: boolean;
  error: string | null;
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [marketData, setMarketData] = useState<MarketData>({
    trends: [],
    loading: true,
    error: null
  });
  const [stockData, setStockData] = useState<StockData>({
    prices: [],
    loading: true,
    error: null
  });
  const [ipoData, setIPOData] = useState<IPOData>({
    listings: [],
    loading: true,
    error: null
  });

  // Handle authentication on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        await mockLogin(); // This will set up our dev token
      } catch (err) {
        console.error("Failed to initialize auth:", err);
      }
    };

    initAuth();
  }, []);

  // Fetch market data
  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const trends = await getMarketTrends('BIOTECH', '1m');
        setMarketData({
          trends,
          loading: false,
          error: null
        });
      } catch (err) {
        setMarketData(prev => ({
          ...prev,
          loading: false,
          error: 'Failed to fetch market data'
        }));
      }
    };

    fetchMarketData();
  }, []);

  // Fetch stock data - only if we have a selected company, otherwise show placeholder
  useEffect(() => {
    const fetchStockData = async () => {
      try {
        // For now, using AAPL as example. You should replace this with selected company
        const prices = await getStockPrices('AAPL');
        setStockData({
          prices,
          loading: false,
          error: null
        });
      } catch (err) {
        setStockData(prev => ({
          ...prev,
          loading: false,
          error: 'Select a company to view stock data'
        }));
      }
    };

    fetchStockData();
  }, []);

  // Fetch IPO data
  useEffect(() => {
    const fetchIPOData = async () => {
      try {
        const listings = await getIPOListings();
        setIPOData({
          listings,
          loading: false,
          error: null
        });
      } catch (err) {
        setIPOData(prev => ({
          ...prev,
          loading: false,
          error: 'Failed to fetch IPO data'
        }));
      }
    };

    fetchIPOData();
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'market', label: 'Market Trends' },
    { id: 'ipo', label: 'IPO Insights' }
  ];

  const renderLoadingState = () => (
    <div className="animate-pulse flex space-x-4">
      <div className="flex-1 space-y-4 py-1">
        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    </div>
  );

  const renderErrorState = (message: string) => (
    <div className="bg-red-50 p-4 rounded-md">
      <p className="text-red-600">{message}</p>
    </div>
  );

  const renderNoDataState = (message: string) => (
    <div className="bg-gray-50 p-4 rounded-md">
      <p className="text-gray-600">{message}</p>
    </div>
  );

  return (
    <div className="p-6">
      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardContent>
              <h2 className="text-xl font-bold mb-4">Stock Performance</h2>
              {stockData.loading ? renderLoadingState() :
               stockData.error ? renderErrorState(stockData.error) :
               stockData.prices.length === 0 ? renderNoDataState('Select a company to view stock data') :
               <StockChart symbol="AAPL" data={stockData.prices} />}
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <h2 className="text-xl font-bold mb-4">Market Summary</h2>
              {marketData.loading ? renderLoadingState() :
               marketData.error ? renderErrorState(marketData.error) :
               marketData.trends.length === 0 ? renderNoDataState('No market data available') :
               <MarketTrends data={marketData.trends} />}
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <h2 className="text-xl font-bold mb-4">Recent IPOs</h2>
              {ipoData.loading ? renderLoadingState() :
               ipoData.error ? renderErrorState(ipoData.error) :
               ipoData.listings.length === 0 ? renderNoDataState('No IPO data available') :
               <IPOInsights data={ipoData.listings} />}
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'market' && (
        <div className="w-full">
          <Card>
            <CardContent>
              {marketData.loading ? renderLoadingState() :
               marketData.error ? renderErrorState(marketData.error) :
               marketData.trends.length === 0 ? renderNoDataState('No market data available') :
               <MarketTrends data={marketData.trends} fullView />}
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'ipo' && (
        <div className="w-full">
          <Card>
            <CardContent>
              {ipoData.loading ? renderLoadingState() :
               ipoData.error ? renderErrorState(ipoData.error) :
               ipoData.listings.length === 0 ? renderNoDataState('No IPO data available') :
               <IPOInsights data={ipoData.listings} fullView />}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
