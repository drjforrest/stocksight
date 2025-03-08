"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card } from "../ui/card";

interface StockPredictionProps {
  symbol: string;
  daysAhead?: number;
}

export default function StockPrediction({
  symbol,
  daysAhead = 30,
}: StockPredictionProps) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPredictions();
  }, [symbol]);

  const fetchPredictions = async () => {
    try {
      const response = await axios.get(`/api/market/predict-stock`, {
        params: { symbol, days_ahead: daysAhead },
      });

      const { forecast_dates, models } = response.data;
      const formattedData = forecast_dates.map((date: string, i: number) => ({
        date,
        holtwinters: models.holtwinters?.forecast[i] || null,
        arima: models.arima?.forecast[i] || null,
        prophet: models.prophet?.forecast[i] || null,
        ensemble: models.ensemble?.forecast[i] || null,
      }));

      setData(formattedData);
    } catch (err) {
      console.error("Error fetching stock predictions", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p>Loading stock predictions...</p>;

  return (
    <Card className="p-6">
      <h2 className="text-xl font-bold mb-4">
        Stock Price Forecast ({symbol})
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="holtwinters"
            stroke="#8884d8"
            name="Holt-Winters"
          />
          <Line type="monotone" dataKey="arima" stroke="#82ca9d" name="ARIMA" />
          <Line
            type="monotone"
            dataKey="prophet"
            stroke="#FFBB28"
            name="Prophet"
          />
          <Line
            type="monotone"
            dataKey="ensemble"
            stroke="#FF8042"
            name="Ensemble (Weighted)"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
