"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { FaTrash, FaExternalLinkAlt } from "react-icons/fa";

interface TrackedCompanyCardProps {
  symbol: string;
  refreshTracked: () => void;
}

export default function TrackedCompanyCard({
  symbol,
  refreshTracked,
}: TrackedCompanyCardProps) {
  const [companyData, setCompanyData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanyData();
  }, []);

  const fetchCompanyData = async () => {
    try {
      const response = await axios.get(`/api/companies/${symbol}/figures`);
      setCompanyData(response.data);
    } catch (err) {
      console.error(`Error fetching ${symbol} data`);
    } finally {
      setLoading(false);
    }
  };

  const removeCompany = async () => {
    try {
      await axios.delete(`/api/tracked/${symbol}`);
      refreshTracked();
    } catch (err) {
      console.error(`Error removing ${symbol}`);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-200 animate-pulse p-4 rounded-lg">Loading...</div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between">
        <h3 className="text-lg font-bold">
          {companyData.name} ({symbol})
        </h3>
        <button
          onClick={removeCompany}
          className="text-red-500 hover:text-red-700"
        >
          <FaTrash />
        </button>
      </div>
      <p>Market Cap: {companyData.market_cap}</p>
      <p>Therapeutic Area: {companyData.therapeutic_area}</p>
      <button className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded flex items-center justify-center gap-2">
        <FaExternalLinkAlt />
        View Details
      </button>
    </div>
  );
}
