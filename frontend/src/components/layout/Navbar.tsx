"use client";

import React, { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import {
  AppBar,
  Toolbar,
  Typography,
  InputBase,
  Box,
  Tabs,
  Tab,
  IconButton,
} from "@mui/material";
import { styled, alpha } from "@mui/material/styles";
import SearchIcon from "@mui/icons-material/Search";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import BarChartIcon from "@mui/icons-material/BarChart";
import CompareArrowsIcon from "@mui/icons-material/CompareArrows";
import DescriptionIcon from "@mui/icons-material/Description";

const Search = styled("div")(({ theme }) => ({
  position: "relative",
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  "&:hover": { backgroundColor: alpha(theme.palette.common.white, 0.25) },
  marginLeft: theme.spacing(3),
  width: "auto",
}));

const SearchIconWrapper = styled("div")(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: "100%",
  position: "absolute",
  pointerEvents: "none",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: "inherit",
  "& .MuiInputBase-input": {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create("width"),
    width: "20ch",
  },
}));

const StyledTab = styled(Tab)(({ theme }) => ({
  "&:hover": {
    color: theme.palette.primary.main,
    opacity: 1,
    backgroundColor: alpha(theme.palette.primary.main, 0.1),
  },
  transition: "all 0.2s",
  borderRadius: "8px",
  margin: "0 4px",
  minHeight: "48px",
}));

const pathToIndex: { [key: string]: number } = {
  "/": 0,
  "/browse": 1,
  "/tracked": 2,
  "/compare": 3,
  "/report": 4,
  "/analytics": 5,
  "/about": 6,
};

const indexToPath: { [key: number]: string } = {
  0: "/",
  1: "/browse",
  2: "/tracked",
  3: "/compare",
  4: "/report",
  5: "/analytics",
  6: "/about",
};

export function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = useState("");

  const currentValue = pathToIndex[pathname] || 0;

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    router.push(indexToPath[newValue]);
  };

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    router.push(`/browse?query=${searchQuery}`);
  };

  return (
    <AppBar position="static" color="default" elevation={1}>
      <Toolbar>
        <ShowChartIcon sx={{ mr: 1, color: "primary.main" }} />
        <Typography
          variant="h6"
          noWrap
          sx={{
            mr: 2,
            fontFamily: "monospace",
            fontWeight: 700,
            letterSpacing: ".2rem",
            color: "primary.main",
            textDecoration: "none",
            cursor: "pointer",
          }}
          onClick={() => router.push("/")}
        >
          STOCKSIGHT
        </Typography>

        <Box sx={{ flexGrow: 1 }}>
          <Tabs
            value={currentValue}
            onChange={handleChange}
            sx={{ "& .MuiTabs-indicator": { height: 3, borderRadius: "3px" } }}
          >
            <StyledTab icon={<ShowChartIcon />} label="Dashboard" />
            <StyledTab icon={<BarChartIcon />} label="Browse" />
            <StyledTab icon={<BarChartIcon />} label="Tracked" />
            <StyledTab icon={<CompareArrowsIcon />} label="Compare" />
            <StyledTab icon={<DescriptionIcon />} label="Reports" />
            <StyledTab icon={<BarChartIcon />} label="Analytics" />
          </Tabs>
        </Box>

        <form onSubmit={handleSearch}>
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder="Search companies..."
              inputProps={{ "aria-label": "search" }}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Search>
        </form>
      </Toolbar>
    </AppBar>
  );
}
