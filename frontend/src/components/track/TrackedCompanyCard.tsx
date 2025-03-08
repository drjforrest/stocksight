"use client";

import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Grid,
  Box,
  Stack,
  Chip,
  Collapse,
  Divider,
} from "@mui/material";
import {
  Delete as DeleteIcon,
  OpenInNew as OpenInNewIcon,
  TrendingUp,
  TrendingDown,
  Science,
  LocalPharmacy,
  BarChart,
} from "@mui/icons-material";
import axios from "axios";

interface TrackedCompanyCardProps {
  symbol: string;
  refreshTracked: () => void;
  expanded: boolean;
}

export default function TrackedCompanyCard({
  symbol,
  refreshTracked,
  expanded,
}: TrackedCompanyCardProps) {
  const [companyData, setCompanyData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanyData();
  }, [symbol]);

  const fetchCompanyData = async () => {
    try {
      const response = await axios.get(`/api/companies/${symbol}/details`);
      setCompanyData(response.data);
    } catch (err) {
      console.error(`Error fetching ${symbol} data`);
    } finally {
      setLoading(false);
    }
  };

  const removeCompany = async () => {
    try {
      await axios.delete(`/api/tracked/${symbol}`);
      refreshTracked();
    } catch (err) {
      console.error(`Error removing ${symbol}`);
    }
  };

  if (loading) {
    return (
      <Card sx={{ p: 3, bgcolor: "grey.100" }}>
        <Box sx={{ height: expanded ? 400 : 200 }} className="animate-pulse" />
      </Card>
    );
  }

  return (
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        transition: "all 0.3s ease",
      }}
    >
      <CardContent>
        {/* Header */}
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
          <Box>
            <Typography variant="h5" gutterBottom>
              {companyData.name}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              {symbol}
            </Typography>
          </Box>
          <IconButton
            onClick={removeCompany}
            color="error"
            sx={{ alignSelf: "flex-start" }}
          >
            <DeleteIcon />
          </IconButton>
        </Box>

        {/* Key Metrics */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Market Cap
            </Typography>
            <Typography variant="h6">
              ${(companyData.market_cap / 1e9).toFixed(2)}B
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Stock Price
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="h6">
                ${companyData.price.toFixed(2)}
              </Typography>
              <Typography
                color={companyData.change_percent >= 0 ? "success.main" : "error.main"}
                sx={{ display: "flex", alignItems: "center" }}
              >
                {companyData.change_percent >= 0 ? (
                  <TrendingUp fontSize="small" />
                ) : (
                  <TrendingDown fontSize="small" />
                )}
                {Math.abs(companyData.change_percent).toFixed(2)}%
              </Typography>
            </Stack>
          </Grid>
        </Grid>

        {/* Quick Stats */}
        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Chip
            icon={<Science />}
            label={`${companyData.active_trials || 0} Active Trials`}
            color="primary"
            variant="outlined"
          />
          <Chip
            icon={<LocalPharmacy />}
            label={`${companyData.fda_submissions || 0} FDA Submissions`}
            color="primary"
            variant="outlined"
          />
        </Stack>

        {/* Expanded Content */}
        <Collapse in={expanded} timeout="auto">
          <Divider sx={{ my: 2 }} />
          
          {/* Therapeutic Areas */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Therapeutic Areas
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {companyData.therapeutic_areas?.map((area: string) => (
                <Chip
                  key={area}
                  label={area}
                  size="small"
                  sx={{ mb: 1 }}
                />
              ))}
            </Stack>
          </Box>

          {/* Pipeline Overview */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Pipeline Overview
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(companyData.pipeline || {}).map(([phase, count]) => (
                <Grid item xs={6} key={phase}>
                  <Typography variant="body2" color="text.secondary">
                    {phase}
                  </Typography>
                  <Typography>{String(count)}</Typography>
                </Grid>
              ))}
            </Grid>
          </Box>

          {/* Financial Metrics */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Financial Metrics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Revenue (TTM)
                </Typography>
                <Typography>
                  ${((companyData.revenue || 0) / 1e6).toFixed(1)}M
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  R&D Spend
                </Typography>
                <Typography>
                  ${((companyData.rd_spend || 0) / 1e6).toFixed(1)}M
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Cash Position
                </Typography>
                <Typography>
                  ${((companyData.cash_position || 0) / 1e6).toFixed(1)}M
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Burn Rate
                </Typography>
                <Typography>
                  ${((companyData.burn_rate || 0) / 1e6).toFixed(1)}M/month
                </Typography>
              </Grid>
            </Grid>
          </Box>
        </Collapse>

        {/* Actions */}
        <Box sx={{ mt: 'auto', pt: 2 }}>
          <Button
            variant="outlined"
            fullWidth
            startIcon={expanded ? <BarChart /> : <OpenInNewIcon />}
          >
            {expanded ? "View Analytics" : "View Details"}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}
