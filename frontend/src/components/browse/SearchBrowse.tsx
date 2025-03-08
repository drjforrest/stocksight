"use client";

import React, { useState, useRef } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Button,
  Tooltip,
  Snackbar,
  Alert,
  IconButton,
  Chip,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import {
  CompareArrows,
  AddCircleOutline,
  FileDownload as FileDownloadIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
import debounce from "lodash/debounce";
import { useRouter } from "next/navigation";
import MarketOverviewCards from "../dashboard-home/MarketOverviewCards";
import { Company } from "./types";

interface SearchBrowseProps {
  addToCompare: (company: Company) => void;
}

export default function SearchBrowse({ addToCompare }: SearchBrowseProps) {
  const router = useRouter();
  const searchInputRef = useRef<HTMLInputElement>(null);

  // State for filters & pagination
  const [searchQuery, setSearchQuery] = useState("");
  const [marketCap, setMarketCap] = useState<string>("");
  const [hasApprovedDrugs, setHasApprovedDrugs] = useState<boolean>(false);

  // Snackbar state for notifications
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success" as "success" | "error",
  });

  // Debounced search handler
  const debouncedSearch = debounce((value: string) => {
    setSearchQuery(value);
  }, 500);

  // Fetch companies
  const {
    data: browseData,
    isLoading,
    isError,
  } = useQuery<{ results: Company[] }>({
    queryKey: ["browseCompanies", { searchQuery, marketCap, hasApprovedDrugs }],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append("query", searchQuery);
      if (marketCap) params.append("market_cap", marketCap);
      if (hasApprovedDrugs) params.append("has_approved_drugs", "true");

      const response = await fetch(`/api/browse/companies?${params}`);
      if (!response.ok) throw new Error("Failed to fetch companies");
      return response.json();
    },
  });

  // Handle track company
  const handleTrackCompany = async (symbol: string) => {
    try {
      await fetch(`/api/tracked/add`, {
        method: "POST",
        body: JSON.stringify({ symbol }),
      });
      setSnackbar({
        open: true,
        message: `Added ${symbol} to tracking`,
        severity: "success",
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: `Error tracking ${symbol}`,
        severity: "error",
      });
    }
  };

  const CompanyCard = ({ company }: { company: Company }) => (
    <Card>
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            mb: 2,
          }}
        >
          <Typography variant="h6" gutterBottom>
            {company.name} ({company.symbol})
          </Typography>
          <Stack direction="row" spacing={1}>
            <Tooltip title="Compare">
              <IconButton onClick={() => addToCompare(company)} color="primary">
                <CompareArrows />
              </IconButton>
            </Tooltip>
            <Tooltip title="Track Company">
              <IconButton
                onClick={() => handleTrackCompany(company.symbol)}
                color="success"
              >
                <AddCircleOutline />
              </IconButton>
            </Tooltip>
          </Stack>
        </Box>

        <Typography variant="body2" color="text.secondary">
          Market Cap: ${company.market_cap.toFixed(2)}B
        </Typography>
        <Typography variant="subtitle2">
          FDA Submissions: {company.fda_submissions}
        </Typography>
        <Typography variant="subtitle2">
          Active Clinical Trials: {company.active_trials}
        </Typography>

        <Typography variant="subtitle2">Approved Drugs:</Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          {company.approved_drugs.map((drug) => (
            <Chip key={drug} label={drug} size="small" color="success" />
          ))}
        </Stack>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4">Browse Biotech Companies</Typography>
      </Box>

      {/* Market Overview Cards for context */}
      <MarketOverviewCards />

      <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
        <TextField
          label="Search Company"
          variant="outlined"
          fullWidth
          inputRef={searchInputRef}
          onChange={(e) => debouncedSearch(e.target.value)}
          InputProps={{ startAdornment: <SearchIcon /> }}
        />
        <FormControl variant="outlined" fullWidth>
          <InputLabel>Market Cap</InputLabel>
          <Select
            value={marketCap}
            onChange={(e) => setMarketCap(e.target.value)}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="1B">Over $1B</MenuItem>
            <MenuItem value="10B">Over $10B</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={2}>
        {isLoading ? (
          <Typography>Loading...</Typography>
        ) : isError ? (
          <Typography color="error">Error fetching companies</Typography>
        ) : browseData?.results.length === 0 ? (
          <Typography>No companies found.</Typography>
        ) : (
          browseData?.results.map((company) => (
            <Grid item xs={12} md={6} key={company.symbol}>
              <CompanyCard company={company} />
            </Grid>
          ))
        )}
      </Grid>

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
