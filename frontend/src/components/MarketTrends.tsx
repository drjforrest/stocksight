'use client';

import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
import { Card } from './ui/Card';

interface MarketTrendData {
  date: string;
  index_value: number;
  volume: number;
  change_percent: number;
}

interface IndexMetrics {
  volatility: number;
  moving_average: number;
  trend: 'up' | 'down' | 'neutral';
}

export default function MarketTrends() {
  const [data, setData] = useState<MarketTrendData[]>([]);
  const [metrics, setMetrics] = useState<IndexMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'1d' | '1w' | '1m' | '3m' | '1y'>('1m');
  const [index, setIndex] = useState<string>('BIOTECH');

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        const [trendResponse, metricsResponse] = await Promise.all([
          axios.get('/api/market-trends', {
            params: { timeframe, index }
          }),
          axios.get('/api/market-metrics', {
            params: { index }
          })
        ]);
        
        setData(trendResponse.data);
        setMetrics(metricsResponse.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch market trend data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
  }, [timeframe, index]);

  if (loading) return (
    <Card className="animate-pulse">
      <div className="h-64 bg-gray-200 rounded"></div>
    </Card>
  );
  
  if (error) return (
    <Card className="bg-red-50">
      <div className="text-red-500 p-4">{error}</div>
    </Card>
  );
  
  if (!data.length) return null;

  const chartData = {
    labels: data.map((item) => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Market Index',
        data: data.map((item) => item.index_value),
        borderColor: 'rgb(54, 162, 235)',
        tension: 0.1,
        fill: false,
      },
      {
        label: 'Volume',
        data: data.map((item) => item.volume),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
        yAxisID: 'volume',
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: `${index} Index Performance`,
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
      },
      volume: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-yellow-600';
    }
  };

  return (
    <Card className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">Market Trends</h2>
        <div className="flex gap-4">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as typeof timeframe)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="1d">1 Day</option>
            <option value="1w">1 Week</option>
            <option value="1m">1 Month</option>
            <option value="3m">3 Months</option>
            <option value="1y">1 Year</option>
          </select>
          <select
            value={index}
            onChange={(e) => setIndex(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="BIOTECH">Biotech Index</option>
            <option value="PHARMA">Pharmaceutical Index</option>
            <option value="HEALTHCARE">Healthcare Index</option>
          </select>
        </div>
      </div>

      <div className="mb-6">
        <Line data={chartData} options={chartOptions} />
      </div>

      {metrics && (
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Volatility</h3>
            <p>{metrics.volatility.toFixed(2)}%</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Moving Average</h3>
            <p>{metrics.moving_average.toFixed(2)}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Trend</h3>
            <p className={getTrendColor(metrics.trend)}>
              {metrics.trend.toUpperCase()}
            </p>
          </div>
        </div>
      )}
    </Card>
  );
}