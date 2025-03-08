"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Dashboard from "../components/dashboard-home/Dashboard";
import AdminPanel from "../components/AdminPanel";

export default function Page() {
  const [featureFlags, setFeatureFlags] = useState({ competitor_score: false });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFeatureFlags = async () => {
      try {
        const response = await api.get("/feature-flags");
        setFeatureFlags(response.data);
        setError(null);
      } catch (err) {
        console.error("Error fetching feature flags:", err);
        setError("Failed to load feature flags");
      }
    };

    fetchFeatureFlags();
  }, []);

  return (
    <main className="p-6">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Dashboard with Tabs */}
      <Dashboard />

      {/* Admin Panel - Only show if competitor scoring is enabled */}
      {featureFlags.competitor_score && (
        <div className="mt-6">
          <AdminPanel />
        </div>
      )}
    </main>
  );
}
