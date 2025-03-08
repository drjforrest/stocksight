"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Button,
  Checkbox,
  FormControlLabel,
  Box,
  Typography,
} from "@mui/material";
import { FaSearch, FaBell, FaChartLine, FaBalanceScale } from "react-icons/fa";

export default function WelcomeModal() {
  const [open, setOpen] = useState(false);
  const [dontShowAgain, setDontShowAgain] = useState(false);

  useEffect(() => {
    const hasDismissed = localStorage.getItem("hideWelcomeModal");
    if (!hasDismissed) {
      setOpen(true);
    }
  }, []);

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem("hideWelcomeModal", "true");
    }
    setOpen(false);
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Welcome to StockSight! 👋</DialogTitle>
      <DialogContent>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Your personal biotech market intelligence platform.
        </Typography>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 2,
            mb: 3,
          }}
        >
          <FeatureCard
            icon={<FaSearch className="text-blue-600 text-xl" />}
            title="Browse & Compare Companies"
            description="Explore biotech companies by therapeutic area, market cap, and clinical phase."
            link="/browse"
          />
          <FeatureCard
            icon={<FaBell className="text-green-600 text-xl" />}
            title="Track Companies"
            description="Add companies to your watchlist to monitor news, updates, and market movements."
            link="/tracked"
          />
          <FeatureCard
            icon={<FaChartLine className="text-purple-600 text-xl" />}
            title="Analyze Trends"
            description="Get insights into market trends, competitor analysis, and industry movements."
            link="/analytics"
          />
          <FeatureCard
            icon={<FaBalanceScale className="text-orange-600 text-xl" />}
            title="Compare & Report"
            description="Compare companies side-by-side and generate a shareable report."
            link="/compare"
          />
        </Box>

        <FormControlLabel
          control={
            <Checkbox
              checked={dontShowAgain}
              onChange={(e) => setDontShowAgain(e.target.checked)}
            />
          }
          label="Don't show this again"
        />

        <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 2 }}>
          <Button variant="contained" color="primary" onClick={handleClose}>
            Get Started
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  link,
}: {
  icon: JSX.Element;
  title: string;
  description: string;
  link: string;
}) {
  return (
    <Box
      sx={{
        textAlign: "center",
        p: 2,
        borderRadius: 2,
        border: "1px solid #ddd",
        bgcolor: "background.paper",
      }}
    >
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          mb: 1,
        }}
      >
        {icon}
      </Box>
      <Typography variant="subtitle1" fontWeight="bold">
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {description}
      </Typography>
      <Link href={link}>
        <Button size="small" variant="contained" sx={{ mt: 1 }}>
          Explore
        </Button>
      </Link>
    </Box>
  );
}
