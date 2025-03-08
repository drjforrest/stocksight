"use client";

import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
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
} from "@mui/material";
import { Bar } from "react-chartjs-2";
import {
  Delete as DeleteIcon,
  RestartAlt as ResetIcon,
} from "@mui/icons-material";
import { Company } from "./types";

interface CompareCompaniesProps {
  selectedCompanies: Company[];
  resetComparison: () => void;
  removeCompany: (symbol: string) => void;
}

export default function CompareCompanies({
  selectedCompanies,
  resetComparison,
  removeCompany,
}: CompareCompaniesProps) {
  if (selectedCompanies.length === 0) {
    return (
      <Card className="p-6 text-center">
        <Typography variant="h6">
          No Companies Selected for Comparison
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Use the "Compare" button in Browse to add companies here.
        </Typography>
      </Card>
    );
  }

  // Chart Data
  const chartData = {
    labels: selectedCompanies.map((c) => c.name),
    datasets: [
      {
        label: "Market Cap (Billion $)",
        data: selectedCompanies.map((c) => c.market_cap),
        backgroundColor: "rgba(53, 162, 235, 0.6)",
      },
      {
        label: "Active Clinical Trials",
        data: selectedCompanies.map((c) => c.active_trials),
        backgroundColor: "rgba(255, 99, 132, 0.6)",
      },
    ],
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
              <TableCell>FDA Submissions</TableCell>
              <TableCell>Active Trials</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {selectedCompanies.map((company) => (
              <TableRow key={company.symbol}>
                <TableCell>
                  {company.name} ({company.symbol})
                </TableCell>
                <TableCell>${company.market_cap.toFixed(2)}B</TableCell>
                <TableCell>{company.fda_submissions}</TableCell>
                <TableCell>{company.active_trials}</TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => removeCompany(company.symbol)}
                    color="error"
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
        <Typography variant="h6" sx={{ mb: 2 }}>
          Market Cap & Clinical Trials Overview
        </Typography>
        <Bar data={chartData} />
      </Card>
    </Box>
  );
}
