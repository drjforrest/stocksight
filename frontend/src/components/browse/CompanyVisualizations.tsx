import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Sankey,
  Scatter,
  ScatterChart,
  ZAxis
} from 'recharts';
import { Box, Card, CardContent, Typography, Grid } from '@mui/material';
import { Company } from './BrowseCompanies';

interface CompanyVisualizationsProps {
  companies: Company[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export default function CompanyVisualizations({ companies }: CompanyVisualizationsProps) {
  // Prepare market cap distribution data
  const marketCapData = useMemo(() => {
    const ranges = [
      { range: '0-1B', min: 0, max: 1 },
      { range: '1-5B', min: 1, max: 5 },
      { range: '5-10B', min: 5, max: 10 },
      { range: '10-50B', min: 10, max: 50 },
      { range: '50B+', min: 50, max: Infinity }
    ];

    return ranges.map(({ range, min, max }) => ({
      range,
      count: companies.filter(c => c.market_cap >= min && c.market_cap < max).length
    }));
  }, [companies]);

  // Prepare clinical trial data
  const trialData = useMemo(() => {
    const phases = ['phase1', 'phase2', 'phase3', 'phase4'] as const;
    return phases.map(phase => ({
      phase: phase.toUpperCase(),
      count: companies.reduce((acc, company) => 
        acc + company.clinical_trials[phase].length, 0
      )
    }));
  }, [companies]);

  // Prepare therapeutic area distribution
  const therapeuticAreaData = useMemo(() => {
    const areaCount = new Map<string, number>();
    companies.forEach(company => {
      company.therapeutic_areas.forEach(area => {
        areaCount.set(area, (areaCount.get(area) || 0) + 1);
      });
    });
    return Array.from(areaCount.entries())
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5); // Top 5 therapeutic areas
  }, [companies]);

  // Prepare market cap vs trials scatter data
  const scatterData = useMemo(() => 
    companies.map(company => ({
      name: company.symbol,
      marketCap: company.market_cap,
      totalTrials: Object.values(company.clinical_trials)
        .reduce((acc, trials) => acc + trials.length, 0),
      approvedDrugs: company.approved_drugs.length
    }))
  , [companies]);

  return (
    <Grid container spacing={3}>
      {/* Market Cap Distribution */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Market Cap Distribution
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={marketCapData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Clinical Trial Pipeline */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Clinical Trial Pipeline
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trialData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="phase" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#00C49F" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Top Therapeutic Areas */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Top Therapeutic Areas
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={therapeuticAreaData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ name, percent }) => 
                      `${name} (${(percent * 100).toFixed(0)}%)`
                    }
                  >
                    {therapeuticAreaData.map((entry, index) => (
                      <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Market Cap vs Clinical Trials */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Market Cap vs Clinical Development
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="marketCap" 
                    name="Market Cap" 
                    unit="B"
                    type="number"
                  />
                  <YAxis 
                    dataKey="totalTrials" 
                    name="Total Trials"
                    type="number"
                  />
                  <ZAxis 
                    dataKey="approvedDrugs" 
                    range={[50, 400]} 
                    name="Approved Drugs"
                  />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ payload }) => {
                      if (!payload?.[0]) return null;
                      const data = payload[0].payload;
                      return (
                        <Card sx={{ p: 1 }}>
                          <Typography variant="body2">{data.name}</Typography>
                          <Typography variant="body2">
                            Market Cap: ${data.marketCap.toFixed(2)}B
                          </Typography>
                          <Typography variant="body2">
                            Total Trials: {data.totalTrials}
                          </Typography>
                          <Typography variant="body2">
                            Approved Drugs: {data.approvedDrugs}
                          </Typography>
                        </Card>
                      );
                    }}
                  />
                  <Scatter 
                    data={scatterData} 
                    fill="#8884d8"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
} 