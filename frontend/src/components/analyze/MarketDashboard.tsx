"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { Select, MenuItem, FormControl, InputLabel } from "@mui/material";
import StockPrediction from "./StockPrediction";
import MarketVolatility from "./MarketVolatility";
import IPOSuccess from "./IPOSuccess";

export default function AnalyzePage() {
  const [trackedCompanies, setTrackedCompanies] = useState<string[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>("");

  useEffect(() => {
    fetchTrackedCompanies();
  }, []);

  const fetchTrackedCompanies = async () => {
    try {
      const response = await axios.get("/api/tracked");
      setTrackedCompanies(response.data);
      if (response.data.length > 0) {
        setSelectedCompany(response.data[0]); // Default to the first company
      }
    } catch (err) {
      console.error("Error fetching tracked companies", err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Dropdown for Selecting a Company */}
      <FormControl fullWidth>
        <InputLabel>Select a Company</InputLabel>
        <Select
          value={selectedCompany}
          onChange={(e) => setSelectedCompany(e.target.value)}
        >
          {trackedCompanies.map((company) => (
            <MenuItem key={company} value={company}>
              {company}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Dynamic Analysis Components */}
      {selectedCompany && (
        <>
          <StockPrediction symbol={selectedCompany} />
          <MarketVolatility symbols={[selectedCompany]} />
          <IPOSuccess />
        </>
      )}
    </div>
  );
}
