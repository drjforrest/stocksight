"use client";

import React, { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { AlertCircle, X } from "lucide-react";
import MarketOverview from "./MarketOverview";
import TrackedCompaniesList from "./TrackedCompaniesList";
import WelcomeModal from "./WelcomeModal";
import { Card } from "../ui/card";
import { TrackedCompany } from "./types";

export default function Dashboard() {
  const queryClient = useQueryClient();
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    // Check if it's the user's first visit
    const hasVisited = localStorage.getItem("hasVisitedDashboard");
    if (!hasVisited) {
      setShowWelcome(true);
      localStorage.setItem("hasVisitedDashboard", "true");
    }
  }, []);

  // Fetch tracked companies
  const {
    data: trackedCompanies = [],
    isLoading,
    error,
  } = useQuery<TrackedCompany[]>({
    queryKey: ["trackedCompanies"],
    queryFn: async () => {
      const response = await axios.get("/api/tracked");
      return response.data;
    },
  });

  // Remove company mutation
  const removeMutation = useMutation({
    mutationFn: async (symbol: string) => {
      await axios.delete(`/api/tracked/${symbol}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trackedCompanies"] });
    },
  });

  // Handle remove company
  const handleRemoveCompany = async (symbol: string) => {
    return removeMutation.mutateAsync(symbol);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <>
      <WelcomeModal open={showWelcome} onClose={() => setShowWelcome(false)} />
      
      <div className="space-y-8 p-6">
        {/* Error Display */}
        {(error || removeMutation.error) && (
          <Card className="bg-red-50 border-red-200 p-4">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <div className="flex-1">
                <p className="text-red-600">
                  {error
                    ? "Failed to load tracked companies"
                    : "Failed to remove company"}
                </p>
              </div>
              <button
                onClick={() => queryClient.resetQueries({ queryKey: ["trackedCompanies"] })}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </Card>
        )}

        {/* Market Overview Section */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Market Overview</h2>
          <MarketOverview />
        </section>

        {/* Tracked Companies Section */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Your Tracked Companies</h2>
          <TrackedCompaniesList
            trackedCompanies={trackedCompanies}
            onRemoveCompany={handleRemoveCompany}
          />
        </section>
      </div>
    </>
  );
}
