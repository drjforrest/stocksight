import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Switch,
  FormControlLabel,
  Pagination,
  Chip,
  Stack,
  Button,
  Skeleton,
  Alert,
  Snackbar,
  IconButton,
  Tooltip,
  Tab,
  Tabs,
  Fab
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  CompareArrows, 
  Favorite, 
  FavoriteBorder, 
  History, 
  BarChart as BarChartIcon,
  GridView,
  Help as HelpIcon
} from '@mui/icons-material';
import debounce from 'lodash/debounce';
import CompanyVisualizations from './CompanyVisualizations';
import BrowseHelp from './BrowseHelp';

export interface Company {
  symbol: string;
  name: string;
  market_cap: number;
  therapeutic_areas: string[];
  approved_drugs: string[];
  clinical_trials: {
    phase1: string[];
    phase2: string[];
    phase3: string[];
    phase4: string[];
  };
}

interface BrowseResponse {
  total: number;
  page: number;
  page_size: number;
  results: Company[];
}

export default function BrowseCompanies() {
  const queryClient = useQueryClient();
  
  // Filter state
  const [therapeuticArea, setTherapeuticArea] = useState<string>('');
  const [marketCapMin, setMarketCapMin] = useState<string>('');
  const [marketCapMax, setMarketCapMax] = useState<string>('');
  const [hasApprovedDrugs, setHasApprovedDrugs] = useState<boolean>(false);
  const [phase, setPhase] = useState<string>('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Additional state
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const [view, setView] = useState<'cards' | 'visualizations'>('cards');
  const [helpOpen, setHelpOpen] = useState(false);

  // Debounced market cap input handlers
  const debouncedSetMarketCapMin = debounce((value: string) => {
    setMarketCapMin(value);
  }, 500);

  const debouncedSetMarketCapMax = debounce((value: string) => {
    setMarketCapMax(value);
  }, 500);

  // Fetch therapeutic areas with error handling
  const { 
    data: therapeuticAreas = [],
    isError: isTherapeuticAreasError,
    error: therapeuticAreasError
  } = useQuery<string[]>({
    queryKey: ['therapeuticAreas'],
    queryFn: async () => {
      const response = await fetch('/api/browse/therapeutic-areas');
      if (!response.ok) {
        throw new Error('Failed to fetch therapeutic areas');
      }
      return response.json();
    }
  });

  // Fetch companies with error handling
  const { 
    data: browseData,
    isLoading,
    isError,
    error
  } = useQuery<BrowseResponse>({
    queryKey: ['browseCompanies', {
      therapeuticArea,
      marketCapMin,
      marketCapMax,
      hasApprovedDrugs,
      phase,
      page
    }],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (therapeuticArea) params.append('therapeutic_area', therapeuticArea);
      if (marketCapMin) params.append('market_cap_min', marketCapMin);
      if (marketCapMax) params.append('market_cap_max', marketCapMax);
      if (hasApprovedDrugs) params.append('has_approved_drugs', 'true');
      if (phase) params.append('phase', phase);
      params.append('page', page.toString());
      params.append('page_size', pageSize.toString());

      const response = await fetch(`/api/browse/companies?${params}`);
      if (!response.ok) {
        throw new Error('Failed to fetch companies');
      }
      return response.json();
    }
  });

  // Track company mutation
  const trackCompanyMutation = useMutation({
    mutationFn: async (symbol: string) => {
      const response = await fetch('/api/companies/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbol }),
      });
      if (!response.ok) {
        throw new Error('Failed to track company');
      }
      return response.json();
    },
    onSuccess: (data, symbol) => {
      setSnackbar({
        open: true,
        message: `Successfully tracked ${symbol}`,
        severity: 'success'
      });
      queryClient.invalidateQueries({ queryKey: ['trackedCompanies'] });
    },
    onError: (error, symbol) => {
      setSnackbar({
        open: true,
        message: `Failed to track ${symbol}: ${error.message}`,
        severity: 'error'
      });
    }
  });

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [therapeuticArea, marketCapMin, marketCapMax, hasApprovedDrugs, phase]);

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleTrackCompany = (symbol: string) => {
    trackCompanyMutation.mutate(symbol);
  };

  const handleCompareToggle = (symbol: string) => {
    setSelectedCompanies(prev => 
      prev.includes(symbol)
        ? prev.filter(s => s !== symbol)
        : prev.length < 3
          ? [...prev, symbol]
          : prev
    );
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const CompanyCard = ({ company }: { company: Company }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            {company.name} ({company.symbol})
          </Typography>
          <Stack direction="row" spacing={1}>
            <Tooltip title="Compare">
              <IconButton
                size="small"
                onClick={() => handleCompareToggle(company.symbol)}
                color={selectedCompanies.includes(company.symbol) ? 'primary' : 'default'}
              >
                <CompareArrows />
              </IconButton>
            </Tooltip>
            <Tooltip title="Track Company">
              <IconButton
                size="small"
                onClick={() => handleTrackCompany(company.symbol)}
                disabled={trackCompanyMutation.isPending}
              >
                {trackCompanyMutation.isPending ? <FavoriteBorder /> : <Favorite />}
              </IconButton>
            </Tooltip>
          </Stack>
        </Box>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Market Cap: ${company.market_cap.toFixed(2)}B
        </Typography>

        <Typography variant="subtitle2" gutterBottom>
          Therapeutic Areas:
        </Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          {company.therapeutic_areas.map((area) => (
            <Chip key={area} label={area} size="small" />
          ))}
        </Stack>

        {company.approved_drugs.length > 0 && (
          <>
            <Typography variant="subtitle2" gutterBottom>
              Approved Drugs:
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
              {company.approved_drugs.map((drug) => (
                <Chip
                  key={drug}
                  label={drug}
                  size="small"
                  color="success"
                />
              ))}
            </Stack>
          </>
        )}

        <Typography variant="subtitle2" gutterBottom>
          Clinical Trials:
        </Typography>
        <Grid container spacing={1}>
          {Object.entries(company.clinical_trials).map(([phase, drugs]) => (
            drugs.length > 0 && (
              <Grid item xs={6} key={phase}>
                <Typography variant="body2">
                  {phase.toUpperCase()}: {drugs.length}
                </Typography>
              </Grid>
            )
          ))}
        </Grid>
      </CardContent>
    </Card>
  );

  const LoadingSkeleton = () => (
    <Card>
      <CardContent>
        <Skeleton variant="text" width="60%" height={32} />
        <Skeleton variant="text" width="30%" />
        <Stack spacing={1}>
          <Skeleton variant="text" width="20%" />
          <Stack direction="row" spacing={1}>
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} variant="rectangular" width={80} height={24} />
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Browse Biotech Companies
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Tabs value={view} onChange={(_, newValue) => setView(newValue)}>
            <Tab 
              value="cards" 
              label="Cards" 
              icon={<GridView />} 
              iconPosition="start"
            />
            <Tab 
              value="visualizations" 
              label="Analytics" 
              icon={<BarChartIcon />} 
              iconPosition="start"
            />
          </Tabs>
          <Tooltip title="Help">
            <IconButton onClick={() => setHelpOpen(true)}>
              <HelpIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Therapeutic Area</InputLabel>
                <Select
                  value={therapeuticArea}
                  label="Therapeutic Area"
                  onChange={(e) => setTherapeuticArea(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  {therapeuticAreas.map((area) => (
                    <MenuItem key={area} value={area}>
                      {area}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                label="Min Market Cap (B)"
                type="number"
                value={marketCapMin}
                onChange={(e) => debouncedSetMarketCapMin(e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                label="Max Market Cap (B)"
                type="number"
                value={marketCapMax}
                onChange={(e) => debouncedSetMarketCapMax(e.target.value)}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Trial Phase</InputLabel>
                <Select
                  value={phase}
                  label="Trial Phase"
                  onChange={(e) => setPhase(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="1">Phase 1</MenuItem>
                  <MenuItem value="2">Phase 2</MenuItem>
                  <MenuItem value="3">Phase 3</MenuItem>
                  <MenuItem value="4">Phase 4</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={hasApprovedDrugs}
                    onChange={(e) => setHasApprovedDrugs(e.target.checked)}
                  />
                }
                label="Has Approved Drugs"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error States */}
      {isTherapeuticAreasError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load therapeutic areas: {therapeuticAreasError?.message}
        </Alert>
      )}

      {isError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load companies: {error?.message}
        </Alert>
      )}

      {/* Selected Companies for Comparison */}
      {selectedCompanies.length > 0 && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Selected for Comparison ({selectedCompanies.length}/3):
            </Typography>
            <Stack direction="row" spacing={1}>
              {selectedCompanies.map(symbol => (
                <Chip
                  key={symbol}
                  label={symbol}
                  onDelete={() => handleCompareToggle(symbol)}
                />
              ))}
            </Stack>
            {selectedCompanies.length > 1 && (
              <Button
                variant="contained"
                size="small"
                sx={{ mt: 1 }}
                onClick={() => {
                  // TODO: Implement comparison view
                }}
              >
                Compare Companies
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* View Content */}
      {view === 'cards' ? (
        <>
          {/* Results Grid */}
          <Grid container spacing={2}>
            {isLoading
              ? Array.from({ length: 6 }).map((_, i) => (
                  <Grid item xs={12} md={6} key={i}>
                    <LoadingSkeleton />
                  </Grid>
                ))
              : browseData?.results.map((company) => (
                  <Grid item xs={12} md={6} key={company.symbol}>
                    <CompanyCard company={company} />
                  </Grid>
                ))}
          </Grid>

          {/* Pagination */}
          {browseData && browseData.total > pageSize && (
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
              <Pagination
                count={Math.ceil(browseData.total / pageSize)}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </>
      ) : (
        // Visualizations View
        browseData?.results && <CompanyVisualizations companies={browseData.results} />
      )}

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Help Dialog */}
      <BrowseHelp
        open={helpOpen}
        onClose={() => setHelpOpen(false)}
      />
    </Box>
  );
} 