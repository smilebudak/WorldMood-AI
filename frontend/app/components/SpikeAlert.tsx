"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import { fetchSpikes, type Spike } from "../lib/api";
import { getMoodMeta } from "../lib/moodColors";

export default function SpikeAlert() {
  const [spikes, setSpikes] = useState<Spike[]>([]);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchSpikes()
      .then((res) => setSpikes(res.spikes.slice(0, 5)))
      .catch(() => {});
  }, []);

  if (spikes.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.6, duration: 0.4 }}
      className="fixed top-6 left-6 z-30 w-72"
    >
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-2 rounded-xl bg-red-500/10 backdrop-blur-lg
                   border border-red-500/20 px-4 py-2.5 text-left transition-colors
                   hover:bg-red-500/15"
      >
        <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
        <span className="text-sm font-medium text-red-300 flex-1">
          {spikes.length} Mood Spike{spikes.length > 1 ? "s" : ""} Detected
        </span>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-red-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-red-400" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="mt-2 rounded-xl bg-surface/95 backdrop-blur-xl border border-border divide-y divide-border">
              {spikes.map((s) => {
                const newMeta = getMoodMeta(s.new_label);
                return (
                  <div key={s.id} className="px-4 py-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-white">
                        {s.country_code}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(s.detected_at).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400">
                      {s.previous_label} →{" "}
                      <span style={{ color: newMeta.color }} className="font-medium">
                        {s.new_label} {newMeta.emoji}
                      </span>
                      <span className="text-gray-600 ml-2">
                        Δ{s.delta > 0 ? "+" : ""}
                        {s.delta.toFixed(3)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
