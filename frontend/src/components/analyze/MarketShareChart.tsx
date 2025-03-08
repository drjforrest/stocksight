'use client';

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Pie } from "react-chartjs-2";

export default function MarketShareChart({ therapeuticArea }: { therapeuticArea?: string }) {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchMarketShare = async () => {
      try {
        const response = await axios.get(`/api/competitors/analysis/market-share`, {
          params: { therapeutic_area: therapeuticArea },
        });
        setData(response.data);
      } catch (error) {
        console.error("Failed to fetch market share data", error);
      }
    };

    fetchMarketShare();
  }, [therapeuticArea]);

  if (!data) return <p>Loading...</p>;

  const chartData = {
    labels: data.competitors.map((comp: any) => comp.name),
    datasets: [
      {
        data: data.competitors.map((comp: any) => comp.market_share),
        backgroundColor: ["#4CAF50", "#FF9800", "#2196F3", "#9C27B0"],
      },
    ],
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">Market Share Distribution</h2>
      <Pie data={chartData} />
    </div>
  );
}