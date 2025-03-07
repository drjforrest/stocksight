'use client';

import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Radar } from 'react-chartjs-2';
import axios from 'axios';
import { Card } from './ui/card';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface IPOData {
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

type ChartType = 'bar' | 'horizontal-bar' | 'radar';

interface IPOInsightsProps {
  data: any[];
  fullView?: boolean;
}

export default function IPOInsights({ data, fullView = false }: IPOInsightsProps) {
  const [ipoData, setIPOData] = useState<IPOData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'30d' | '90d' | '180d' | '365d'>('90d');
  const [therapeuticArea, setTherapeuticArea] = useState<string>('all');
  const [chartType, setChartType] = useState<ChartType>('bar');

  useEffect(() => {
    const fetchIPOData = async () => {
      try {
        const response = await axios.get('/api/ipo-insights', {
          params: {
            timeframe,
            therapeutic_area: therapeuticArea !== 'all' ? therapeuticArea : undefined
          }
        });
        setIPOData(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch IPO data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchIPOData();
  }, [timeframe, therapeuticArea]);

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
  
  if (!ipoData) return null;

  const getChartData = () => {
    const baseData = {
      labels: ['Completion Rate', 'Withdrawal Rate', 'Avg Price Performance'],
      datasets: [
        {
          label: 'IPO Insights',
          data: [ipoData.completion_rate, ipoData.withdrawal_rate, ipoData.avg_price_performance],
          backgroundColor: [
            'rgba(76, 175, 80, 0.8)',
            'rgba(244, 67, 54, 0.8)',
            'rgba(255, 193, 7, 0.8)',
          ],
          borderColor: [
            'rgb(76, 175, 80)',
            'rgb(244, 67, 54)',
            'rgb(255, 193, 7)',
          ],
          borderWidth: 2,
          borderRadius: chartType === 'radar' ? 0 : 8,
        },
      ],
    };

    if (chartType === 'horizontal-bar') {
      return {
        ...baseData,
        indexAxis: 'y' as const,
      };
    }

    return baseData;
  };

  const getChartOptions = () => {
    const baseOptions = {
      responsive: true,
      animation: {
        duration: 2000,
        easing: 'easeOutQuart' as const,
      },
      plugins: {
        legend: {
          position: 'top' as const,
          labels: {
            padding: 20,
            font: {
              size: 12,
            },
          },
        },
        title: {
          display: true,
          text: `IPO Performance Metrics (${timeframe})`,
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
          callbacks: {
            label: function(context: any) {
              const value = context.parsed.y || context.parsed.r;
              return `${context.label}: ${(value * 100).toFixed(1)}%`;
            },
          },
        },
      },
      scales: chartType !== 'radar' ? {
        y: {
          beginAtZero: true,
          max: 1,
          ticks: {
            callback: function(value: any) {
              return (value * 100) + '%';
            },
            font: {
              size: 12,
            },
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)',
          },
        },
        x: {
          grid: {
            display: false,
          },
          ticks: {
            font: {
              size: 12,
            },
          },
        },
      } : undefined,
    };

    return baseOptions;
  };

  return (
    <Card className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">IPO Insights</h2>
        <div className="flex gap-4">
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value as ChartType)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="bar">Bar Chart</option>
            <option value="horizontal-bar">Horizontal Bar</option>
            <option value="radar">Radar Chart</option>
          </select>
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as typeof timeframe)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="180d">Last 180 Days</option>
            <option value="365d">Last Year</option>
          </select>
          <select
            value={therapeuticArea}
            onChange={(e) => setTherapeuticArea(e.target.value)}
            className="px-3 py-2 border rounded-md"
          >
            <option value="all">All Areas</option>
            <option value="oncology">Oncology</option>
            <option value="immunology">Immunology</option>
            <option value="neurology">Neurology</option>
            <option value="rare-diseases">Rare Diseases</option>
          </select>
        </div>
      </div>

      <div className="mb-6">
        {chartType === 'radar' ? (
          <Radar data={getChartData()} options={getChartOptions()} />
        ) : (
          <Bar data={getChartData()} options={getChartOptions()} />
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Summary Statistics</h3>
          <p>Total IPOs: {ipoData.total_ipos}</p>
          <p>Success Rate: {(ipoData.completion_rate * 100).toFixed(1)}%</p>
          <p>Average Performance: {(ipoData.avg_price_performance * 100).toFixed(1)}%</p>
        </div>
        {ipoData.statistical_analysis && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Statistical Analysis</h3>
            <p>T-Statistic: {ipoData.statistical_analysis.t_statistic.toFixed(2)}</p>
            <p>P-Value: {ipoData.statistical_analysis.p_value.toFixed(4)}</p>
            <p className={ipoData.statistical_analysis.significant ? 'text-green-600' : 'text-yellow-600'}>
              {ipoData.statistical_analysis.significant ? 'Statistically Significant' : 'Not Statistically Significant'}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}