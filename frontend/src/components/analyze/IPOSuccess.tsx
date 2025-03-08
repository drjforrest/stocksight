// This component visualizes IPO success rates, withdrawal rates, and pricing trends.

"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts";
import { Card } from "../ui/card";

export default function IPOSuccess({
  timeframeDays = 365,
}: {
  timeframeDays?: number;
}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIPOSuccess();
  }, []);

  const fetchIPOSuccess = async () => {
    try {
      const response = await axios.get(`/api/market/ipo-success`, {
        params: { timeframe_days: timeframeDays },
      });
      setData(response.data);
    } catch (err) {
      console.error("Error fetching IPO success data", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p>Loading IPO success data...</p>;

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">IPO Success Rates</h2>

      {/* Completion vs Withdrawal Pie Chart */}
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data?.visualization_data?.completion_rates}
            dataKey="values"
            nameKey="labels"
            cx="50%"
            cy="50%"
            outerRadius={80}
          >
            <Cell fill="#00C49F" />
            <Cell fill="#FFBB28" />
            <Cell fill="#FF8042" />
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>

      {/* Pricing Trends */}
      <h3 className="text-lg font-bold mt-4">IPO Pricing Trends</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data?.visualization_data?.valuation_distribution}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="bin_edges" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="bins" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
