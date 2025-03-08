"use client";

import React from "react";
import {
  Box,
  Card,
  Grid,
  Typography,
  Tooltip,
  IconButton,
  CircularProgress,
  Fade,
  Zoom,
  Button,
  Menu,
  MenuItem,
  Chip,
} from "@mui/material";
import {
  InfoOutlined,
  TrendingUp,
  TrendingDown,
  FilterList,
  GetApp,
  Clear,
  Analytics,
} from "@mui/icons-material";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip as RechartsTooltip,
  Legend,
  Cell,
  ReferenceArea,
  ReferenceLine,
} from "recharts";

interface FilterState {
  correlation: [number, number];
  priceImpact: [number, number];
  significance: boolean | null;
}

interface SelectedArea {
  x1: number;
  y1: number;
  x2?: number;
  y2?: number;
}

// Enhanced tooltip component for scatter plot with statistical details
const CustomScatterTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const zScore = Math.abs(data.correlation) / (1 / Math.sqrt(data.sample_size || 30));
    const isSignificant = zScore > 1.96; // 95% confidence level

    return (
      <Card sx={{ p: 2, boxShadow: 2, maxWidth: 300 }}>
        <Typography variant="subtitle2" gutterBottom>
          {data.competitor}
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Correlation: <strong>{data.correlation.toFixed(3)}</strong>
            <Chip
              size="small"
              label={isSignificant ? "Significant" : "Not Significant"}
              color={isSignificant ? "success" : "default"}
              sx={{ ml: 1 }}
            />
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Price Impact:{" "}
            <strong style={{ 
              color: data.price_change >= 0 ? "#4caf50" : "#f44336"
            }}>
              {(data.price_change * 100).toFixed(1)}%
            </strong>
          </Typography>
          {data.pre_ipo_avg && data.post_ipo_avg && (
            <>
              <Typography variant="body2" color="text.secondary">
                Pre-IPO Avg: ${data.pre_ipo_avg.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Post-IPO Avg: ${data.post_ipo_avg.toFixed(2)}
              </Typography>
            </>
          )}
          <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="caption" display="block">
              Z-Score: {zScore.toFixed(2)}
            </Typography>
            <Typography variant="caption" display="block">
              Sample Size: {data.sample_size || 'N/A'}
            </Typography>
          </Box>
        </Box>
      </Card>
    );
  }
  return null;
};

// Enhanced tooltip component for bar chart with additional metrics
const CustomBarTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const range = `$${(Number(label)/1e9).toFixed(1)}B - $${(Number(data.bin_edges_high)/1e9).toFixed(1)}B`;
    const percentage = (data.bins / data.total_companies * 100).toFixed(1);
    
    return (
      <Card sx={{ p: 2, boxShadow: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Valuation Range: {range}
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Companies: <strong>{payload[0].value}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Percentage: <strong>{percentage}%</strong>
          </Typography>
          {data.avg_market_cap && (
            <Typography variant="body2" color="text.secondary">
              Avg Market Cap: <strong>${(data.avg_market_cap/1e9).toFixed(2)}B</strong>
            </Typography>
          )}
        </Box>
      </Card>
    );
  }
  return null;
};

interface AdvancedAnalyticsProps {
  symbols: string[];
  timeframe: string;
}

