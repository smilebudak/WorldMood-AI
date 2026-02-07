"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { CountryMood } from "../lib/api";
import { getMoodMeta } from "../lib/moodColors";

interface CountryTooltipProps {
  country: CountryMood | null;
  position: { x: number; y: number } | null;
}

export default function CountryTooltip({ country, position }: CountryTooltipProps) {
  return (
    <AnimatePresence>
      {country && position && (
        <motion.div
          initial={{ opacity: 0, y: 4, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 4, scale: 0.96 }}
          transition={{ duration: 0.15, ease: "easeOut" }}
          className="pointer-events-none fixed z-50"
          style={{
            left: position.x + 16,
            top: position.y - 8,
          }}
        >
          <div className="rounded-xl bg-surface border border-border px-4 py-3 shadow-2xl min-w-[200px]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-white">
                {country.country_name}
              </span>
              <span className="text-lg">{getMoodMeta(country.mood_label).emoji}</span>
            </div>

            <div className="flex items-center gap-2 mb-2">
              <span
                className="inline-block w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: country.color_code }}
              />
              <span
                className="text-sm font-medium"
                style={{ color: country.color_code }}
              >
                {country.mood_label}
              </span>
              <span className="text-xs text-gray-500 ml-auto">
                {country.mood_score > 0 ? "+" : ""}
                {country.mood_score.toFixed(2)}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-400">
              {country.valence !== null && (
                <div>
                  Valence{" "}
                  <span className="text-gray-200">{country.valence.toFixed(2)}</span>
                </div>
              )}
              {country.energy !== null && (
                <div>
                  Energy{" "}
                  <span className="text-gray-200">{country.energy.toFixed(2)}</span>
                </div>
              )}
              {country.top_genre && (
                <div className="col-span-2 mt-1 truncate">
                  Genre{" "}
                  <span className="text-gray-200">{country.top_genre}</span>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
