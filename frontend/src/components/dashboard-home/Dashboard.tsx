"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import MarketOverview from "./MarketOverview";
import TrackedCompaniesList from "./TrackedCompaniesList";
import { Card } from "../ui/card";

export default function Dashboard() {
  const [trackedCompanies, setTrackedCompanies] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrackedCompanies();
  }, []);

  const fetchTrackedCompanies = async () => {
    try {
      const response = await axios.get(`/api/tracked`);
      setTrackedCompanies(response.data);
    } catch (err) {
      setError("Error fetching tracked companies");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const removeCompany = async (symbol: string) => {
    try {
      await axios.delete(`/api/tracked/${symbol}`);
      setTrackedCompanies((prev) =>
        prev.filter((company) => company !== symbol),
      );
    } catch (err) {
      setError(`Error removing ${symbol}`);
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">
      {error && (
        <Card className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
          <button
            className="absolute top-0 right-0 px-4 py-3"
            onClick={() => setError(null)}
          >
            ×
          </button>
        </Card>
      )}

      {/* 🔹 Market Overview Cards */}
      <MarketOverview />

      {/* 🔹 List of Tracked Companies */}
      <TrackedCompaniesList
        trackedCompanies={trackedCompanies}
        onRemoveCompany={removeCompany}
      />
    </div>
  );
}
