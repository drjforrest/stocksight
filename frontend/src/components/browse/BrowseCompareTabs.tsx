"use client";

import React, { useState } from "react";
import { Box, Tabs, Tab } from "@mui/material";
import SearchBrowse from "./SearchBrowse";
import CompareCompanies from "./CompareCompanies";
import { Company } from "./types"; // Ensure type consistency across components

export default function BrowseCompareTabs() {
  const [tab, setTab] = useState<0 | 1>(0);
  const [selectedCompanies, setSelectedCompanies] = useState<Company[]>([]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: 0 | 1) => {
    setTab(newValue);
  };

  const addToCompare = (company: Company) => {
    setSelectedCompanies((prev) =>
      prev.some((c) => c.symbol === company.symbol) ? prev : [...prev, company],
    );
    setTab(1); // Switch to Compare tab
  };

  const removeFromCompare = (symbol: string) => {
    setSelectedCompanies((prev) => prev.filter((c) => c.symbol !== symbol));
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Tabs */}
      <Tabs value={tab} onChange={handleTabChange} centered>
        <Tab label="Browse Companies" />
        <Tab label={`Compare (${selectedCompanies.length})`} />
      </Tabs>

      {/* Render Based on Tab */}
      {tab === 0 ? (
        <SearchBrowse addToCompare={addToCompare} />
      ) : (
        <CompareCompanies
          selectedCompanies={selectedCompanies}
          removeFromCompare={removeFromCompare}
        />
      )}
    </Box>
  );
}
