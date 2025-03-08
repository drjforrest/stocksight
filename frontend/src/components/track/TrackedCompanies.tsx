"use client";

import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Typography,
  Tab,
  Tabs,
  Button,
  Alert,
  Paper,
  Divider,
} from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";
import axios from "axios";
import TrackedCompaniesList from "./TrackedCompaniesList";
import IPOInsights from "./IPOInsights";
import PipelineComparisonChart from "./PipelineComparisonChart";
import CompanyNews from "./CompanyNews";
import CompanyVisualizations from "./CompanyVisualizations";
import TrackedCompanySearch from "./TrackedCompanySearch";
import CompanyCarousel from "./CompanyCarousel";

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
      id={`tracked-tabpanel-${index}`}
      aria-labelledby={`tracked-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function TrackedCompanies() {
  const [tracked, setTracked] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSearch, setShowSearch] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [companyData, setCompanyData] = useState<any[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);

  useEffect(() => {
    fetchTrackedCompanies();
  }, []);

  useEffect(() => {
    if (tracked.length > 0) {
      fetchCompanyData();
    }
  }, [tracked]);

  const fetchTrackedCompanies = async () => {
    try {
      const response = await axios.get("/api/tracked");
      setTracked(response.data);
      setError(null);
    } catch (err) {
      setError("Error fetching tracked companies");
    } finally {
      setLoading(false);
    }
  };

  const fetchCompanyData = async () => {
    try {
      const promises = tracked.map(symbol => 
        axios.get(`/api/companies/${symbol}/details`)
      );
      const responses = await Promise.all(promises);
      setCompanyData(responses.map(res => res.data));
    } catch (err) {
      console.error("Error fetching company details:", err);
    }
  };

  const handleCompanySelect = async (company: any) => {
    try {
      await axios.post("/api/tracked/add", { symbol: company.symbol });
      setShowSearch(false);
      fetchTrackedCompanies();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Error adding ${company.symbol}`);
    }
  };

  const handleViewDetails = (symbol: string) => {
    setSelectedCompany(symbol);
    setActiveTab(0); // Switch to overview tab
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%" }}>
      {/* Header Section */}
      <Box sx={{ mb: 4, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Tracked Companies
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setShowSearch(!showSearch)}
        >
          {showSearch ? "Close Search" : "Add Company"}
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search Modal */}
      {showSearch && (
        <Box sx={{ mb: 4 }}>
          <TrackedCompanySearch onSelect={handleCompanySelect} />
        </Box>
      )}

      {tracked.length === 0 ? (
        <Box sx={{ textAlign: "center", py: 8, bgcolor: "background.paper", borderRadius: 1 }}>
          <Typography variant="h6" gutterBottom>
            Start Tracking Companies
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Track companies to get detailed insights, news, and market analysis.
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setShowSearch(true)}
          >
            Add Your First Company
          </Button>
        </Box>
      ) : (
        <>
          {/* Company Carousel */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Quick Overview
            </Typography>
            <CompanyCarousel
              companies={companyData}
              onViewDetails={handleViewDetails}
            />
          </Paper>

          {/* Tabs Navigation */}
          <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
            <Tabs
              value={activeTab}
              onChange={(_, newValue) => setActiveTab(newValue)}
              aria-label="tracked companies tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="Company Details" />
              <Tab label="Market Analysis" />
              <Tab label="Pipeline & Trials" />
              <Tab label="News & Updates" />
            </Tabs>
          </Box>

          {/* Tab Panels */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TrackedCompaniesList
                  tracked={tracked}
                  refreshTracked={fetchTrackedCompanies}
                  selectedCompany={selectedCompany}
                />
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <CompanyVisualizations companies={companyData} />
              </Grid>
              <Grid item xs={12}>
                <IPOInsights data={companyData} />
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <PipelineComparisonChart symbols={tracked} />
          </TabPanel>

          <TabPanel value={activeTab} index={3}>
            <CompanyNews trackedCompanies={tracked} />
          </TabPanel>
        </>
      )}
    </Box>
  );
}
