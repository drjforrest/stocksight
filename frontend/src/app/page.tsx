'use client';

import React from 'react';
import StockPrice from '@/components/StockPrice';
import StockChart from '@/components/StockChart';

export default function Home() {
  const [watchlist] = React.useState(['AAPL', 'GOOGL', 'MSFT', 'AMZN']);

  return (
    <main className="min-h-screen p-8 bg-gray-100">
      <h1 className="text-4xl font-bold mb-8">StockSight Dashboard</h1>
      
      {/* Stock Price Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {watchlist.map(symbol => (
          <StockPrice key={symbol} symbol={symbol} />
        ))}
      </div>

      {/* Stock Charts */}
      <div className="space-y-8">
        {watchlist.map(symbol => (
          <div key={symbol} className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">{symbol} Price History</h2>
            <StockChart
              symbol={symbol}
              data={[]} // This will be populated with real data
            />
          </div>
        ))}
      </div>
    </main>
  );
}
