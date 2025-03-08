"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";

interface PipelineComparisonChartProps {
  symbols: string[];
}

export default function PipelineComparisonChart({
  symbols,
}: PipelineComparisonChartProps) {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    if (symbols.length === 0) return;

    const fetchPipelineData = async () => {
      try {
        const response = await axios.get(
          "/api/competitors/analysis/pipeline-comparison",
          {
            params: { symbols },
          },
        );
        setData(response.data);
      } catch (error) {
        console.error("Error fetching pipeline data", error);
      }
    };

    fetchPipelineData();
  }, [symbols]);

  if (!data) return <p className="text-center">Loading pipeline data...</p>;

  const chartData = {
    labels: symbols,
    datasets: [
      {
        label: "Preclinical",
        data: data.stages.map((s: any) => s.preclinical),
        backgroundColor: "#FF6384",
      },
      {
        label: "Phase 1",
        data: data.stages.map((s: any) => s.phase_1),
        backgroundColor: "#36A2EB",
      },
      {
        label: "Phase 2",
        data: data.stages.map((s: any) => s.phase_2),
        backgroundColor: "#FFCE56",
      },
      {
        label: "Phase 3",
        data: data.stages.map((s: any) => s.phase_3),
        backgroundColor: "#4CAF50",
      },
      {
        label: "Phase 4",
        data: data.stages.map((s: any) => s.phase_4),
        backgroundColor: "#8E44AD",
      },
    ],
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">Pipeline Comparison</h2>
      <Bar data={chartData} />
    </div>
  );
}
