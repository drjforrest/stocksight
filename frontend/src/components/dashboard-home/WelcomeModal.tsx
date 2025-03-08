"use client";

import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Box,
  IconButton,
  useTheme,
} from "@mui/material";
import {
  Close as CloseIcon,
  TrendingUp,
  CompareArrows,
  Notifications,
  BarChart,
  Science,
  LocalPharmacy,
} from "@mui/icons-material";

interface WelcomeModalProps {
  open: boolean;
  onClose: () => void;
}

export default function WelcomeModal({ open, onClose }: WelcomeModalProps) {
  const theme = useTheme();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          p: 2,
        },
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" component="div" fontWeight="bold" color="primary">
            Welcome to StockSight
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Typography variant="body1" paragraph>
          Your intelligent platform for biotech market insights. Here's what you can do:
        </Typography>

        <List>
          <ListItem>
            <ListItemIcon>
              <TrendingUp color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Track Market Trends"
              secondary="Monitor real-time biotech market movements and key indicators"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <Science color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Clinical Trial Insights"
              secondary="Stay updated on clinical trial progress and outcomes"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <LocalPharmacy color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="FDA Pipeline Tracking"
              secondary="Monitor drug approvals and regulatory decisions"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <CompareArrows color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Company Comparison"
              secondary="Compare up to 3 companies side by side with detailed metrics"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <BarChart color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Advanced Analytics"
              secondary="Access AI-powered market analysis and predictions"
            />
          </ListItem>

          <ListItem>
            <ListItemIcon>
              <Notifications color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Real-time Alerts"
              secondary="Get notified about important events for your tracked companies"
            />
          </ListItem>
        </List>

        <Box sx={{ mt: 4, textAlign: "center" }}>
          <Typography variant="body2" color="text.secondary" paragraph>
            Pro Tip: Start by browsing companies and adding them to your tracking list!
          </Typography>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={onClose}
            sx={{ minWidth: 200 }}
          >
            Get Started
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
} 