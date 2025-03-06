'use client';

import React from 'react';
import axios from 'axios';

interface StockPriceProps {
  symbol: string;
}

interface PriceData {
  symbol: string;
  price: number;
  timestamp: string;
}

export default function StockPrice({ symbol }: StockPriceProps) {
  const [priceData, setPriceData] = React.useState<PriceData | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchPrice = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/stocks/${symbol}/price`);
        setPriceData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch price data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPrice();
    const interval = setInterval(fetchPrice, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [symbol]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!priceData) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">{symbol}</h2>
      <div className="text-4xl font-bold text-green-600">
        ${priceData.price.toFixed(2)}
      </div>
      <div className="text-sm text-gray-500 mt-2">
        Last updated: {new Date(priceData.timestamp).toLocaleString()}
      </div>
    </div>
  );
} 