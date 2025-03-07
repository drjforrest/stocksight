'use client';

import React, { useState } from "react";
import axios from "axios";

export default function CompetitorSearch({ onSelect }: { onSelect: (competitor: any) => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/competitors?query=${query}`);
      setResults(response.data);
    } catch (err) {
      setError("No competitors found");
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-2">Search for Competitors</h2>
      <div className="flex mb-4">
        <input
          type="text"
          placeholder="Company name or stock symbol..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-grow p-2 border rounded"
        />
        <button onClick={handleSearch} className="ml-2 bg-blue-600 text-white px-4 py-2 rounded">
          Search
        </button>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      <ul>
        {results.map((comp) => (
          <li key={comp.symbol} className="flex justify-between items-center p-2 border-b">
            <div>
              <span className="font-bold">{comp.name} ({comp.symbol})</span>
              <p className="text-sm text-gray-500">Therapeutic Area: {comp.therapeutic_area}</p>
            </div>
            <button
              onClick={() => onSelect(comp)}
              className="bg-green-500 text-white px-3 py-1 rounded"
            >
              Save
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}