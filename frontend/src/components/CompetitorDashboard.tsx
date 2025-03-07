'use client';

import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  ScaleOptionsByType,
  TooltipItem,
  Scale,
  CoreScaleOptions,
  ChartOptions,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import axios from 'axios';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface CompetitorData {
  symbol: string;
  name: string;
  market_cap: number;
  r_and_d_expense: number;
  competitiveness_score: number;
  pipeline_stage: string;
  therapeutic_area?: string;
}

// Format large numbers to readable format
const formatCurrency = (value: number, decimals = 1): string => {
  if (value >= 1e9) {
    return `$${(value / 1e9).toFixed(decimals)}B`;
  }
  if (value >= 1e6) {
    return `$${(value / 1e6).toFixed(decimals)}M`;
  }
  return `$${value.toFixed(decimals)}`;
};

export default function CompetitorDashboard() {
  const [competitors, setCompetitors] = useState<CompetitorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompetitor, setSelectedCompetitor] = useState<CompetitorData | null>(null);
  const [chartType, setChartType] = useState<'market' | 'score'>('market');
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/competitors');
        setCompetitors(response.data);
      } catch (err) {
        setError('Failed to fetch competitor data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Update chart colors based on theme
  const getChartColors = (opacity: number = 0.5) => {
    return {
      blue: {
        bg: isDarkMode ? `rgba(96, 165, 250, ${opacity})` : `rgba(53, 162, 235, ${opacity})`,
        border: isDarkMode ? 'rgba(96, 165, 250, 1)' : 'rgba(53, 162, 235, 1)',
      },
      green: {
        bg: isDarkMode ? `rgba(52, 211, 153, ${opacity})` : `rgba(75, 192, 192, ${opacity})`,
        border: isDarkMode ? 'rgba(52, 211, 153, 1)' : 'rgba(75, 192, 192, 1)',
      },
      red: {
        bg: isDarkMode ? `rgba(248, 113, 113, ${opacity})` : `rgba(255, 99, 132, ${opacity})`,
        border: isDarkMode ? 'rgba(248, 113, 113, 1)' : 'rgba(255, 99, 132, 1)',
      },
      yellow: {
        bg: isDarkMode ? `rgba(251, 191, 36, ${opacity})` : `rgba(255, 206, 86, ${opacity})`,
        border: isDarkMode ? 'rgba(251, 191, 36, 1)' : 'rgba(255, 206, 86, 1)',
      },
    };
  };

  const colors = getChartColors();

  const marketShareData = {
    labels: competitors.map(c => c.symbol),
    datasets: [{
      label: 'Market Share',
      data: competitors.map(c => c.market_cap),
      backgroundColor: colors.blue.bg,
      borderColor: colors.blue.border,
      borderWidth: 1,
    }]
  };

  const scoreData = {
    labels: competitors.map(c => c.symbol),
    datasets: [{
      label: 'Competitor Score',
      data: competitors.map(c => c.competitiveness_score),
      backgroundColor: colors.green.bg,
      borderColor: colors.green.border,
      borderWidth: 1,
    }]
  };

  const pipelineData = {
    labels: ['Phase 1', 'Phase 2', 'Phase 3', 'FDA Approved'],
    datasets: [{
      data: ['Phase 1', 'Phase 2', 'Phase 3', 'FDA Approved'].map(stage =>
        competitors.filter(c => c.pipeline_stage === stage).length
      ),
      backgroundColor: [
        colors.red.bg,
        colors.blue.bg,
        colors.yellow.bg,
        colors.green.bg,
      ],
      borderColor: [
        colors.red.border,
        colors.blue.border,
        colors.yellow.border,
        colors.green.border,
      ],
      borderWidth: 1,
    }]
  };

  const chartOptions: ChartOptions<'bar'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: isDarkMode ? '#e5e7eb' : '#374151',
        },
      },
      tooltip: {
        callbacks: {
          label: (context: TooltipItem<'bar'>) => {
            const value = context.raw as number;
            if (context.dataset.label === 'Market Share') {
              return `Market Cap: ${formatCurrency(value)}`;
            }
            if (context.dataset.label === 'Competitor Score') {
              return `Score: ${value.toFixed(1)}`;
            }
            return `Count: ${value}`;
          }
        }
      }
    },
    scales: {
      y: {
        type: 'linear' as const,
        beginAtZero: true,
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          color: isDarkMode ? '#e5e7eb' : '#374151',
          callback: function(tickValue: number | string) {
            const value = Number(tickValue);
            return chartType === 'market' ? formatCurrency(value) : value;
          }
        }
      },
      x: {
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        },
        ticks: {
          color: isDarkMode ? '#e5e7eb' : '#374151',
        }
      }
    },
    onClick: (event: any, elements: any) => {
      if (elements.length > 0) {
        const index = elements[0].index;
        setSelectedCompetitor(competitors[index]);
      }
    },
  };

  const pieOptions: ChartOptions<'pie'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: isDarkMode ? '#e5e7eb' : '#374151',
        },
      },
      tooltip: {
        callbacks: {
          label: (context: TooltipItem<'pie'>) => {
            const value = context.raw as number;
            return `Count: ${value}`;
          }
        }
      }
    }
  };

  if (loading) return <div className="p-4 dark:text-gray-200">Loading dashboard...</div>;
  if (error) return <div className="p-4 text-red-500 dark:text-red-400">{error}</div>;

  return (
    <div className={`p-6 rounded-lg shadow-lg transition-colors duration-200 ${isDarkMode ? 'bg-gray-800 text-gray-200' : 'bg-white text-gray-900'}`}>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Competitor Analysis Dashboard</h2>
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
            isDarkMode 
              ? 'bg-gray-700 hover:bg-gray-600 text-gray-200' 
              : 'bg-gray-200 hover:bg-gray-300 text-gray-900'
          }`}
        >
          {isDarkMode ? '🌞 Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className={`p-4 border rounded-lg hover:shadow-lg transition-all ${
          isDarkMode ? 'border-gray-700 hover:border-gray-600' : 'border-gray-200 hover:border-gray-300'
        }`}>
          <h3 className="text-lg font-semibold mb-4">Market Share Distribution</h3>
          <Bar 
            data={marketShareData} 
            options={chartOptions} 
            onMouseEnter={() => setChartType('market')}
          />
        </div>

        <div className={`p-4 border rounded-lg hover:shadow-lg transition-all ${
          isDarkMode ? 'border-gray-700 hover:border-gray-600' : 'border-gray-200 hover:border-gray-300'
        }`}>
          <h3 className="text-lg font-semibold mb-4">Competitor Scores</h3>
          <Bar 
            data={scoreData} 
            options={chartOptions}
            onMouseEnter={() => setChartType('score')}
          />
        </div>

        <div className={`p-4 border rounded-lg hover:shadow-lg transition-all ${
          isDarkMode ? 'border-gray-700 hover:border-gray-600' : 'border-gray-200 hover:border-gray-300'
        }`}>
          <h3 className="text-lg font-semibold mb-4">Pipeline Stage Distribution</h3>
          <Pie data={pipelineData} options={pieOptions} />
        </div>

        <div className={`p-4 border rounded-lg hover:shadow-lg transition-all ${
          isDarkMode ? 'border-gray-700 hover:border-gray-600' : 'border-gray-200 hover:border-gray-300'
        }`}>
          <h3 className="text-lg font-semibold mb-4">Key Metrics Summary</h3>
          <div className="space-y-4">
            <div>
              <p className="font-semibold">Total Competitors: {competitors.length}</p>
              <p className="font-semibold">Average Market Cap: {formatCurrency(competitors.reduce((acc, curr) => acc + curr.market_cap, 0) / competitors.length)}</p>
              <p className="font-semibold">Average R&D Spend: {formatCurrency(competitors.reduce((acc, curr) => acc + curr.r_and_d_expense, 0) / competitors.length)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Competitor Details */}
      {selectedCompetitor && (
        <div className={`mt-6 p-4 border rounded-lg transition-colors duration-200 ${
          isDarkMode 
            ? 'bg-gray-700 border-gray-600' 
            : 'bg-blue-50 border-blue-100'
        }`}>
          <h3 className="text-lg font-semibold mb-2">
            {selectedCompetitor.name} ({selectedCompetitor.symbol})
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p><span className="font-medium">Market Cap:</span> {formatCurrency(selectedCompetitor.market_cap)}</p>
              <p><span className="font-medium">R&D Expense:</span> {formatCurrency(selectedCompetitor.r_and_d_expense)}</p>
            </div>
            <div>
              <p><span className="font-medium">Pipeline Stage:</span> {selectedCompetitor.pipeline_stage}</p>
              <p><span className="font-medium">Score:</span> {selectedCompetitor.competitiveness_score.toFixed(1)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 