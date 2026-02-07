"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BarChart3, Zap, TrendingUp, ChevronUp, ChevronDown } from "lucide-react";
import type { CountryMood } from "../lib/api";
import { getMoodMeta } from "../lib/moodColors";

interface GlobalStatsProps {
    countries: CountryMood[];
}

// Calculate mood distribution and stats from countries data
function useGlobalStats(countries: CountryMood[]) {
    return useMemo(() => {
        if (!countries.length) return null;

        // Count countries by mood
        const moodCounts = new Map<string, number>();
        let totalValence = 0;
        let totalEnergy = 0;
        let valenceCount = 0;
        let energyCount = 0;

        countries.forEach((c) => {
            // Mood distribution
            const count = moodCounts.get(c.mood_label) || 0;
            moodCounts.set(c.mood_label, count + 1);

            // Average valence/energy
            if (c.valence !== null) {
                totalValence += c.valence;
                valenceCount++;
            }
            if (c.energy !== null) {
                totalEnergy += c.energy;
                energyCount++;
            }
        });

        // Sort moods by count (descending)
        const distribution = Array.from(moodCounts.entries())
            .map(([mood, count]) => ({
                mood,
                count,
                percentage: Math.round((count / countries.length) * 100),
                meta: getMoodMeta(mood),
            }))
            .sort((a, b) => b.count - a.count);

        // Get dominant mood
        const dominantMood = distribution[0];

        return {
            totalCountries: countries.length,
            distribution,
            dominantMood,
            avgValence: valenceCount > 0 ? totalValence / valenceCount : 0,
            avgEnergy: energyCount > 0 ? totalEnergy / energyCount : 0,
        };
    }, [countries]);
}

export default function GlobalStats({ countries }: GlobalStatsProps) {
    const stats = useGlobalStats(countries);
    const [isExpanded, setIsExpanded] = useState(true);

    if (!stats) return null;

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.4 }}
            className="fixed bottom-20 sm:bottom-24 left-2 sm:left-6 z-20 pointer-events-auto"
        >
            <div className="bg-surface/90 backdrop-blur-xl rounded-2xl border border-border/50 
                      shadow-2xl overflow-hidden w-[240px] sm:min-w-[280px]">
                {/* Header - always visible, clickable on mobile */}
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="w-full px-3 sm:px-4 py-2 sm:py-3 border-b border-border/50 flex items-center gap-2 
                               hover:bg-white/5 transition-colors"
                >
                    <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-mood-happy to-mood-calm 
                          flex items-center justify-center">
                        <BarChart3 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
                    </div>
                    <div className="flex-1 text-left">
                        <h3 className="text-xs sm:text-sm font-semibold text-white">Global Stats</h3>
                        <p className="text-[10px] sm:text-xs text-gray-500">{stats.totalCountries} countries</p>
                    </div>
                    {/* Collapse toggle */}
                    <div className="sm:hidden text-gray-400">
                        {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                    </div>
                </button>

                {/* Stats content - collapsible on mobile */}
                <AnimatePresence>
                    {isExpanded && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="overflow-hidden"
                        >
                            <div className="p-3 sm:p-4 space-y-3 sm:space-y-4">
                                {/* Dominant Mood */}
                                <div className="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 rounded-xl"
                                    style={{ backgroundColor: `${stats.dominantMood.meta.color}15` }}>
                                    <span className="text-xl sm:text-2xl">{stats.dominantMood.meta.emoji}</span>
                                    <div className="flex-1 min-w-0">
                                        <div className="text-[10px] sm:text-xs text-gray-400">Dominant</div>
                                        <div className="text-sm sm:text-lg font-bold truncate" style={{ color: stats.dominantMood.meta.color }}>
                                            {stats.dominantMood.mood}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-lg sm:text-xl font-bold text-white">{stats.dominantMood.percentage}%</div>
                                    </div>
                                </div>

                                {/* Mood Distribution */}
                                <div className="space-y-1.5 sm:space-y-2">
                                    <div className="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Distribution</div>
                                    {stats.distribution.map((item, i) => (
                                        <motion.div
                                            key={item.mood}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.4 + i * 0.05 }}
                                            className="flex items-center gap-1.5 sm:gap-2"
                                        >
                                            <span className="text-xs sm:text-sm">{item.meta.emoji}</span>
                                            <div className="flex-1">
                                                <div className="h-1.5 sm:h-2 rounded-full bg-border overflow-hidden">
                                                    <motion.div
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${item.percentage}%` }}
                                                        transition={{ delay: 0.5 + i * 0.05, duration: 0.5 }}
                                                        className="h-full rounded-full"
                                                        style={{ backgroundColor: item.meta.color }}
                                                    />
                                                </div>
                                            </div>
                                            <span className="text-[10px] sm:text-xs text-gray-400 w-8 sm:w-10 text-right">{item.percentage}%</span>
                                        </motion.div>
                                    ))}
                                </div>

                                {/* Average Metrics */}
                                <div className="grid grid-cols-2 gap-1.5 sm:gap-2 pt-1 sm:pt-2">
                                    <div className="p-2 sm:p-2.5 rounded-lg bg-white/5 border border-white/5">
                                        <div className="flex items-center gap-1 sm:gap-1.5 mb-0.5 sm:mb-1">
                                            <TrendingUp className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-mood-happy" />
                                            <span className="text-[10px] sm:text-xs text-gray-400">Valence</span>
                                        </div>
                                        <div className="text-base sm:text-lg font-semibold text-white">{stats.avgValence.toFixed(2)}</div>
                                    </div>
                                    <div className="p-2 sm:p-2.5 rounded-lg bg-white/5 border border-white/5">
                                        <div className="flex items-center gap-1 sm:gap-1.5 mb-0.5 sm:mb-1">
                                            <Zap className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-mood-anxious" />
                                            <span className="text-[10px] sm:text-xs text-gray-400">Energy</span>
                                        </div>
                                        <div className="text-base sm:text-lg font-semibold text-white">{stats.avgEnergy.toFixed(2)}</div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
}

