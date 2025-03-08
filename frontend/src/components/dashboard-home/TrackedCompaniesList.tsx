"use client";

import React from "react";
import { Card } from "../ui/card";
import { TrackedCompaniesListProps } from "./types";

export default function TrackedCompaniesList({
  trackedCompanies,
  onRemoveCompany,
}: TrackedCompaniesListProps) {
  if (trackedCompanies.length === 0) {
    return (
      <Card className="p-6 text-center text-gray-500">
        <p>No companies tracked yet.</p>
        <p className="text-sm mt-2">
          Use the Browse page to find and track companies.
        </p>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {trackedCompanies.map((company) => (
        <Card key={company.symbol} className="p-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-bold">{company.name}</h3>
              <p className="text-sm text-gray-500">{company.symbol}</p>
            </div>
            <button
              onClick={() => onRemoveCompany(company.symbol)}
              className="text-red-500 hover:text-red-700"
            >
              Remove
            </button>
          </div>
          
          <div className="mt-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-500">Market Cap</span>
              <span>${(company.market_cap / 1e9).toFixed(2)}B</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Price</span>
              <span className="flex items-center gap-2">
                ${company.price.toFixed(2)}
                <span className={company.change_percent >= 0 ? "text-green-500" : "text-red-500"}>
                  {company.change_percent >= 0 ? "+" : ""}
                  {company.change_percent.toFixed(2)}%
                </span>
              </span>
            </div>
            {company.active_trials !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-500">Active Trials</span>
                <span>{company.active_trials}</span>
              </div>
            )}
            {company.fda_submissions !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-500">FDA Submissions</span>
                <span>{company.fda_submissions}</span>
              </div>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}
