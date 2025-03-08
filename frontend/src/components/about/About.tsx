"use client";

import { Box, Typography, Container, Paper, Divider } from "@mui/material";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import BusinessIcon from "@mui/icons-material/Business";
import InsightsIcon from "@mui/icons-material/Insights";
import ScienceIcon from "@mui/icons-material/Science";

export default function AboutStockSight() {
  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
          <ShowChartIcon sx={{ fontSize: 40, color: "primary.main" }} />
          <Typography variant="h4" fontWeight="bold">
            About StockSight
          </Typography>
        </Box>

        <Typography variant="body1" color="text.secondary">
          StockSight is a **data-driven biotech investment intelligence
          platform** developed by drjforrest.com, that integrates **SEC, FDA,
          and Market** data to **track, analyze, visualize, and compare
          companies and their product pipelines. By integrating **real-time
          stock data (MarketStack API)**, **company fundamentals (SEC API)**,
          and **regulatory insights (FDA API)**, StockSight offers a
          **comprehensive analysis** tool of the contemporary biotech landscape.
        </Typography>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
          🔹 StockSight Features
        </Typography>

        <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
          <BusinessIcon color="primary" />
          <Typography variant="body1">
            **Company Fundamentals** – Track biotech companies with **market
            cap, trial phases, and approval data**.
          </Typography>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
          <InsightsIcon color="primary" />
          <Typography variant="body1">
            **Investment Insights** – Compare biotech firms and **generate
            professional reports** for analysis.
          </Typography>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <ScienceIcon color="primary" />
          <Typography variant="body1">
            **FDA Pipeline Data** – Monitor drug approvals, clinical trial
            results, and **regulatory decisions**.
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
          🔹 Why StockSight?
        </Typography>

        <Typography variant="body1" color="text.secondary">
          **StockSight is not just another finance tool**—it is developed by
          **biotech insiders who understand the key investment signals**.
          Existing tools are built by **general finance/tech professionals**
          without deep biotech expertise. They focus on **broad market
          indicators**, missing the **specific clinical, regulatory, and R&D
          insights** crucial for biotech investments. StockSight **integrates
          biotech-first intelligence**—aligning **FDA filings, clinical trial
          results, and market trends** in one unified platform.
        </Typography>

        <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
          🔹 Why Now?
        </Typography>

        <Typography variant="body1" color="text.secondary">
          - Biotech markets are **more competitive and volatile than ever** with
          an AI-revolution that is shaking up the landscape.. - Investors need
          **faster, smarter, and more biotech-specific analytics**. - StockSight
          provides an **unmatched edge** by focusing on **the right variables**
          that impact biotech success.
        </Typography>

        <Typography variant="h6" fontWeight="bold">
          🚀 Join us in building the next-gen biotech market intelligence tool.
        </Typography>
      </Paper>
    </Container>
  );
}
