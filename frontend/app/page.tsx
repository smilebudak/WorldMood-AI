"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import WorldMap from "./components/WorldMap";
import CountryTooltip from "./components/CountryTooltip";
import CountryPanel from "./components/CountryPanel";
import MoodLegend from "./components/MoodLegend";
import SpikeAlert from "./components/SpikeAlert";
import GlobalStats from "./components/GlobalStats";
import { fetchGlobalMood, type CountryMood } from "./lib/api";

export default function Home() {
  const [countries, setCountries] = useState<CountryMood[]>([]);
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Tooltip state
  const [hoveredCountry, setHoveredCountry] = useState<CountryMood | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number } | null>(null);

  // Side panel
  const [selectedCode, setSelectedCode] = useState<string | null>(null);

  useEffect(() => {
    fetchGlobalMood()
      .then((res) => {
        setCountries(res.countries);
        setUpdatedAt(res.updated_at);
      })
      .catch((error) => {
        // Failed to fetch mood data, using fallback/empty state
      })
      .finally(() => setLoading(false));
  }, []);

  const handleHover = useCallback(
    (country: CountryMood | null, point: { x: number; y: number } | null) => {
      setHoveredCountry(country);
      setTooltipPos(point);
    },
    []
  );

  const handleClick = useCallback((code: string) => {
    setSelectedCode(code);
  }, []);

  const handleClosePanel = useCallback(() => {
    setSelectedCode(null);
  }, []);

  return (
    <main className="relative w-screen h-screen overflow-hidden bg-background">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-30 flex items-center justify-between
                   px-3 py-2 sm:px-6 sm:py-4 pointer-events-none"
      >
        <div className="pointer-events-auto flex items-start gap-2 sm:gap-3">
          {/* Animated Globe Icon */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="relative w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-mood-happy via-mood-calm to-mood-sad
                       flex items-center justify-center shadow-lg shadow-mood-calm/20"
          >
            <span className="text-base sm:text-lg">🌍</span>
            {/* Orbit ring */}
            <div className="absolute inset-0 rounded-full border border-white/20 animate-pulse" />
          </motion.div>

          <div>
            <h1 className="text-lg sm:text-2xl font-bold tracking-tight bg-gradient-to-r from-white via-mood-calm to-mood-happy
                           bg-clip-text text-transparent drop-shadow-lg">
              WorldMood-AI
            </h1>
            <p className="hidden sm:block text-xs text-gray-400 tracking-wide">Global Mood Map</p>
          </div>
        </div>

        {/* Right side - Live badge and timestamp */}
        <div className="pointer-events-auto flex items-center gap-3">
          {/* Live indicator - moved to top right */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full
                       bg-surface/80 backdrop-blur-md border border-border shadow-lg"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-mood-happy opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-mood-happy"></span>
            </span>
            <span className="text-xs font-medium text-mood-happy">LIVE</span>
          </motion.div>

          {/* Updated timestamp */}
          {updatedAt && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-xs text-gray-500 bg-surface/60 backdrop-blur-sm
                         px-3 py-1.5 rounded-full border border-border/50"
            >
              Updated {new Date(updatedAt).toLocaleTimeString()}
            </motion.div>
          )}
        </div>
      </motion.header>

      {/* Loading state */}
      {loading && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-background">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <div className="w-8 h-8 border-2 border-mood-calm border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm text-gray-500">Loading global mood data...</p>
          </motion.div>
        </div>
      )}

      {/* Map */}
      <WorldMap
        countries={countries}
        onCountryClick={handleClick}
        onCountryHover={handleHover}
      />

      {/* Tooltip */}
      <CountryTooltip country={hoveredCountry} position={tooltipPos} />

      {/* Side panel */}
      <CountryPanel countryCode={selectedCode} onClose={handleClosePanel} />

      {/* Legend */}
      <MoodLegend />

      {/* Global Stats */}
      {!loading && countries.length > 0 && <GlobalStats countries={countries} />}

      {/* Spike alerts */}
      <SpikeAlert />
    </main>
  );
}
