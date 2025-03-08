"use client";

import React from "react";
import { Grid, Box, Typography, Paper } from "@mui/material";
import TrackedCompanyCard from "./TrackedCompanyCard";

interface TrackedCompaniesListProps {
  tracked: string[];
  refreshTracked: () => void;
  selectedCompany: string | null;
}

export default function TrackedCompaniesList({
  tracked,
  refreshTracked,
  selectedCompany,
}: TrackedCompaniesListProps) {
  if (tracked.length === 0) {
    return (
      <Box sx={{ textAlign: "center", py: 8, bgcolor: "background.paper", borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          Start Tracking Companies
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track companies to get real-time updates, news, and market insights.
        </Typography>
      </Box>
    );
  }

  // Filter companies if one is selected
  const displayedCompanies = selectedCompany
    ? tracked.filter(symbol => symbol === selectedCompany)
    : tracked;

  return (
    <Grid container spacing={3}>
      {displayedCompanies.map((symbol) => (
        <Grid item xs={12} md={selectedCompany ? 12 : 6} key={symbol}>
          <TrackedCompanyCard
            symbol={symbol}
            refreshTracked={refreshTracked}
            expanded={selectedCompany === symbol}
          />
        </Grid>
      ))}
    </Grid>
  );
}
