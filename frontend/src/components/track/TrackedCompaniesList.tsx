"use client";

import React from "react";
import TrackedCompanyCard from "./TrackedCompanyCard";

interface TrackedCompaniesListProps {
  tracked: string[];
  refreshTracked: () => void;
}

export default function TrackedCompaniesList({
  tracked,
  refreshTracked,
}: TrackedCompaniesListProps) {
  if (tracked.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow-md">
        <h3 className="text-2xl font-semibold mb-4">
          Start Tracking Companies
        </h3>
        <p className="text-gray-600 mb-6">
          Track companies to get real-time updates, news, and market insights.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {tracked.map((symbol) => (
        <TrackedCompanyCard
          key={symbol}
          symbol={symbol}
          refreshTracked={refreshTracked}
        />
      ))}
    </div>
  );
}
