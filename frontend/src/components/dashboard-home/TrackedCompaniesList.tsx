"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { FaTrash, FaExternalLinkAlt } from "react-icons/fa";
import { useRouter } from "next/navigation";
import { Card } from "../ui/card";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogActions,
  Button,
} from "@mui/material";

interface TrackedCompany {
  symbol: string;
  name: string;
  market_cap: number;
  sector: string;
  price: number;
}

export default function TrackedCompaniesList() {
  const [trackedCompanies, setTrackedCompanies] = useState<TrackedCompany[]>(
    [],
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const router = useRouter();
  const userId = 1; // TODO: Get from auth context

  useEffect(() => {
    fetchTrackedCompanies();
  }, []);

  const fetchTrackedCompanies = async () => {
    try {
      const response = await axios.get(`/api/tracked/${userId}`);
      setTrackedCompanies(response.data);
      setError(null);
    } catch (err) {
      setError("Error fetching tracked companies");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveClick = (symbol: string) => {
    setSelectedCompany(symbol);
    setConfirmOpen(true);
  };

  const confirmRemoveCompany = async () => {
    if (!selectedCompany) return;
    try {
      await axios.delete(`/api/tracked/${userId}/${selectedCompany}`);
      setTrackedCompanies((prev) =>
        prev.filter((company) => company.symbol !== selectedCompany),
      );
    } catch (err) {
      setError(`Error removing ${selectedCompany}`);
      console.error(err);
    } finally {
      setConfirmOpen(false);
      setSelectedCompany(null);
    }
  };

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return <Card className="bg-red-50 text-red-700 p-4 rounded">{error}</Card>;
  }

  if (trackedCompanies.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow-md">
        <h3 className="text-2xl font-semibold mb-4">No Companies Tracked</h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Start tracking companies to receive updates and insights.
        </p>
        <button
          onClick={() => router.push("/browse")}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center justify-center gap-2 mx-auto"
        >
          Track Companies
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {trackedCompanies.map((company) => (
          <Card
            key={company.symbol}
            className="p-6 shadow-md bg-white rounded-lg"
          >
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">
                {company.name} ({company.symbol})
              </h3>
              <button
                onClick={() => handleRemoveClick(company.symbol)}
                className="text-red-500 hover:text-red-700"
                title="Remove from tracking"
              >
                <FaTrash />
              </button>
            </div>
            <p className="text-gray-600 text-sm mt-1">{company.sector}</p>

            <div className="flex justify-between mt-4">
              <div>
                <p className="text-sm text-gray-500">Market Cap</p>
                <p className="text-lg font-semibold">
                  {formatCurrency(company.market_cap)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Stock Price</p>
                <p className="text-lg font-semibold">
                  ${company.price.toFixed(2)}
                </p>
              </div>
            </div>

            <button
              onClick={() => router.push(`/tracked/${company.symbol}`)}
              className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded flex items-center justify-center gap-2"
            >
              <FaExternalLinkAlt />
              View Details
            </button>
          </Card>
        ))}
      </div>

      {/* Confirmation Dialog */}
      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <DialogTitle>Remove Tracked Company</DialogTitle>
        <DialogContent>
          <p>
            Are you sure you want to remove {selectedCompany} from tracking?
          </p>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={confirmRemoveCompany} color="error">
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
