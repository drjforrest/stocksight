'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FaRss, FaTrash, FaNewspaper, FaPlus, FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import CompetitorSearch from './CompetitorSearch';
import { Carousel } from 'react-responsive-carousel';
import "react-responsive-carousel/lib/styles/carousel.min.css";

interface NewsArticle {
  id: number;
  title: string;
  url: string;
  source: string;
  published_at: string;
  sentiment_score: number | null;
}

interface CompanyNews {
  symbol: string;
  articles: NewsArticle[];
}

interface CompanyFigures {
  symbol: string;
  name: string;
  competitor_score: number;
  market_cap?: string;
  price?: number;
  volume?: number;
  therapeutic_area?: string;
}

export default function TrackedCompanies() {
  const [tracked, setTracked] = useState<string[]>([]);
  const [news, setNews] = useState<CompanyNews[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSearch, setShowSearch] = useState(false);
  const [companyFigures, setCompanyFigures] = useState<CompanyFigures[]>([]);
  const userId = 1; // TODO: Get from auth context

  useEffect(() => {
    fetchTrackedCompanies();
  }, []);

  const fetchTrackedCompanies = async () => {
    try {
      const response = await axios.get(`/api/tracked/${userId}`);
      setTracked(response.data);
      fetchNewsForCompanies(response.data);
      fetchCompanyFigures(response.data);
    } catch (err) {
      setError('Error fetching tracked companies');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCompanyFigures = async (companies: string[]) => {
    try {
      const figuresPromises = companies.map(async (symbol) => {
        const response = await axios.get(`/api/companies/${symbol}/figures`);
        return response.data;
      });
      const figures = await Promise.all(figuresPromises);
      // Sort by competitor score
      figures.sort((a, b) => b.competitor_score - a.competitor_score);
      setCompanyFigures(figures);
    } catch (err) {
      setError('Error fetching company figures');
      console.error(err);
    }
  };

  const fetchNewsForCompanies = async (companies: string[]) => {
    try {
      const newsPromises = companies.map(symbol =>
        axios.get(`/api/news/articles/${symbol}`).then(response => ({
          symbol,
          articles: response.data
        }))
      );
      const results = await Promise.all(newsPromises);
      setNews(results);
    } catch (err) {
      setError('Error fetching company news');
      console.error(err);
    }
  };

  const handleCompetitorSelect = async (competitor: any) => {
    try {
      await axios.post(`/api/tracked/${userId}/${competitor.symbol}`);
      setShowSearch(false);
      fetchTrackedCompanies();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Error adding ${competitor.symbol}`);
      console.error(err);
    }
  };

  const removeCompany = async (symbol: string) => {
    try {
      await axios.delete(`/api/tracked/${userId}/${symbol}`);
      setTracked(prev => prev.filter(s => s !== symbol));
      setNews(prev => prev.filter(n => n.symbol !== symbol));
      setCompanyFigures(prev => prev.filter(c => c.symbol !== symbol));
    } catch (err) {
      setError(`Error removing ${symbol}`);
      console.error(err);
    }
  };

  const getSentimentColor = (score: number | null) => {
    if (score === null) return 'text-gray-500';
    if (score > 0.33) return 'text-green-500';
    if (score < -0.33) return 'text-red-500';
    return 'text-yellow-500';
  };

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  );

  return (
    <div className="space-y-8">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          {error}
          <button
            className="absolute top-0 right-0 px-4 py-3"
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}

      {/* Add Company Button */}
      <div className="flex justify-end">
        <button
          onClick={() => setShowSearch(!showSearch)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2"
        >
          <FaPlus />
          {showSearch ? 'Close Search' : 'Add Competitor'}
        </button>
      </div>

      {/* Competitor Search */}
      {showSearch && (
        <CompetitorSearch onSelect={handleCompetitorSelect} />
      )}

      {/* Company Figures Carousel */}
      {companyFigures.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4">Company Overview</h3>
          <Carousel
            showThumbs={false}
            showStatus={false}
            infiniteLoop
            className="company-carousel"
          >
            {companyFigures.map((company) => (
              <div key={company.symbol} className="p-4">
                <h4 className="text-lg font-bold">{company.name} ({company.symbol})</h4>
                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div>
                    <p className="text-sm text-gray-600">Competitor Score</p>
                    <p className="text-lg font-semibold">{(company.competitor_score * 100).toFixed(1)}%</p>
                  </div>
                  {company.market_cap && (
                    <div>
                      <p className="text-sm text-gray-600">Market Cap</p>
                      <p className="text-lg font-semibold">{company.market_cap}</p>
                    </div>
                  )}
                  {company.price && (
                    <div>
                      <p className="text-sm text-gray-600">Price</p>
                      <p className="text-lg font-semibold">${company.price.toFixed(2)}</p>
                    </div>
                  )}
                  {company.therapeutic_area && (
                    <div>
                      <p className="text-sm text-gray-600">Therapeutic Area</p>
                      <p className="text-lg font-semibold">{company.therapeutic_area}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </Carousel>
        </div>
      )}

      {/* News Feed */}
      {tracked.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-md">
          <h3 className="text-2xl font-semibold mb-4">Start Tracking Companies</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Track companies to get real-time updates, news, and market insights. Click the "Add Competitor" button above to get started.
          </p>
          <button
            onClick={() => setShowSearch(true)}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 mx-auto"
          >
            <FaPlus />
            Add Your First Company
          </button>
        </div>
      ) : (
        tracked.map(symbol => (
          <div key={symbol} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">{symbol}</h3>
              <div className="flex space-x-4">
                <a
                  href={`/api/rss/${userId}`}
                  className="text-orange-500 hover:text-orange-600"
                  title="RSS Feed"
                >
                  <FaRss />
                </a>
                <button
                  onClick={() => removeCompany(symbol)}
                  className="text-red-500 hover:text-red-600"
                  title="Remove from tracking"
                >
                  <FaTrash />
                </button>
              </div>
            </div>

            <div className="space-y-4">
              {news
                .find(n => n.symbol === symbol)
                ?.articles.map(article => (
                  <div key={article.id} className="border-b pb-4">
                    <div className="flex items-start justify-between">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 flex-grow"
                      >
                        {article.title}
                      </a>
                      {article.sentiment_score !== null && (
                        <span
                          className={`ml-2 ${getSentimentColor(article.sentiment_score)}`}
                          title={`Sentiment Score: ${article.sentiment_score.toFixed(2)}`}
                        >
                          <FaNewspaper />
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {article.source} • {new Date(article.published_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
} 