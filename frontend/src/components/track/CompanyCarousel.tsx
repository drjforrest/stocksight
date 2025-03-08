"use client";

import React from "react";
import {
  Box,
  Card,
  IconButton,
  Typography,
  Stack,
  Chip,
  Button,
  useTheme,
} from "@mui/material";
import {
  ArrowForward,
  ArrowBack,
  TrendingUp,
  TrendingDown,
  Science,
  LocalPharmacy,
  OpenInNew,
} from "@mui/icons-material";
import { useKeenSlider } from "keen-slider/react";
import "keen-slider/keen-slider.min.css";
import { KeenSliderOptions } from "keen-slider/react";

interface CompanyCarouselProps {
  companies: any[];
  onViewDetails: (symbol: string) => void;
}

export default function CompanyCarousel({ companies, onViewDetails }: CompanyCarouselProps) {
  const theme = useTheme();
  const [currentSlide, setCurrentSlide] = React.useState(0);
  const [loaded, setLoaded] = React.useState(false);

  const [sliderRef, instanceRef] = useKeenSlider<HTMLDivElement>({
    initial: 0,
    slides: {
      perView: Math.min(3, companies.length),
      spacing: 16,
    },
    breakpoints: {
      "(max-width: 1200px)": {
        slides: { perView: Math.min(2, companies.length), spacing: 16 },
      },
      "(max-width: 800px)": {
        slides: { perView: 1, spacing: 16 },
      },
    },
    slideChanged(slider) {
      setCurrentSlide(slider.track.details.rel);
    },
    created() {
      setLoaded(true);
    },
  } as KeenSliderOptions);

  return (
    <Box sx={{ position: "relative", py: 2 }}>
      {/* Carousel Navigation */}
      {loaded && instanceRef.current && (
        <>
          <IconButton
            sx={{
              position: "absolute",
              left: -20,
              top: "50%",
              transform: "translateY(-50%)",
              zIndex: 2,
              bgcolor: "background.paper",
              boxShadow: 2,
              "&:hover": { bgcolor: "background.paper" },
            }}
            onClick={() => instanceRef.current?.prev()}
            disabled={currentSlide === 0}
          >
            <ArrowBack />
          </IconButton>

          <IconButton
            sx={{
              position: "absolute",
              right: -20,
              top: "50%",
              transform: "translateY(-50%)",
              zIndex: 2,
              bgcolor: "background.paper",
              boxShadow: 2,
              "&:hover": { bgcolor: "background.paper" },
            }}
            onClick={() => instanceRef.current?.next()}
            disabled={
              currentSlide ===
              (instanceRef.current.track.details.slides.length -
                (typeof instanceRef.current.options.slides === 'object' &&
                instanceRef.current.options.slides?.perView
                  ? Number(instanceRef.current.options.slides.perView)
                  : 1))
            }
          >
            <ArrowForward />
          </IconButton>
        </>
      )}

      {/* Carousel Content */}
      <div ref={sliderRef} className="keen-slider">
        {companies.map((company, idx) => (
          <Card
            key={company.symbol}
            className="keen-slider__slide"
            sx={{
              p: 3,
              height: "100%",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              transition: "transform 0.2s",
              "&:hover": {
                transform: "translateY(-4px)",
              },
            }}
          >
            {/* Company Header */}
            <Box>
              <Typography variant="h6" gutterBottom>
                {company.name}
              </Typography>
              <Typography variant="subtitle2" color="text.secondary">
                {company.symbol}
              </Typography>
            </Box>

            {/* Key Metrics */}
            <Stack spacing={2} sx={{ my: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Market Cap
                </Typography>
                <Typography variant="h6">
                  ${(company.market_cap / 1e9).toFixed(2)}B
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">
                  Stock Price
                </Typography>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="h6">
                    ${company.price.toFixed(2)}
                  </Typography>
                  <Typography
                    color={company.change_percent >= 0 ? "success.main" : "error.main"}
                    sx={{ display: "flex", alignItems: "center" }}
                  >
                    {company.change_percent >= 0 ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
                    {Math.abs(company.change_percent).toFixed(2)}%
                  </Typography>
                </Stack>
              </Box>

              <Stack direction="row" spacing={2}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Science fontSize="small" color="primary" />
                  <Typography>{company.active_trials || 0} Trials</Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <LocalPharmacy fontSize="small" color="primary" />
                  <Typography>{company.fda_submissions || 0} FDA</Typography>
                </Box>
              </Stack>
            </Stack>

            {/* Actions */}
            <Button
              variant="outlined"
              endIcon={<OpenInNew />}
              onClick={() => onViewDetails(company.symbol)}
              fullWidth
            >
              View Details
            </Button>
          </Card>
        ))}
      </div>
    </Box>
  );
} 