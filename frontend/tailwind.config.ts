import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mood: {
          happy: "#22c55e",
          calm: "#38bdf8",
          sad: "#8b5cf6",
          angry: "#ef4444",
          anxious: "#f97316",
        },
        background: "#0a0a0f",
        surface: "#14141f",
        border: "#1e1e2e",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
