"use client";

import React, { useState } from "react";
import axios from "axios";
import { CircularProgress } from "@mui/material";

export function ReportBuilder({ availableCharts }: { availableCharts: any[] }) {
  const [selectedCharts, setSelectedCharts] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [reportFormat, setReportFormat] = useState<"pdf" | "csv">("pdf");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleChartSelection = (chartId: string) => {
    setSelectedCharts((prev) =>
      prev.includes(chartId)
        ? prev.filter((id) => id !== chartId)
        : [...prev, chartId],
    );
  };

  const handleGenerateReport = async () => {
    if (selectedCharts.length === 0) {
      setError("Please select at least one chart.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post("/api/generate-report", {
        selected_charts: selectedCharts,
        email: email || null,
        format: reportFormat,
      });

      alert(response.data.message);
    } catch (error) {
      console.error("Failed to generate report", error);
      setError("Failed to generate report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg space-y-4">
      <h2 className="text-xl font-bold">Create a Report</h2>

      {/* Email Input */}
      <div>
        <label className="block text-sm font-medium">
          Send Report to Email (Optional)
        </label>
        <input
          type="email"
          placeholder="Enter recipient email..."
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded mt-1"
        />
      </div>

      {/* Format Selection */}
      <div>
        <label className="block text-sm font-medium">Report Format</label>
        <select
          value={reportFormat}
          onChange={(e) => setReportFormat(e.target.value as "pdf" | "csv")}
          className="w-full p-2 border rounded mt-1"
        >
          <option value="pdf">PDF</option>
          <option value="csv">CSV</option>
        </select>
      </div>

      {/* Chart Selection */}
      <h3 className="text-lg font-semibold">Select Charts to Include:</h3>
      <ul className="space-y-2">
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

      {/* Error Message */}
      {error && <p className="text-red-600 text-sm">{error}</p>}

      {/* Report Preview */}
      {selectedCharts.length > 0 && (
        <div className="border p-4 rounded bg-gray-50">
          <h4 className="font-semibold mb-2">Report Preview:</h4>
          <ul className="list-disc pl-4 text-sm">
            {selectedCharts.map((id) => {
              const chart = availableCharts.find((c) => c.id === id);
              return <li key={id}>{chart?.title}</li>;
            })}
          </ul>
        </div>
      )}

      {/* Generate Report Button */}
      <button
        onClick={handleGenerateReport}
        className="bg-blue-600 text-white px-4 py-2 rounded flex items-center justify-center"
        disabled={loading}
      >
        {loading ? (
          <CircularProgress size={20} color="inherit" />
        ) : (
          "Generate Report"
        )}
      </button>
    </div>
  );
}
