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
  Divider,
  IconButton,
  Box,
  Button,
} from "@mui/material";
import {
  Close,
  BarChart,
  PieChart,
  BubbleChart,
  FilterList,
  CompareArrows,
  Favorite,
  GridView,
  RssFeed,
  OpenInNew,
  FileDownload,
  LocalPharmacy,
  Science,
} from "@mui/icons-material";

interface BrowseHelpProps {
  open: boolean;
  onClose: () => void;
}

export default function BrowseHelp({ open, onClose }: BrowseHelpProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          Browse & Analytics Features
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        {/* --- Views Section --- */}
        <Typography variant="h6" gutterBottom>
          Views
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <GridView />
            </ListItemIcon>
            <ListItemText
              primary="Card View"
              secondary="Browse biotech companies in a card format with key insights."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <BarChart />
            </ListItemIcon>
            <ListItemText
              primary="Analytics View"
              secondary="Visualize biotech market trends and patterns."
            />
          </ListItem>
        </List>
        <Divider sx={{ my: 2 }} />

        {/* --- Filtering & Search Section --- */}
        <Typography variant="h6" gutterBottom>
          Filtering & Search
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <FilterList />
            </ListItemIcon>
            <ListItemText
              primary="Advanced Filters"
              secondary="Filter by market cap, therapeutic area, clinical trial phase, and FDA status."
            />
          </ListItem>
        </List>
        <Divider sx={{ my: 2 }} />

        {/* --- FDA Integration Section --- */}
        <Typography variant="h6" gutterBottom>
          FDA Integration
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <LocalPharmacy />
            </ListItemIcon>
            <ListItemText
              primary="FDA Approvals & Submissions"
              secondary="Track how many drugs a company has submitted or had approved."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Science />
            </ListItemIcon>
            <ListItemText
              primary="Active Clinical Trials"
              secondary="See how many ongoing trials the company is involved in."
            />
          </ListItem>
        </List>
        <Divider sx={{ my: 2 }} />

        {/* --- Analytics Features Section --- */}
        <Typography variant="h6" gutterBottom>
          Analytics Features
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <BarChart />
            </ListItemIcon>
            <ListItemText
              primary="Market Cap Distribution"
              secondary="See how biotech companies distribute across market cap ranges."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <PieChart />
            </ListItemIcon>
            <ListItemText
              primary="Therapeutic Areas"
              secondary="Understand the market share of different biotech fields."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <BubbleChart />
            </ListItemIcon>
            <ListItemText
              primary="Market Cap vs Development"
              secondary="Compare company size vs clinical development activity."
            />
          </ListItem>
        </List>
        <Divider sx={{ my: 2 }} />

        {/* --- Company Management Section --- */}
        <Typography variant="h6" gutterBottom>
          Company Management
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <CompareArrows />
            </ListItemIcon>
            <ListItemText
              primary="Compare Companies"
              secondary="Select up to 3 companies to compare side-by-side."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Favorite />
            </ListItemIcon>
            <ListItemText
              primary="Track Companies"
              secondary="Save companies for real-time updates & alerts."
            />
          </ListItem>
        </List>
        <Divider sx={{ my: 2 }} />

        {/* --- Report Builder Section --- */}
        <Typography variant="h6" gutterBottom>
          Report Builder
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <FileDownload />
            </ListItemIcon>
            <ListItemText
              primary="Generate Custom Reports"
              secondary="Export insights into PDFs or share via email."
            />
          </ListItem>
        </List>
        <Divider sx={{ my: 2 }} />

        {/* --- RSS Feed Section --- */}
        <Typography variant="h6" gutterBottom>
          RSS Feed Integration
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <RssFeed />
            </ListItemIcon>
            <ListItemText
              primary="Personalized RSS Feed"
              secondary="Get biotech updates for your tracked companies in an RSS reader."
            />
          </ListItem>
        </List>
        <Divider sx={{ my: 2 }} />

        {/* --- Pro Tips Section --- */}
        <Typography variant="body2" color="text.secondary">
          <strong>Pro Tips:</strong>
          <List dense>
            <ListItem>
              • Use market cap filters to compare companies of similar size.
            </ListItem>
            <ListItem>
              • Analytics view updates dynamically as you refine your search.
            </ListItem>
            <ListItem>
              • Hover over chart elements for detailed insights.
            </ListItem>
          </List>
        </Typography>

        {/* --- Close Button --- */}
        <Box display="flex" justifyContent="flex-end" mt={2}>
          <Button onClick={onClose} variant="contained" color="primary">
            Got it!
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
