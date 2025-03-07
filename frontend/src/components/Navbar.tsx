'use client';

import React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { AppBar, Toolbar, Typography, InputBase, Box, Tabs, Tab, useTheme } from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import ShowChartIcon from '@mui/icons-material/ShowChart';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '20ch',
    },
  },
}));

const StyledTab = styled(Tab)(({ theme }) => ({
  '&:hover': {
    color: theme.palette.primary.main,
    opacity: 1,
    backgroundColor: alpha(theme.palette.primary.main, 0.1),
  },
  transition: 'all 0.2s',
  borderRadius: '8px',
  margin: '0 4px',
  minHeight: '48px',
}));

// Map paths to tab indices
const pathToIndex: { [key: string]: number } = {
  '/': 0,
  '/browse': 1,
  '/tracked': 2,
  '/analytics': 3,
};

// Map indices to paths
const indexToPath: { [key: number]: string } = {
  0: '/',
  1: '/browse',
  2: '/tracked',
  3: '/analytics',
};

export function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const theme = useTheme();
  
  // Get current tab value from pathname
  const currentValue = pathToIndex[pathname] || 0;

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    router.push(indexToPath[newValue]);
  };

  return (
    <AppBar position="static" color="default" elevation={1}>
      <Toolbar>
        <ShowChartIcon sx={{ display: { xs: 'none', md: 'flex' }, mr: 1, color: 'primary.main' }} />
        <Typography
          variant="h6"
          noWrap
          sx={{
            mr: 2,
            display: { xs: 'none', md: 'flex' },
            fontFamily: 'monospace',
            fontWeight: 700,
            letterSpacing: '.2rem',
            color: 'primary.main',
            textDecoration: 'none',
            cursor: 'pointer',
          }}
          onClick={() => router.push('/')}
        >
          STOCKSIGHT
        </Typography>

        <Box sx={{ flexGrow: 1 }}>
          <Tabs 
            value={currentValue} 
            onChange={handleChange}
            sx={{
              '& .MuiTabs-indicator': {
                height: 3,
                borderRadius: '3px',
              },
            }}
          >
            <StyledTab label="Dashboard" />
            <StyledTab label="Browse" />
            <StyledTab label="Tracked" />
            <StyledTab label="Analytics" />
          </Tabs>
        </Box>

        <Search>
          <SearchIconWrapper>
            <SearchIcon />
          </SearchIconWrapper>
          <StyledInputBase
            placeholder="Search companies..."
            inputProps={{ 'aria-label': 'search' }}
          />
        </Search>
      </Toolbar>
    </AppBar>
  );
}