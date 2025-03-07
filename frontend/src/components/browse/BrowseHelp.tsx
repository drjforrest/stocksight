import React from 'react';
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
} from '@mui/material';
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
} from '@mui/icons-material';

interface BrowseHelpProps {
  open: boolean;
  onClose: () => void;
}

export default function BrowseHelp({ open, onClose }: BrowseHelpProps) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          Browse & Analytics Features
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
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
              secondary="Browse companies in a card layout showing key information including market cap, therapeutic areas, approved drugs, and clinical trials."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <BarChart />
            </ListItemIcon>
            <ListItemText
              primary="Analytics View"
              secondary="Visualize market trends and patterns across companies using interactive charts and graphs."
            />
          </ListItem>
        </List>

        <Divider sx={{ my: 2 }} />

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
              secondary="Filter companies by therapeutic area, market cap range, clinical trial phase, and presence of approved drugs."
            />
          </ListItem>
        </List>

        <Divider sx={{ my: 2 }} />

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
              secondary="Bar chart showing the distribution of companies across different market cap ranges (0-1B, 1-5B, 5-10B, 10-50B, 50B+)."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <BarChart />
            </ListItemIcon>
            <ListItemText
              primary="Clinical Trial Pipeline"
              secondary="Overview of clinical trials across all phases (1-4) for the filtered set of companies."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <PieChart />
            </ListItemIcon>
            <ListItemText
              primary="Therapeutic Areas"
              secondary="Pie chart showing the distribution of top therapeutic areas among the filtered companies."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <BubbleChart />
            </ListItemIcon>
            <ListItemText
              primary="Market Cap vs Development"
              secondary="Scatter plot comparing company market caps to their clinical development activity. Bubble size indicates number of approved drugs."
            />
          </ListItem>
        </List>

        <Divider sx={{ my: 2 }} />

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
              secondary="Select up to 3 companies to compare their key metrics and development pipelines side by side."
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Favorite />
            </ListItemIcon>
            <ListItemText
              primary="Track Companies"
              secondary="Add companies to your tracking list for monitoring news, updates, and developments."
            />
          </ListItem>
        </List>

        <Divider sx={{ my: 2 }} />

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
              secondary={
                <React.Fragment>
                  <Typography component="span" variant="body2" color="text.primary">
                    Get updates for your tracked companies in any RSS reader:
                  </Typography>
                  <List dense>
                    <ListItem>
                      • Each user gets a unique, secure RSS feed URL
                    </ListItem>
                    <ListItem>
                      • Feed includes news, sentiment analysis, and company mentions
                    </ListItem>
                    <ListItem>
                      • Updates hourly with fresh content
                    </ListItem>
                    <ListItem>
                      • Works with any standard RSS reader (Feedly, NewsBlur, etc.)
                    </ListItem>
                  </List>
                </React.Fragment>
              }
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <OpenInNew />
            </ListItemIcon>
            <ListItemText
              primary="How to Use Your RSS Feed"
              secondary={
                <React.Fragment>
                  <Typography component="span" variant="body2">
                    1. Go to your profile settings to get your unique RSS feed URL
                  </Typography>
                  <Typography component="span" variant="body2" display="block">
                    2. Copy the URL and add it to your preferred RSS reader
                  </Typography>
                  <Typography component="span" variant="body2" display="block">
                    3. Your reader will automatically fetch updates about your tracked companies
                  </Typography>
                  <Typography component="span" variant="body2" display="block" color="primary" sx={{ mt: 1 }}>
                    Pro Tip: Use RSS feed filters in your reader to focus on specific companies or news types
                  </Typography>
                </React.Fragment>
              }
            />
          </ListItem>
        </List>

        <Divider sx={{ my: 2 }} />

        <Typography variant="body2" color="text.secondary">
          Pro Tips:
          <List dense>
            <ListItem>
              • Use market cap filters to focus on companies of similar size
            </ListItem>
            <ListItem>
              • The analytics view automatically updates as you adjust filters
            </ListItem>
            <ListItem>
              • Hover over chart elements for detailed information
            </ListItem>
            <ListItem>
              • Compare companies in similar therapeutic areas to find potential competitors
            </ListItem>
          </List>
        </Typography>
      </DialogContent>
    </Dialog>
  );
} 