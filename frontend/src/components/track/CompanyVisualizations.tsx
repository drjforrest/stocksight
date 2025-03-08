"use client";

import React, { useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Sankey,
} from "recharts";
import { Box, Card, CardContent, Typography, Grid } from "@mui/material";

interface Company {
  symbol: string;
  market_cap: number;
  fda_approvals: number;
  fda_rejections: number;
  fda_warnings: number;
  clinical_trials: {
    phase1: string[];
    phase2: string[];
    phase3: string[];
    phase4: string[];
  };
}

interface CompanyVisualizationsProps {
  companies: Company[];
}

export default function CompanyVisualizations({
  companies,
}: CompanyVisualizationsProps) {
  const marketCapData = useMemo(() => {
    const ranges = [
      { range: "0-1B", min: 0, max: 1 },
      { range: "1-5B", min: 1, max: 5 },
      { range: "5-10B", min: 5, max: 10 },
      { range: "10-50B", min: 10, max: 50 },
      { range: "50B+", min: 50, max: Infinity },
    ];
    return ranges.map(({ range, min, max }) => ({
      range,
      count: companies.filter((c) => c.market_cap >= min && c.market_cap < max)
        .length,
    }));
  }, [companies]);

  const fdaApprovalData = useMemo(
    () =>
      companies.map((company) => ({
        name: company.symbol,
        approved: company.fda_approvals || 0,
        rejected: company.fda_rejections || 0,
      })),
    [companies],
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Market Cap Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={marketCapData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">FDA Drug Approvals</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={fdaApprovalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="approved" fill="#00C49F" />
                <Bar dataKey="rejected" fill="#d62728" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}
