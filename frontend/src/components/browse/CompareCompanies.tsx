"use client";

import React from "react";
import {
  Box,
  Card,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Stack,
  Chip,
  Tabs,
  Tab,
} from "@mui/material";
import { Bar, Radar } from "react-chartjs-2";
import {
  Delete as DeleteIcon,
  RestartAlt as ResetIcon,
} from "@mui/icons-material";
import type { CompareCompaniesProps } from "@/types/company";
import { CompanyTableSkeleton, ChartSkeleton } from "./LoadingSkeleton";

export default function CompareCompanies({
  selectedCompanies,
  removeCompany,
  resetComparison,
}: CompareCompaniesProps) {
  const [chartType, setChartType] = React.useState<"bar" | "radar">("bar");

  if (selectedCompanies.length === 0) {
    return (
      <Card className="p-6 text-center">
        <Typography variant="h6">
          No Companies Selected for Comparison
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Use the Browse tab to add companies for comparison.
        </Typography>
      </Card>
    );
  }

  // Chart Data
  const barChartData = {
    labels: selectedCompanies.map((c) => c.name),
    datasets: [
      {
        label: "Market Cap (Billion $)",
        data: selectedCompanies.map((c) => c.market_cap / 1e9),
        backgroundColor: "rgba(53, 162, 235, 0.6)",
      },
      {
        label: "Active Clinical Trials",
        data: selectedCompanies.map((c) => c.active_trials || 0),
        backgroundColor: "rgba(255, 99, 132, 0.6)",
      },
    ],
  };

  // Radar Chart Data for relative comparison
  const radarChartData = {
    labels: [
      "Market Cap",
      "Price",
      "FDA Submissions",
      "Active Trials",
      "Therapeutic Areas",
    ],
    datasets: selectedCompanies.map((company, index) => ({
      label: company.name,
      data: [
        company.market_cap / 1e9, // Normalized market cap
        company.price,
        company.fda_submissions || 0,
        company.active_trials || 0,
        company.therapeutic_areas?.length || 0,
      ],
      backgroundColor: `rgba(${index * 100}, 99, 132, 0.2)`,
      borderColor: `rgba(${index * 100}, 99, 132, 1)`,
    })),
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        sx={{ mb: 3 }}
      >
        <Typography variant="h4">Compare Selected Companies</Typography>
        <Button
          variant="outlined"
          startIcon={<ResetIcon />}
          onClick={resetComparison}
        >
          Reset Comparison
        </Button>
      </Stack>

      {/* Comparison Table */}
      <TableContainer component={Card}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Company</TableCell>
              <TableCell>Market Cap</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>FDA Submissions</TableCell>
              <TableCell>Active Trials</TableCell>
              <TableCell>Therapeutic Areas</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {selectedCompanies.map((company) => (
              <TableRow key={company.symbol}>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle1">{company.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {company.symbol}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>${(company.market_cap / 1e9).toFixed(2)}B</TableCell>
                <TableCell>
                  <Box>
                    <Typography>${company.price.toFixed(2)}</Typography>
                    <Typography
                      color={
                        company.change_percent >= 0
                          ? "success.main"
                          : "error.main"
                      }
                      variant="caption"
                    >
                      {company.change_percent >= 0 ? "+" : ""}
                      {company.change_percent.toFixed(2)}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{company.fda_submissions || 0}</TableCell>
                <TableCell>{company.active_trials || 0}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    {company.therapeutic_areas?.map((area) => (
                      <Chip
                        key={area}
                        label={area}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => removeCompany(company.symbol)}
                    color="error"
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Chart Visualization */}
      <Card sx={{ mt: 4, p: 3 }}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          sx={{ mb: 3 }}
        >
          <Typography variant="h6">Company Metrics Comparison</Typography>
          <Tabs
            value={chartType}
            onChange={(_, newValue) => setChartType(newValue)}
            sx={{ minHeight: 0 }}
          >
            <Tab
              label="Bar Chart"
              value="bar"
              sx={{ minHeight: 0, textTransform: "none" }}
            />
            <Tab
              label="Radar Chart"
              value="radar"
              sx={{ minHeight: 0, textTransform: "none" }}
            />
          </Tabs>
        </Stack>

        <Box sx={{ height: 400 }}>
          {chartType === "bar" ? (
            <Bar
              data={barChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          ) : (
            <Radar
              data={radarChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  r: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          )}
        </Box>
      </Card>
    </Box>
  );
}
