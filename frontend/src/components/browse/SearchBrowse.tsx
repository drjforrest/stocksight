"use client";

import React, { useState, useRef } from "react";
import {
  Box,
  Card,
  Typography,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  IconButton,
  Tooltip,
  Chip,
  Alert,
  Snackbar,
} from "@mui/material";
import {
  CompareArrows,
  AddCircleOutline,
  Search as SearchIcon,
  HelpOutline as HelpIcon,
} from "@mui/icons-material";
import { useQuery } from "@tanstack/react-query";
import debounce from "lodash/debounce";
import type { SearchBrowseProps, SearchFilters, Company } from "@/types/company";
import { CompanyCardSkeleton } from "./LoadingSkeleton";
import BrowseHelp from "./BrowseHelp";

export default function SearchBrowse({ addToCompare }: SearchBrowseProps) {
  // State for filters & search
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({
    marketCap: "",
    hasApprovedDrugs: false,
    therapeuticArea: "",
    trialPhase: "",
  });
  const [showHelp, setShowHelp] = useState(false);

  // Snackbar state
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success" as "success" | "error",
  });

  // Debounced search handler
  const debouncedSearch = debounce((value: string) => {
    setSearchQuery(value);
  }, 500);

  // Fetch companies with filters
  const {
    data: companies = [],
    isLoading,
    error,
  } = useQuery<Company[]>({
    queryKey: ["companies", searchQuery, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append("query", searchQuery);
      if (filters.marketCap) params.append("market_cap", filters.marketCap);
      if (filters.hasApprovedDrugs) params.append("has_approved_drugs", "true");
      if (filters.therapeuticArea)
        params.append("therapeutic_area", filters.therapeuticArea);
      if (filters.trialPhase) params.append("trial_phase", filters.trialPhase);

      const response = await fetch(`/api/companies/search?${params}`);
      if (!response.ok) throw new Error("Failed to fetch companies");
      return response.json();
    },
  });

  // Handle track company
  const handleTrackCompany = async (company: Company) => {
    try {
      await fetch("/api/tracked/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: company.symbol }),
      });
      setSnackbar({
        open: true,
        message: `Added ${company.symbol} to tracking`,
        severity: "success",
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: `Error tracking ${company.symbol}`,
        severity: "error",
      });
    }
  };

  const CompanyCard = ({ company }: { company: Company }) => (
    <Card className="p-4">
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          mb: 2,
        }}
      >
        <div>
          <Typography variant="h6">{company.name}</Typography>
          <Typography variant="caption" color="text.secondary">
            {company.symbol}
          </Typography>
        </div>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Compare">
            <IconButton
              onClick={() => addToCompare(company)}
              color="primary"
              size="small"
            >
              <CompareArrows />
            </IconButton>
          </Tooltip>
          <Tooltip title="Track Company">
            <IconButton
              onClick={() => handleTrackCompany(company)}
              color="success"
              size="small"
            >
              <AddCircleOutline />
            </IconButton>
          </Tooltip>
        </Stack>
      </Box>

      <Stack spacing={2}>
        <Box>
          <Typography variant="body2" color="text.secondary">
            Market Cap
          </Typography>
          <Typography variant="h6">
            ${(company.market_cap / 1e9).toFixed(2)}B
          </Typography>
        </Box>

        <Box>
          <Typography variant="body2" color="text.secondary">
            Stock Price
          </Typography>
          <Stack direction="row" spacing={1} alignItems="baseline">
            <Typography variant="h6">${company.price.toFixed(2)}</Typography>
            <Typography
              color={
                company.change_percent >= 0 ? "success.main" : "error.main"
              }
            >
              {company.change_percent >= 0 ? "+" : ""}
              {company.change_percent.toFixed(2)}%
            </Typography>
          </Stack>
        </Box>

        {company.therapeutic_areas && company.therapeutic_areas.length > 0 && (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Therapeutic Areas
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {company.therapeutic_areas.map((area) => (
                <Chip
                  key={area}
                  label={area}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Stack>
          </Box>
        )}

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              FDA Submissions
            </Typography>
            <Typography>{company.fda_submissions || 0}</Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Active Trials
            </Typography>
            <Typography>{company.active_trials || 0}</Typography>
          </Grid>
        </Grid>
      </Stack>
    </Card>
  );

  return (
    <Box>
      {/* Help Modal */}
      <BrowseHelp open={showHelp} onClose={() => setShowHelp(false)} />

      {/* Search & Filters */}
      <Stack spacing={3} sx={{ mb: 4 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <TextField
            label="Search Companies"
            variant="outlined"
            fullWidth
            onChange={(e) => debouncedSearch(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ color: "text.secondary", mr: 1 }} />,
            }}
          />
          <Tooltip title="Browse & Analytics Help">
            <IconButton
              onClick={() => setShowHelp(true)}
              color="primary"
              sx={{ flexShrink: 0 }}
            >
              <HelpIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Market Cap</InputLabel>
              <Select
                value={filters.marketCap}
                label="Market Cap"
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    marketCap: e.target.value as string,
                  }))
                }
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="1B">Over $1B</MenuItem>
                <MenuItem value="10B">Over $10B</MenuItem>
                <MenuItem value="50B">Over $50B</MenuItem>
                <MenuItem value="100B">Over $100B</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Therapeutic Area</InputLabel>
              <Select
                value={filters.therapeuticArea}
                label="Therapeutic Area"
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    therapeuticArea: e.target.value as string,
                  }))
                }
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="Oncology">Oncology</MenuItem>
                <MenuItem value="Immunology">Immunology</MenuItem>
                <MenuItem value="Neurology">Neurology</MenuItem>
                <MenuItem value="Cardiology">Cardiology</MenuItem>
                <MenuItem value="Rare Diseases">Rare Diseases</MenuItem>
                <MenuItem value="Gene Therapy">Gene Therapy</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Trial Phase</InputLabel>
              <Select
                value={filters.trialPhase}
                label="Trial Phase"
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    trialPhase: e.target.value as string,
                  }))
                }
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="phase1">Phase 1</MenuItem>
                <MenuItem value="phase2">Phase 2</MenuItem>
                <MenuItem value="phase3">Phase 3</MenuItem>
                <MenuItem value="phase4">Phase 4</MenuItem>
                <MenuItem value="approved">Approved</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>FDA Status</InputLabel>
              <Select
                value={filters.hasApprovedDrugs ? "approved" : "all"}
                label="FDA Status"
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    hasApprovedDrugs: e.target.value === "approved",
                  }))
                }
              >
                <MenuItem value="all">All Companies</MenuItem>
                <MenuItem value="approved">With Approved Drugs</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Active Filters Display */}
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {Object.entries(filters).map(([key, value]) => {
            if (!value) return null;
            return (
              <Chip
                key={key}
                label={`${key.replace(/([A-Z])/g, ' $1').trim()}: ${value}`}
                onDelete={() =>
                  setFilters((prev) => ({ ...prev, [key]: key === 'hasApprovedDrugs' ? false : '' }))
                }
                color="primary"
                variant="outlined"
                size="small"
              />
            );
          })}
        </Stack>
      </Stack>

      {/* Results */}
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error fetching companies
        </Alert>
      ) : isLoading ? (
        <Grid container spacing={3}>
          {[...Array(4)].map((_, i) => (
            <Grid item xs={12} md={6} key={i}>
              <CompanyCardSkeleton />
            </Grid>
          ))}
        </Grid>
      ) : companies.length === 0 ? (
        <Alert severity="info">No companies found matching your criteria.</Alert>
      ) : (
        <Grid container spacing={3}>
          {companies.map((company) => (
            <Grid item xs={12} md={6} key={company.symbol}>
              <CompanyCard company={company} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
      >
        <Alert severity={snackbar.severity} sx={{ width: "100%" }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
