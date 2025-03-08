"use client";

import React from "react";
import { Box, Card, Grid, Skeleton, Stack } from "@mui/material";

export function CompanyCardSkeleton() {
  return (
    <Card className="p-4">
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Box>
          <Skeleton variant="text" width={200} height={32} />
          <Skeleton variant="text" width={100} height={24} />
        </Box>
        <Stack direction="row" spacing={1}>
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="circular" width={32} height={32} />
        </Stack>
      </Box>

      <Stack spacing={2}>
        <Box>
          <Skeleton variant="text" width={80} height={20} />
          <Skeleton variant="text" width={120} height={32} />
        </Box>

        <Box>
          <Skeleton variant="text" width={80} height={20} />
          <Stack direction="row" spacing={1} alignItems="baseline">
            <Skeleton variant="text" width={100} height={32} />
            <Skeleton variant="text" width={60} height={24} />
          </Stack>
        </Box>

        <Box>
          <Skeleton variant="text" width={120} height={20} />
          <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 1 }}>
            <Skeleton variant="rounded" width={80} height={24} />
            <Skeleton variant="rounded" width={100} height={24} />
            <Skeleton variant="rounded" width={90} height={24} />
          </Stack>
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Skeleton variant="text" width={100} height={20} />
            <Skeleton variant="text" width={40} height={24} />
          </Grid>
          <Grid item xs={6}>
            <Skeleton variant="text" width={100} height={20} />
            <Skeleton variant="text" width={40} height={24} />
          </Grid>
        </Grid>
      </Stack>
    </Card>
  );
}

export function CompanyTableSkeleton() {
  return (
    <Stack spacing={1}>
      <Skeleton variant="rectangular" height={56} />
      {[...Array(3)].map((_, i) => (
        <Skeleton key={i} variant="rectangular" height={72} />
      ))}
    </Stack>
  );
}

export function ChartSkeleton() {
  return (
    <Card sx={{ mt: 4, p: 3 }}>
      <Skeleton variant="text" width={300} height={32} sx={{ mb: 2 }} />
      <Skeleton variant="rectangular" height={300} />
    </Card>
  );
} 