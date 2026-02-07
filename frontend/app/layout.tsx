import type { Metadata } from "next";
import "./styles/globals.css";

export const metadata: Metadata = {
  title: "MoodAtlas – Global Mood Map",
  description:
    "Visualize the emotional mood of countries on a world map, derived from music listening data.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.css"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background text-white antialiased">{children}</body>
    </html>
  );
}
