'use client';

import React from "react";

export default function SavedCompetitors({ savedCompetitors }: { savedCompetitors: any[] }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-2">Tracked Competitors</h2>
      {savedCompetitors.length === 0 && <p>No competitors saved.</p>}
      <ul>
        {savedCompetitors.map((comp) => (
          <li key={comp.symbol} className="flex justify-between items-center p-2 border-b">
            <div>
              <span className="font-bold">{comp.name} ({comp.symbol})</span>
              <p className="text-sm text-gray-500">Market Cap: ${comp.market_cap}B</p>
            </div>
            <button
              className="bg-red-500 text-white px-3 py-1 rounded"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}