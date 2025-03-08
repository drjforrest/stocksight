"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card } from "../ui/card";

interface MarketVolatilityProps {
  symbols: string[];
}

export default function MarketVolatility({ symbols }: MarketVolatilityProps) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVolatility();
  }, [symbols]);

  const fetchVolatility = async () => {
    try {
      const response = await axios.get(`/api/market/volatility`, {
        params: { symbols },
      });
      const formattedData = Object.entries(response.data).map(
        ([symbol, metrics]) => ({
          symbol,
          volatility: metrics.volatility,
          sharpe_ratio: metrics.sharpe_ratio,
        }),
      );

      setData(formattedData);
    } catch (err) {
      console.error("Error fetching market volatility", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p>Loading market volatility...</p>;

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">Market Volatility</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <XAxis dataKey="symbol" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="volatility" fill="#FF8042" name="Volatility" />
          <Bar dataKey="sharpe_ratio" fill="#00C49F" name="Sharpe Ratio" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
