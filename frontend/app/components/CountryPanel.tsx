"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { X, TrendingUp, AlertTriangle, Music } from "lucide-react";
import { fetchCountryDetail, type CountryDetailResponse } from "../lib/api";
import { getMoodMeta } from "../lib/moodColors";

interface CountryPanelProps {
  countryCode: string | null;
  onClose: () => void;
}

export default function CountryPanel({ countryCode, onClose }: CountryPanelProps) {
  const [data, setData] = useState<CountryDetailResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!countryCode) {
      setData(null);
      return;
    }
    setLoading(true);
    fetchCountryDetail(countryCode)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [countryCode]);

  const meta = data ? getMoodMeta(data.mood_label) : null;

  return (
    <AnimatePresence>
      {countryCode && (
        <motion.aside
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 400, opacity: 0 }}
          transition={{ type: "spring", damping: 26, stiffness: 240 }}
          className="fixed right-0 top-0 h-full w-[380px] bg-surface/95 backdrop-blur-xl
                     border-l border-border z-40 overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-5 border-b border-border">
            <h2 className="text-lg font-semibold text-white">
              {data?.country_name || countryCode}
            </h2>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-white/5 transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          {loading && (
            <div className="flex items-center justify-center h-40 text-gray-500">
              Loading...
            </div>
          )}

          {data && meta && (
            <div className="p-5 space-y-6">
              {/* Mood badge */}
              <div className="flex items-center gap-3">
                <span className="text-3xl">{meta.emoji}</span>
                <div>
                  <div
                    className="text-xl font-bold"
                    style={{ color: meta.color }}
                  >
                    {data.mood_label}
                  </div>
                  <div className="text-sm text-gray-400">
                    Score: {data.mood_score > 0 ? "+" : ""}
                    {data.mood_score.toFixed(3)}
                  </div>
                </div>
                {data.spike_active && (
                  <div className="ml-auto spike-pulse rounded-full px-3 py-1 bg-red-500/10 border border-red-500/30">
                    <span className="text-xs text-red-400 font-medium flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" /> Spike
                    </span>
                  </div>
                )}
              </div>

              {/* Audio features */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Valence", value: data.valence },
                  { label: "Energy", value: data.energy },
                  { label: "Danceability", value: data.danceability },
                  { label: "Acousticness", value: data.acousticness },
                ].map(
                  (f) =>
                    f.value !== null && (
                      <div
                        key={f.label}
                        className="rounded-lg bg-background/60 border border-border p-3"
                      >
                        <div className="text-xs text-gray-500 mb-1">{f.label}</div>
                        <div className="text-lg font-semibold text-white">
                          {f.value!.toFixed(2)}
                        </div>
                        <div className="mt-1.5 h-1.5 rounded-full bg-border overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-500"
                            style={{
                              width: `${f.value! * 100}%`,
                              backgroundColor: meta.color,
                            }}
                          />
                        </div>
                      </div>
                    )
                )}
              </div>

              {/* Top track / genre */}
              {(data.top_track || data.top_genre) && (
                <div className="rounded-lg bg-background/60 border border-border p-3 flex items-center gap-3">
                  <Music className="w-4 h-4 text-gray-500 shrink-0" />
                  <div className="min-w-0">
                    {data.top_track && (
                      <div className="text-sm text-white truncate">{data.top_track}</div>
                    )}
                    {data.top_genre && (
                      <div className="text-xs text-gray-500">{data.top_genre}</div>
                    )}
                  </div>
                </div>
              )}

              {/* 7-day trend chart */}
              {data.trend.length > 1 && (
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-4 h-4 text-gray-500" />
                    <span className="text-sm font-medium text-gray-300">
                      7-Day Mood Trend
                    </span>
                  </div>
                  <div className="h-40 -ml-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={data.trend}>
                        <XAxis
                          dataKey="date"
                          tick={{ fontSize: 10, fill: "#555" }}
                          tickFormatter={(v: string) =>
                            new Date(v).toLocaleDateString("en", {
                              month: "short",
                              day: "numeric",
                            })
                          }
                          axisLine={false}
                          tickLine={false}
                        />
                        <YAxis
                          domain={[-1, 1]}
                          tick={{ fontSize: 10, fill: "#555" }}
                          axisLine={false}
                          tickLine={false}
                          width={30}
                        />
                        <Tooltip
                          contentStyle={{
                            background: "#14141f",
                            border: "1px solid #1e1e2e",
                            borderRadius: 8,
                            fontSize: 12,
                          }}
                          labelFormatter={(v: string) =>
                            new Date(v).toLocaleDateString()
                          }
                        />
                        <Line
                          type="monotone"
                          dataKey="mood_score"
                          stroke={meta.color}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4, fill: meta.color }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          )}
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
