import React, { useState } from "react";
import StockChart from "./StockChart";
import MarketTrends from "./MarketTrends";
import IPOInsights from "./IPOInsights";
import { Card, CardContent } from "./ui/card";

type TabType = 'overview' | 'market' | 'ipo';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'market', label: 'Market Trends' },
    { id: 'ipo', label: 'IPO Insights' }
  ];

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
              <StockChart symbol="AAPL" data={[]} />
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <h2 className="text-xl font-bold mb-4">Market Summary</h2>
              <MarketTrends />
            </CardContent>
          </Card>
          
          <Card>
            <CardContent>
              <h2 className="text-xl font-bold mb-4">Recent IPOs</h2>
              <IPOInsights />
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'market' && (
        <div className="w-full">
          <Card>
            <CardContent>
              <MarketTrends />
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'ipo' && (
        <div className="w-full">
          <Card>
            <CardContent>
              <IPOInsights />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
