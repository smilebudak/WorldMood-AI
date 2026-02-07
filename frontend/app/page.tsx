"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import WorldMap from "./components/WorldMap";
import CountryTooltip from "./components/CountryTooltip";
import CountryPanel from "./components/CountryPanel";
import MoodLegend from "./components/MoodLegend";
import SpikeAlert from "./components/SpikeAlert";
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
      .catch(console.error)
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
                   px-6 py-4 pointer-events-none"
      >
        <div className="pointer-events-auto">
          <h1 className="text-xl font-bold text-white tracking-tight">
            MoodAtlas
          </h1>
          <p className="text-xs text-gray-500">Global Mood Map</p>
        </div>
        {updatedAt && (
          <div className="text-xs text-gray-600 pointer-events-auto">
            Updated {new Date(updatedAt).toLocaleTimeString()}
          </div>
        )}
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

      {/* Spike alerts */}
      <SpikeAlert />
    </main>
  );
}
