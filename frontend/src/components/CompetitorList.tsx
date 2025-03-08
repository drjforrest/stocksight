'use client';

import React, { useEffect, useState } from "react";
import { api } from '@/lib/api';
import { Competitor, FeatureFlags } from "../types/competitor";

export default function CompetitorList() {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [featureEnabled, setFeatureEnabled] = useState(false);

  useEffect(() => {
    api.get<FeatureFlags>('/feature-flags').then((res) => {
      setFeatureEnabled(res.data.competitor_score);
    });

    api.get<Competitor[]>('/competitors').then((res) => {
      setCompetitors(res.data);
    });
  }, []);

  return (
    <div className="p-6 bg-white rounded shadow-lg">
      <h2 className="text-xl font-bold">Competitor List</h2>
      <ul>
        {competitors.map((comp) => (
          <li key={comp.symbol} className="flex justify-between p-2 border-b">
            <div>
              <span className="font-bold">{comp.name} ({comp.symbol})</span>
              <p className="text-sm text-gray-500">Market Cap: ${comp.market_cap}B</p>
            </div>
            {featureEnabled && comp.competitiveness_score !== null && (
              <span className="text-sm bg-blue-100 px-2 py-1 rounded">
                Score: {comp.competitiveness_score}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}