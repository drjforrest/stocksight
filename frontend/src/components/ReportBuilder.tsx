'use client';

import React, { useState } from "react";
import axios from "axios";

export default function ReportBuilder({ availableCharts }: { availableCharts: any[] }) {
  const [selectedCharts, setSelectedCharts] = useState<string[]>([]);
  const [email, setEmail] = useState("");

  const toggleChartSelection = (chartId: string) => {
    setSelectedCharts((prev) =>
      prev.includes(chartId) ? prev.filter(id => id !== chartId) : [...prev, chartId]
    );
  };

  const handleGenerateReport = async () => {
    try {
      const response = await axios.post("/api/generate-report", {
        selected_charts: selectedCharts,
        email: email || null,
      });

      alert(response.data.message);
    } catch (error) {
      console.error("Failed to generate report", error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">Create a Report</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium">Send Report to Email (Optional)</label>
        <input
          type="email"
          placeholder="Enter recipient email..."
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded mt-1"
        />
      </div>

      <h3 className="text-lg font-semibold mb-2">Select Charts to Include:</h3>
      <ul className="mb-4">
        {availableCharts.map((chart) => (
          <li key={chart.id} className="flex items-center">
            <input
              type="checkbox"
              checked={selectedCharts.includes(chart.id)}
              onChange={() => toggleChartSelection(chart.id)}
              className="mr-2"
            />
            <span>{chart.title}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={handleGenerateReport}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Generate Report
      </button>
    </div>
  );
}