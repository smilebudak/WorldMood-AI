export type MoodLabel = "Happy" | "Calm" | "Sad" | "Angry" | "Anxious";

export interface MoodMeta {
  color: string;
  emoji: string;
  bgClass: string;
  textClass: string;
}

export const MOOD_MAP: Record<MoodLabel, MoodMeta> = {
  Happy: {
    color: "#22c55e",
    emoji: "😊",
    bgClass: "bg-mood-happy",
    textClass: "text-mood-happy",
  },
  Calm: {
    color: "#38bdf8",
    emoji: "😌",
    bgClass: "bg-mood-calm",
    textClass: "text-mood-calm",
  },
  Sad: {
    color: "#8b5cf6",
    emoji: "😢",
    bgClass: "bg-mood-sad",
    textClass: "text-mood-sad",
  },
  Angry: {
    color: "#ef4444",
    emoji: "😠",
    bgClass: "bg-mood-angry",
    textClass: "text-mood-angry",
  },
  Anxious: {
    color: "#f97316",
    emoji: "😰",
    bgClass: "bg-mood-anxious",
    textClass: "text-mood-anxious",
  },
};

export function getMoodMeta(label: string): MoodMeta {
  return MOOD_MAP[label as MoodLabel] ?? MOOD_MAP.Calm;
}

export function getMoodColor(label: string): string {
  return getMoodMeta(label).color;
}

export function getMoodEmoji(label: string): string {
  return getMoodMeta(label).emoji;
}

/**
 * Build a Mapbox match expression for country fill colors.
 * Input: array of { country_code, color_code }
 */
export function buildFillColorExpression(
  countries: { country_code: string; color_code: string }[]
): any[] {
  const expr: any[] = ["match", ["get", "iso_3166_1"]];
  for (const c of countries) {
    expr.push(c.country_code, c.color_code);
  }
  // Default color for countries without data: Calm blue
  expr.push("#38bdf8");
  return expr;
}
