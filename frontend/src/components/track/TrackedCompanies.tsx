"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { FaPlus } from "react-icons/fa";
import TrackedCompaniesList from "./TrackedCompaniesList";
import IPOInsights from "./IPOInsights";
import PipelineComparisonChart from "./PipelineComparisonChart";
import CompanyNews from "./CompanyNews";
import CompetitorSearch from "./TrackedCompanySearch";

export default function TrackedCompaniesPage() {
  const [tracked, setTracked] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSearch, setShowSearch] = useState(false);
  const userId = 1; // TODO: Replace with Auth Context

  useEffect(() => {
    fetchTrackedCompanies();
  }, []);

  const fetchTrackedCompanies = async () => {
    try {
      const response = await axios.get(`/api/tracked/${userId}`);
      setTracked(response.data);
      setError(null);
    } catch (err) {
      setError("Error fetching tracked companies");
    } finally {
      setLoading(false);
    }
  };

  const handleCompetitorSelect = async (competitor: any) => {
    try {
      await axios.post(`/api/tracked/${userId}/${competitor.symbol}`);
      setShowSearch(false);
      fetchTrackedCompanies();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || `Error adding ${competitor.symbol}`,
      );
    }
  };

  if (loading)
    return (
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
      <div className="flex justify-between items-center">
        <button
          onClick={() => setShowSearch(!showSearch)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2"
        >
          <FaPlus />
          {showSearch ? "Close Search" : "Add Company"}
        </button>
      </div>

      {/* Company Search Modal */}
      {showSearch && <CompetitorSearch onSelect={handleCompetitorSelect} />}

      {/* Tracked Companies List */}
      <TrackedCompaniesList
        tracked={tracked}
        refreshTracked={fetchTrackedCompanies}
      />

      {/* Market Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <IPOInsights data={tracked} />
        <PipelineComparisonChart symbols={tracked} />
      </div>

      {/* News & Updates */}
      <CompanyNews trackedCompanies={tracked} />
    </div>
  );
}
