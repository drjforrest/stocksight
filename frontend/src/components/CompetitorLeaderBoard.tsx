'use client';

import React, { useEffect, useState } from "react";
import axios from "axios";

interface Competitor {
  symbol: string;
  name: string;
  score: number;
}

export default function CompetitorLeaderboard() {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCompetitors() {
      try {
        const response = await axios.get(`/api/competitor-scores`);
        setCompetitors(response.data);
      } catch (err) {
        setError("Failed to fetch competitor scores");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchCompetitors();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">Competitor Rankings</h2>
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="text-left p-2">Company</th>
            <th className="text-left p-2">Symbol</th>
            <th className="text-right p-2">Score</th>
          </tr>
        </thead>
        <tbody>
          {competitors.map((comp, index) => (
            <tr key={index} className="border-b">
              <td className="p-2">{comp.name}</td>
              <td className="p-2">{comp.symbol}</td>
              <td className="p-2 text-right font-bold">{comp.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}