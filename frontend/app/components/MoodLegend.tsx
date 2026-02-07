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
      className="fixed bottom-6 left-6 z-30 flex items-center gap-4
                 rounded-xl bg-surface/90 backdrop-blur-lg border border-border
                 px-5 py-3 shadow-lg"
    >
      <span className="text-xs font-medium text-gray-400 mr-1">Mood</span>
      {LABELS.map((label) => {
        const meta = MOOD_MAP[label];
        return (
          <div key={label} className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: meta.color }}
            />
            <span className="text-xs text-gray-300">{label}</span>
          </div>
        );
      })}
    </motion.div>
  );
}
