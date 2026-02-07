"use client";

import { motion } from "framer-motion";
import { MOOD_MAP, type MoodLabel } from "../lib/moodColors";

const LABELS: MoodLabel[] = ["Happy", "Calm", "Anxious", "Sad", "Angry"];

export default function MoodLegend() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4, duration: 0.4 }}
      className="fixed bottom-2 sm:bottom-6 left-2 sm:left-6 z-30 flex flex-wrap items-center gap-2 sm:gap-4
                 rounded-xl bg-surface/90 backdrop-blur-lg border border-border
                 px-3 sm:px-5 py-2 sm:py-3 shadow-lg max-w-[calc(100vw-1rem)] sm:max-w-none"
    >
      <span className="text-[10px] sm:text-xs font-medium text-gray-400">Mood</span>
      {LABELS.map((label) => {
        const meta = MOOD_MAP[label];
        return (
          <div key={label} className="flex items-center gap-1 sm:gap-1.5">
            <span
              className="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full"
              style={{ backgroundColor: meta.color }}
            />
            <span className="text-[10px] sm:text-xs text-gray-300">{label}</span>
          </div>
        );
      })}
    </motion.div>
  );
}

