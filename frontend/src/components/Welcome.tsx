import React from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from './ui/card';
import { FaSearch, FaBell, FaChartLine } from 'react-icons/fa';

export default function Welcome() {
  const router = useRouter();

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">Welcome to StockSight! 👋</h1>
        <p className="text-gray-600 text-lg">
          Your personal biotech market intelligence platform
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="text-center p-6">
            <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <FaSearch className="text-blue-600 text-xl" />
            </div>
            <h3 className="font-semibold text-lg mb-2">1. Browse Companies</h3>
            <p className="text-gray-600">
              Explore biotech companies by therapeutic area, market cap, and clinical phase
            </p>
            <button
              onClick={() => handleNavigation('/browse')}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Start Browsing
            </button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="text-center p-6">
            <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <FaBell className="text-green-600 text-xl" />
            </div>
            <h3 className="font-semibold text-lg mb-2">2. Track Companies</h3>
            <p className="text-gray-600">
              Add companies to your watchlist to monitor news, updates, and market movements
            </p>
            <button
              onClick={() => handleNavigation('/tracked')}
              className="mt-4 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
            >
              View Tracked
            </button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="text-center p-6">
            <div className="bg-purple-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <FaChartLine className="text-purple-600 text-xl" />
            </div>
            <h3 className="font-semibold text-lg mb-2">3. Analyze Trends</h3>
            <p className="text-gray-600">
              Get insights into market trends, competitor analysis, and industry movements
            </p>
            <button
              onClick={() => handleNavigation('/analytics')}
              className="mt-4 px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
            >
              View Analytics
            </button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Start Guide</h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="bg-blue-100 rounded-full w-8 h-8 flex items-center justify-center mr-4 mt-1">
                <span className="font-semibold text-blue-600">1</span>
              </div>
              <div>
                <h3 className="font-semibold mb-1">Browse Companies</h3>
                <p className="text-gray-600">
                  Start by exploring the biotech companies in our database. Use filters to find companies
                  by therapeutic area, market cap, or clinical trial phase.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="bg-green-100 rounded-full w-8 h-8 flex items-center justify-center mr-4 mt-1">
                <span className="font-semibold text-green-600">2</span>
              </div>
              <div>
                <h3 className="font-semibold mb-1">Track Interesting Companies</h3>
                <p className="text-gray-600">
                  When you find companies you're interested in, click the "Track" button to add them to your
                  watchlist. This will allow you to monitor their news and updates.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="bg-purple-100 rounded-full w-8 h-8 flex items-center justify-center mr-4 mt-1">
                <span className="font-semibold text-purple-600">3</span>
              </div>
              <div>
                <h3 className="font-semibold mb-1">Monitor Your Dashboard</h3>
                <p className="text-gray-600">
                  Your dashboard will automatically update with news, market trends, and insights about your
                  tracked companies. Set up alerts to stay informed about important developments.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 