'use client';

import React, { useState, useEffect } from "react";
import axios from "axios";

export default function AdminPanel() {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    async function fetchFeatureStatus() {
      try {
        const response = await axios.get("/api/feature-flags");
        setEnabled(response.data.competitorScoring);
      } catch (error) {
        console.error("Failed to fetch feature flag status", error);
      }
    }

    fetchFeatureStatus();
  }, []);

  const toggleFeature = async () => {
    try {
      await axios.post("/api/feature-flags", { competitorScoring: !enabled });
      setEnabled(!enabled);
    } catch (error) {
      console.error("Failed to toggle feature", error);
    }
  };

  return (
    <div className="bg-gray-100 p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">Admin Controls</h2>
      <button
        onClick={toggleFeature}
        className={`px-4 py-2 rounded text-white ${enabled ? "bg-green-600" : "bg-red-600"}`}
      >
        {enabled ? "Disable Competitor Scoring" : "Enable Competitor Scoring"}
      </button>
    </div>
  );
}