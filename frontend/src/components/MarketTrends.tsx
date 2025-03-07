'use client';

import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Card } from './ui/card';
import { getMarketData } from '@/lib/api-functions';
import type { MarketTrendData, MarketMetrics } from '@/lib/api-functions';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

type ChartType = 'line' | 'area' | 'candlestick';

export default function MarketTrends() {
  const [data, setData] = useState<MarketTrendData[]>([]);
  const [metrics, setMetrics] = useState<MarketMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'1d' | '1w' | '1m' | '3m' | '1y'>('1m');
  const [index, setIndex] = useState<string>('BIOTECH');
  const [chartType, setChartType] = useState<ChartType>('line');

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const { trends, metrics } = await getMarketData(index);
        setData(trends);
        setMetrics(metrics);
        setError(null);
      } catch (err) {
        setError('Failed to fetch market trend data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
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

  const getChartData = () => {
    const baseDataset = {
      labels: data.map((item) => new Date(item.date).toLocaleDateString()),
      datasets: [
        {
          label: 'Market Index',
          data: data.map((item) => item.index_value),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.4,
          fill: chartType === 'area',
          pointRadius: chartType === 'line' ? 4 : 0,
          pointHoverRadius: chartType === 'line' ? 8 : 0,
          pointBackgroundColor: 'rgb(54, 162, 235)',
          pointHoverBackgroundColor: 'white',
          pointBorderColor: 'white',
          pointHoverBorderColor: 'rgb(54, 162, 235)',
          pointBorderWidth: 2,
          pointHoverBorderWidth: 2,
        },
        {
          label: 'Volume',
          data: data.map((item) => item.volume),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.4,
          yAxisID: 'volume',
          fill: true,
          pointRadius: 0,
        },
      ],
    };

    if (chartType === 'candlestick') {
      // Modify dataset for candlestick visualization
      baseDataset.datasets[0] = {
        label: 'Market Index',
        data: data.map((item) => item.index_value),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0,
        fill: false,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: 'rgb(75, 192, 192)',
        pointHoverBackgroundColor: 'white',
        pointBorderColor: 'white',
        pointHoverBorderColor: 'rgb(75, 192, 192)',
        pointBorderWidth: 2,
        pointHoverBorderWidth: 2
      };
    }

    return baseDataset;
  };

  const chartOptions = {
    responsive: true,
    animation: {
      duration: 2000,
      easing: 'easeOutQuart' as const,
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
      axis: 'x' as const,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          pointStyle: 'circle',
          padding: 20,
        },
      },
      title: {
        display: true,
        text: `${index} Index Performance`,
        font: {
          size: 16,
          weight: 'bold' as const,
        },
        padding: 20,
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        titleColor: '#000',
        bodyColor: '#666',
        bodySpacing: 4,
        padding: 12,
        borderColor: '#ddd',
        borderWidth: 1,
        usePointStyle: true,
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            if (context.datasetIndex === 0) {
              return `${label}: ${value.toFixed(2)}`;
            } else {
              return `${label}: ${value.toLocaleString()}`;
            }
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          callback: function(value: any) {
            return value.toFixed(2);
          },
        },
      },
      volume: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          callback: function(value: any) {
            return value.toLocaleString();
          },
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
            value={chartType}
            onChange={(e) => setChartType(e.target.value as ChartType)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="line">Line Chart</option>
            <option value="area">Area Chart</option>
            <option value="candlestick">Candlestick</option>
          </select>
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
        <Line data={getChartData()} options={chartOptions} />
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