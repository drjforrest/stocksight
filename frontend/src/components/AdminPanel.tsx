'use client';

import React, { useState, useEffect } from "react";
import { api } from '@/lib/api';
import { AxiosError } from "axios";
import { FeatureFlags } from "../types/competitor";

export default function AdminPanel() {
  const [enabled, setEnabled] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchFeatureStatus() {
      try {
        const response = await api.get<FeatureFlags>('/feature-flags');
        setEnabled(response.data.competitorScoring);
        setError(null);
      } catch (error) {
        const errorMessage = error instanceof AxiosError 
          ? error.response?.data?.message || "Failed to fetch feature flag status"
          : "An unexpected error occurred";
        setError(errorMessage);
        console.error("Failed to fetch feature flag status", error);
      }
    }

    fetchFeatureStatus();
  }, []);

  const toggleFeature = async () => {
    try {
      await api.post<FeatureFlags>('/feature-flags', { competitorScoring: !enabled });
      setEnabled(!enabled);
      setError(null);
    } catch (error) {
      const errorMessage = error instanceof AxiosError 
        ? error.response?.data?.message || "Failed to toggle feature"
        : "An unexpected error occurred";
      setError(errorMessage);
      console.error("Failed to toggle feature", error);
    }
  };

  return (
    <div className="bg-gray-100 p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">Admin Controls</h2>
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      <button
        onClick={toggleFeature}
        className={`px-4 py-2 rounded text-white ${enabled ? "bg-green-600" : "bg-red-600"}`}
      >
        {enabled ? "Disable Competitor Scoring" : "Enable Competitor Scoring"}
      </button>
    </div>
  );
}