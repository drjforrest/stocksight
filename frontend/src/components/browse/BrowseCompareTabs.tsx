"use client";

import React, { useState } from "react";
import { Box, Tabs, Tab } from "@mui/material";
import SearchBrowse from "./SearchBrowse";
import CompareCompanies from "./CompareCompanies";
import type { Company } from "@/types/company";

export default function BrowseCompareTabs() {
  const [activeTab, setActiveTab] = useState<0 | 1>(0);
  const [selectedCompanies, setSelectedCompanies] = useState<Company[]>([]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: 0 | 1) => {
    setActiveTab(newValue);
  };

  const handleAddToCompare = (company: Company) => {
    if (selectedCompanies.length >= 3) {
      // Optional: Show a notification that max 3 companies can be compared
      return;
    }
    setSelectedCompanies((prev) =>
      prev.some((c) => c.symbol === company.symbol)
        ? prev
        : [...prev, company],
    );
    setActiveTab(1); // Switch to Compare tab
  };

  const handleRemoveCompany = (symbol: string) => {
    setSelectedCompanies((prev) => prev.filter((c) => c.symbol !== symbol));
  };

  const handleResetComparison = () => {
    setSelectedCompanies([]);
    setActiveTab(0); // Switch back to Search tab
  };

  return (
    <Box sx={{ width: "100%" }}>
      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          centered
          sx={{ mb: 2 }}
        >
          <Tab
            label="Browse Companies"
            sx={{ textTransform: "none", fontWeight: 600 }}
          />
          <Tab
            label={`Compare (${selectedCompanies.length})`}
            sx={{ textTransform: "none", fontWeight: 600 }}
          />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <Box sx={{ mt: 2 }}>
        {activeTab === 0 ? (
          <SearchBrowse addToCompare={handleAddToCompare} />
        ) : (
          <CompareCompanies
            selectedCompanies={selectedCompanies}
            removeCompany={handleRemoveCompany}
            resetComparison={handleResetComparison}
          />
        )}
      </Box>
    </Box>
  );
}
