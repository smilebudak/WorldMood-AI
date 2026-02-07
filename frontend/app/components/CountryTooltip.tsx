"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { CountryMood } from "../lib/api";
import { getMoodMeta } from "../lib/moodColors";

interface CountryTooltipProps {
  country: CountryMood | null;
  position: { x: number; y: number } | null;
}

export default function CountryTooltip({ country, position }: CountryTooltipProps) {
  if (!country || !position) return null;

  const meta = getMoodMeta(country.mood_label);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 8, scale: 0.92 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 8, scale: 0.92 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="pointer-events-none fixed z-50"
        style={{
          left: Math.min(position.x + 16, window.innerWidth - 280),
          top: position.y - 8,
        }}
      >
        {/* Tooltip container with glow */}
        <div
          className="relative rounded-2xl bg-surface/90 backdrop-blur-xl border border-white/10 
                     px-4 py-3 shadow-2xl min-w-[240px] overflow-hidden"
          style={{
            boxShadow: `0 0 60px -10px ${country.color_code}40`,
          }}
        >
          {/* Subtle gradient accent at top */}
          <div
            className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl"
            style={{ background: `linear-gradient(90deg, ${country.color_code}, ${country.color_code}80, transparent)` }}
          />

          {/* Country header */}
          <div className="flex items-center gap-3 mb-3">
            {/* Country flag indicator */}
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-2xl
                         shadow-lg"
              style={{
                background: `linear-gradient(135deg, ${country.color_code}30, ${country.color_code}10)`,
                border: `1px solid ${country.color_code}40`
              }}
            >
              {meta.emoji}
            </div>
            <div className="flex-1">
              <h3 className="text-base font-bold text-white tracking-tight">
                {country.country_name}
              </h3>
              <div className="flex items-center gap-1.5">
                <span
                  className="inline-block w-2 h-2 rounded-full animate-pulse"
                  style={{ backgroundColor: country.color_code }}
                />
                <span
                  className="text-sm font-semibold"
                  style={{ color: country.color_code }}
                >
                  {country.mood_label}
                </span>
              </div>
            </div>
            {/* Mood score badge */}
            <div
              className="px-2 py-1 rounded-lg text-sm font-bold"
              style={{
                backgroundColor: `${country.color_code}20`,
                color: country.color_code
              }}
            >
              {country.mood_score > 0 ? "+" : ""}{country.mood_score.toFixed(1)}
            </div>
          </div>

          {/* Audio features */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            {country.valence !== null && (
              <div className="flex items-center justify-between px-2 py-1.5 rounded-lg bg-white/5">
                <span className="text-gray-400">Valence</span>
                <span className="text-white font-medium">{country.valence.toFixed(2)}</span>
              </div>
            )}
            {country.energy !== null && (
              <div className="flex items-center justify-between px-2 py-1.5 rounded-lg bg-white/5">
                <span className="text-gray-400">Energy</span>
                <span className="text-white font-medium">{country.energy.toFixed(2)}</span>
              </div>
            )}
          </div>

          {/* Top genre */}
          {country.top_genre && (
            <div className="mt-2 flex items-center gap-2 text-xs">
              <span className="text-gray-500">🎵</span>
              <span className="text-gray-300 capitalize">{country.top_genre}</span>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
