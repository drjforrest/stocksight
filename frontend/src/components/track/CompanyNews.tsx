"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { FaRss, FaNewspaper } from "react-icons/fa";
import { Card } from "../ui/card";

interface NewsArticle {
  title: string;
  url: string;
  source: string;
  published_at: string;
  sentiment_score?: number;
}

interface CompanyNewsProps {
  trackedCompanies: string[];
}

export default function CompanyNews({ trackedCompanies }: CompanyNewsProps) {
  const [news, setNews] = useState<{ [symbol: string]: NewsArticle[] }>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (trackedCompanies.length === 0) return;
    fetchNews();
  }, [trackedCompanies]);

  const fetchNews = async () => {
    try {
      const newsPromises = trackedCompanies.map(async (symbol) => {
        const response = await axios.get(`/api/news/articles/${symbol}`);
        return { symbol, articles: response.data };
      });

      const results = await Promise.all(newsPromises);
      const newsData = Object.fromEntries(
        results.map(({ symbol, articles }) => [symbol, articles]),
      );
      setNews(newsData);
    } catch (err) {
      console.error("Error fetching news:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p className="text-center">Loading news...</p>;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Latest Company News</h2>

      {trackedCompanies.length === 0 ? (
        <p className="text-gray-600">
          Track companies to get real-time news updates.
        </p>
      ) : (
        trackedCompanies.map((symbol) => (
          <Card key={symbol} className="p-6">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <FaNewspaper />
              {symbol} News
            </h3>

            <ul className="mt-3 space-y-2">
              {news[symbol]?.slice(0, 3).map((article, index) => (
                <li key={index} className="text-blue-600 hover:underline">
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {article.title} ({article.source})
                  </a>
                </li>
              )) || <p>No recent news available.</p>}
            </ul>

            <a
              href={`/api/rss/${symbol}`}
              className="text-orange-500 mt-3 inline-flex items-center gap-2"
            >
              <FaRss />
              Subscribe to RSS Feed
            </a>
          </Card>
        ))
      )}
    </div>
  );
}