export default function AdvancedAnalytics({ symbols, timeframe }: AdvancedAnalyticsProps) {
  const [correlationData, setCorrelationData] = React.useState<any>(null);
  const [pricingTrends, setPricingTrends] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  const [activeIndex, setActiveIndex] = React.useState(-1);
  const [filters, setFilters] = React.useState<FilterState>({
    correlation: [-1, 1],
    priceImpact: [-1, 1],
    significance: null,
  });
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [selectedArea, setSelectedArea] = React.useState<SelectedArea | null>(null);

  // Function to export data
  const handleExport = (type: 'correlation' | 'valuation') => {
    const data = type === 'correlation' ? correlationData : pricingTrends;
    const fileName = `${type}_analysis_${new Date().toISOString().split('T')[0]}.json`;
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Filter handling
  const handleFilterChange = (type: keyof FilterState, value: any) => {
    setFilters(prev => ({ ...prev, [type]: value }));
  };

  const clearFilters = () => {
    setFilters({
      correlation: [-1, 1],
      priceImpact: [-1, 1],
      significance: null,
    });
    setSelectedArea(null);
  };

  // Area selection for scatter plot
  const handleMouseDown = (e: any) => {
    if (e && e.xValue && e.yValue) {
      setSelectedArea({ x1: e.xValue, y1: e.yValue });
    }
  };

  const handleMouseMove = (e: any) => {
    if (selectedArea && e && e.xValue && e.yValue) {
      setSelectedArea((prev: SelectedArea | null) => prev ? { ...prev, x2: e.xValue, y2: e.yValue } : null);
    }
  };

  const handleMouseUp = () => {
    if (selectedArea?.x2) {
      const [x1, x2] = [selectedArea.x1, selectedArea.x2].sort((a: number, b: number) => a - b);
      const [y1, y2] = [selectedArea.y1, selectedArea.y2!].sort((a: number, b: number) => a - b);
      handleFilterChange('correlation', [x1, x2]);
      handleFilterChange('priceImpact', [y1, y2]);
    }
    setSelectedArea(null);
  };

  React.useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        // Fetch correlation data
        const correlationResponse = await fetch(`/api/market/impact/${symbols[0]}`);
        const correlationJson = await correlationResponse.json();
        setCorrelationData(correlationJson);

        // Fetch pricing trends
        const trendsResponse = await fetch('/api/market/pricing-trends');
        const trendsJson = await trendsResponse.json();
        setPricingTrends(trendsJson);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    if (symbols.length > 0) {
      fetchAnalytics();
    }
  }, [symbols, timeframe]);

  const handleMouseEnter = (data: any, index: number) => {
    setActiveIndex(index);
  };

  const handleMouseLeave = () => {
    setActiveIndex(-1);
  };

  // Filter the data based on current filters
  const filteredCompetitorData = React.useMemo(() => {
    if (!correlationData?.competitor_impacts) return [];
    return correlationData.competitor_impacts.filter((d: any) => {
      const correlationMatch = d.correlation >= filters.correlation[0] && d.correlation <= filters.correlation[1];
      const impactMatch = d.price_change >= filters.priceImpact[0] && d.price_change <= filters.priceImpact[1];
      const significanceMatch = filters.significance === null || 
        (filters.significance === (Math.abs(d.correlation) / Math.sqrt(1/30) > 1.96));
      return correlationMatch && impactMatch && significanceMatch;
    });
  }, [correlationData, filters]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Fade in={!loading} timeout={1000}>
      <Grid container spacing={3}>
        {/* Market Impact Analysis */}
        <Grid item xs={12} md={6}>
          <Zoom in={!loading} style={{ transitionDelay: '300ms' }}>
            <Card sx={{ 
              p: 3,
              transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              }
            }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center">
                  <Typography variant="h6">Market Impact Analysis</Typography>
                  <Tooltip title="Shows how this company's IPO affected competitor stock prices">
                    <IconButton size="small">
                      <InfoOutlined />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Box>
                  <Tooltip title="Export Data">
                    <IconButton onClick={() => handleExport('correlation')} size="small">
                      <GetApp />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Filter Data">
                    <IconButton 
                      onClick={(e) => setAnchorEl(e.currentTarget)}
                      size="small"
                      color={Object.values(filters).some(f => f !== null) ? "primary" : "default"}
                    >
                      <FilterList />
                    </IconButton>
                  </Tooltip>
                  {Object.values(filters).some(f => f !== null) && (
                    <Tooltip title="Clear Filters">
                      <IconButton onClick={clearFilters} size="small">
                        <Clear />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Box>
              {correlationData && (
                <>
                  <ResponsiveContainer width="100%" height={300}>
                    <ScatterChart
                      onMouseDown={handleMouseDown}
                      onMouseMove={handleMouseMove}
                      onMouseUp={handleMouseUp}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="correlation" 
                        type="number" 
                        name="Correlation"
                        domain={[-1, 1]}
                        tickFormatter={(value) => value.toFixed(1)}
                      />
                      <YAxis 
                        dataKey="price_change" 
                        type="number" 
                        name="Price Impact"
                        tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                      />
                      <RechartsTooltip content={<CustomScatterTooltip />} />
                      <Legend />
                      {selectedArea?.x2 && (
                        <ReferenceArea
                          x1={selectedArea.x1}
                          x2={selectedArea.x2}
                          y1={selectedArea.y1}
                          y2={selectedArea.y2}
                          strokeOpacity={0.3}
                          fill="blue"
                          fillOpacity={0.1}
                        />
                      )}
                      <ReferenceLine x={0} stroke="#666" strokeDasharray="3 3" />
                      <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
                      <Scatter
                        name="Competitors"
                        data={filteredCompetitorData}
                        fill="#8884d8"
                        onMouseEnter={handleMouseEnter}
                        onMouseLeave={handleMouseLeave}
                        animationBegin={300}
                        animationDuration={1000}
                        animationEasing="ease-out"
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                    Drag to select an area for filtering. Click clear filters to reset.
                  </Typography>
                </>
              )}
            </Card>
          </Zoom>
        </Grid>

        {/* Pricing Trends */}
        <Grid item xs={12} md={6}>
          <Zoom in={!loading} style={{ transitionDelay: '600ms' }}>
            <Card sx={{ 
              p: 3,
              transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              }
            }}>
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="h6">Valuation Trends</Typography>
                <Tooltip title="Historical valuation trends and distribution">
                  <IconButton size="small">
                    <InfoOutlined />
                  </IconButton>
                </Tooltip>
              </Box>
              {pricingTrends && (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart 
                    data={pricingTrends.visualization_data.valuation_distribution}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="bin_edges" 
                      tickFormatter={(value) => `$${(value/1e9).toFixed(1)}B`}
                    />
                    <YAxis />
                    <RechartsTooltip content={<CustomBarTooltip />} />
                    <Bar 
                      dataKey="bins" 
                      fill="#82ca9d"
                      name="Companies"
                      animationBegin={600}
                      animationDuration={1000}
                      animationEasing="ease-out"
                    >
                      {pricingTrends.visualization_data.valuation_distribution.map((entry: any, index: number) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={index === activeIndex ? '#4caf50' : '#82ca9d'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Card>
          </Zoom>
        </Grid>

        {/* Statistical Analysis */}
        <Grid item xs={12}>
          <Zoom in={!loading} style={{ transitionDelay: '900ms' }}>
            <Card sx={{ 
              p: 3,
              transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              }
            }}>
              <Box display="flex" alignItems="center" mb={2}>
                <Typography variant="h6">Statistical Insights</Typography>
                <Tooltip title="Key statistical metrics and significance tests">
                  <IconButton size="small">
                    <InfoOutlined />
                  </IconButton>
                </Tooltip>
              </Box>
              <Grid container spacing={3}>
                {correlationData?.statistical_analysis && (
                  <>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ 
                        p: 2, 
                        borderRadius: 1,
                        bgcolor: 'background.default',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'scale(1.02)' }
                      }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Average Correlation
                        </Typography>
                        <Typography variant="h6">
                          {correlationData.avg_correlation.toFixed(2)}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ 
                        p: 2, 
                        borderRadius: 1,
                        bgcolor: 'background.default',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'scale(1.02)' }
                      }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Statistical Significance
                        </Typography>
                        <Typography 
                          variant="h6" 
                          color={correlationData.statistical_analysis.significant ? "success.main" : "text.secondary"}
                          sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                        >
                          {correlationData.statistical_analysis.significant ? (
                            <>
                              <TrendingUp fontSize="small" />
                              Significant
                            </>
                          ) : (
                            <>
                              <TrendingDown fontSize="small" />
                              Not Significant
                            </>
                          )}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ 
                        p: 2, 
                        borderRadius: 1,
                        bgcolor: 'background.default',
                        transition: 'transform 0.2s',
                        '&:hover': { transform: 'scale(1.02)' }
                      }}>
                        <Typography variant="subtitle2" color="text.secondary">
                          P-Value
                        </Typography>
                        <Typography variant="h6">
                          {correlationData.statistical_analysis.p_value.toFixed(4)}
                        </Typography>
                      </Box>
                    </Grid>
                  </>
                )}
              </Grid>
            </Card>
          </Zoom>
        </Grid>
      </Grid>
    </Fade>
  );
}

// Add Menu component outside the main component
const FilterMenu = ({ anchorEl, onClose, filters, onFilterChange }: any) => (
  <Menu
    anchorEl={anchorEl}
    open={Boolean(anchorEl)}
    onClose={onClose}
    anchorOrigin={{
      vertical: 'bottom',
      horizontal: 'right',
    }}
    transformOrigin={{
      vertical: 'top',
      horizontal: 'right',
    }}
  >
    <MenuItem onClick={() => onFilterChange('significance', true)}>
      Show Significant Only
    </MenuItem>
    <MenuItem onClick={() => onFilterChange('significance', false)}>
      Show Non-Significant Only
    </MenuItem>
    <MenuItem onClick={() => onFilterChange('significance', null)}>
      Show All
    </MenuItem>
  </Menu>
); 