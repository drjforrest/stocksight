"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from "@mui/material";
import StockPrediction from "./StockPrediction";
import MarketVolatility from "./MarketVolatility";
import IPOSuccess from "./IPOSuccess";
import MarketShareChart from "./MarketShareChart";
import MarketTrends from "./MarketImpact";
import AdvancedAnalytics from "./AdvancedAnalytics";

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function MarketDashboard() {
  const [trackedCompanies, setTrackedCompanies] = useState<string[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const [timeframe, setTimeframe] = useState<"1m" | "3m" | "6m" | "1y">("3m");

  useEffect(() => {
    fetchTrackedCompanies();
  }, []);

  const fetchTrackedCompanies = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/api/tracked");
      setTrackedCompanies(response.data);
      if (response.data.length > 0) {
        setSelectedCompanies([response.data[0]]); // Default to first company
      }
      setError(null);
    } catch (err) {
      setError("Error fetching tracked companies");
      console.error("Error fetching tracked companies", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompanyChange = (event: any) => {
    const value = event.target.value;
    setSelectedCompanies(typeof value === "string" ? value.split(",") : value);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (trackedCompanies.length === 0) {
    return (
      <Alert severity="info">
        Please track some companies in the Browse section to view analytics.
      </Alert>
    );
  }

  return (
    <Box sx={{ width: "100%" }}>
      {/* Controls Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Select Companies</InputLabel>
              <Select
                multiple
                value={selectedCompanies}
                onChange={handleCompanyChange}
                renderValue={(selected) => (
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                    {selected.map((value) => (
                      <Typography key={value} component="span" sx={{ mr: 1 }}>
                        {value}
                      </Typography>
                    ))}
                  </Box>
                )}
              >
                {trackedCompanies.map((company) => (
                  <MenuItem key={company} value={company}>
                    {company}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Timeframe</InputLabel>
              <Select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value as typeof timeframe)}
              >
                <MenuItem value="1m">1 Month</MenuItem>
                <MenuItem value="3m">3 Months</MenuItem>
                <MenuItem value="6m">6 Months</MenuItem>
                <MenuItem value="1y">1 Year</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs Navigation */}
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          aria-label="analysis tabs"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="Price Predictions" />
          <Tab label="Market Volatility" />
          <Tab label="Market Share" />
          <Tab label="IPO Analysis" />
          <Tab label="Market Trends" />
          <Tab label="Advanced Analytics" />
        </Tabs>
      </Box>

      {/* Tab Panels */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          {selectedCompanies.map((symbol) => (
            <Grid item xs={12} key={symbol}>
              <StockPrediction symbol={symbol} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <MarketVolatility symbols={selectedCompanies} />
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <MarketShareChart />
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <IPOSuccess timeframeDays={
          timeframe === "1m" ? 30 :
          timeframe === "3m" ? 90 :
          timeframe === "6m" ? 180 : 365
        } />
      </TabPanel>

      <TabPanel value={activeTab} index={4}>
        <MarketTrends />
      </TabPanel>

      <TabPanel value={activeTab} index={5}>
        <AdvancedAnalytics 
          symbols={selectedCompanies}
          timeframe={timeframe}
        />
      </TabPanel>
    </Box>
  );
}
