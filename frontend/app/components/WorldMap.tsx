"use client";

import { useEffect, useRef, useCallback } from "react";
import mapboxgl from "mapbox-gl";
import type { CountryMood } from "../lib/api";
import { buildFillColorExpression, getMoodEmoji } from "../lib/moodColors";

interface WorldMapProps {
  countries: CountryMood[];
  onCountryClick: (countryCode: string) => void;
  onCountryHover: (country: CountryMood | null, point: { x: number; y: number } | null) => void;
}

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";
const COUNTRY_SOURCE = "country-boundaries";
const FILL_LAYER = "country-fills";
const LINE_LAYER = "country-borders";

export default function WorldMap({ countries, onCountryClick, onCountryHover }: WorldMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const hoveredRef = useRef<string | null>(null);

  const countryLookup = useCallback(() => {
    const map = new Map<string, CountryMood>();
    for (const c of countries) {
      map.set(c.country_code, c);
    }
    return map;
  }, [countries]);

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [20, 25],
      zoom: 1.5,
      projection: { name: "globe" } as any, // 3D Globe!
      attributionControl: false,
    });

    map.addControl(new mapboxgl.NavigationControl(), "bottom-right");

    map.on("load", () => {
      // Add starfield background
      map.setFog({
        color: "rgb(10, 10, 20)",
        "high-color": "rgb(20, 20, 40)",
        "horizon-blend": 0.1,
        "space-color": "rgb(5, 5, 15)",
        "star-intensity": 0.8,
      });

      // Use Mapbox's built-in country boundaries tileset
      map.addSource(COUNTRY_SOURCE, {
        type: "vector",
        url: "mapbox://mapbox.country-boundaries-v1",
      });

      map.addLayer({
        id: FILL_LAYER,
        type: "fill",
        source: COUNTRY_SOURCE,
        "source-layer": "country_boundaries",
        paint: {
          "fill-color": "#1e1e2e",
          "fill-opacity": [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            0.9,
            0.7,
          ],
        },
      });

      map.addLayer({
        id: LINE_LAYER,
        type: "line",
        source: COUNTRY_SOURCE,
        "source-layer": "country_boundaries",
        paint: {
          "line-color": "#2a2a3a",
          "line-width": 0.5,
        },
      });
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update fill colors when countries data changes
  useEffect(() => {
    const map = mapRef.current;

    if (!map || !countries.length) return;

    const setColors = () => {

      if (!map.getLayer(FILL_LAYER)) {
        // Layer not ready yet, retry after a short delay
        setTimeout(setColors, 100);
        return;
      }

      const expr = buildFillColorExpression(
        countries.map((c) => ({
          country_code: c.country_code,
          color_code: c.color_code,
        }))
      );


      map.setPaintProperty(FILL_LAYER, "fill-color", expr as any);
    };

    if (map.isStyleLoaded()) {

      setColors();
    } else {

      map.once("load", setColors);
    }
  }, [countries]);

  // Hover + click handlers
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const lookup = countryLookup();

    const onMouseMove = (e: mapboxgl.MapMouseEvent) => {
      const features = map.queryRenderedFeatures(e.point, { layers: [FILL_LAYER] });

      if (features.length > 0) {
        const cc = features[0].properties?.iso_3166_1 as string;
        map.getCanvas().style.cursor = "pointer";

        if (cc !== hoveredRef.current) {
          hoveredRef.current = cc;
          const country = lookup.get(cc) || null;
          onCountryHover(country, { x: e.point.x, y: e.point.y });
        }
      } else {
        map.getCanvas().style.cursor = "";
        if (hoveredRef.current) {
          hoveredRef.current = null;
          onCountryHover(null, null);
        }
      }
    };

    const onMouseLeave = () => {
      map.getCanvas().style.cursor = "";
      hoveredRef.current = null;
      onCountryHover(null, null);
    };

    const onClick = (e: mapboxgl.MapMouseEvent) => {
      const features = map.queryRenderedFeatures(e.point, { layers: [FILL_LAYER] });
      if (features.length > 0) {
        const cc = features[0].properties?.iso_3166_1 as string;
        if (cc) onCountryClick(cc);
      }
    };

    map.on("mousemove", FILL_LAYER, onMouseMove);
    map.on("mouseleave", FILL_LAYER, onMouseLeave);
    map.on("click", FILL_LAYER, onClick);

    return () => {
      map.off("mousemove", FILL_LAYER, onMouseMove);
      map.off("mouseleave", FILL_LAYER, onMouseLeave);
      map.off("click", FILL_LAYER, onClick);
    };
  }, [countries, onCountryClick, onCountryHover, countryLookup]);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full"
    />
  );
}
