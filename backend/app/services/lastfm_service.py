"""
LastFmService – fetches top tracks per country from Last.fm and derives
mood-relevant features from track tags.

Replaces SpotifyService as the music data provider.
Last.fm API docs: https://www.last.fm/api
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import httpx
import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BASE_URL = "https://ws.audioscrobbler.com/2.0/"

# Countries supported by Last.fm geo endpoints (English names)
# Tested and verified with Last.fm API - only countries that return valid data
SUPPORTED_COUNTRIES: dict[str, str] = {
    # North America
    "US": "United States",
    "CA": "Canada",
    "MX": "Mexico",
    
    # South America
    "BR": "Brazil",
    "AR": "Argentina",
    "CL": "Chile",
    "CO": "Colombia",
    "PE": "Peru",
    "VE": "Venezuela",
    "EC": "Ecuador",
    
    # Western Europe
    "GB": "United Kingdom",
    "DE": "Germany",
    "FR": "France",
    "ES": "Spain",
    "IT": "Italy",
    "PT": "Portugal",
    "NL": "Netherlands",
    "BE": "Belgium",
    "AT": "Austria",
    "CH": "Switzerland",
    "IE": "Ireland",
    
    # Northern Europe
    "SE": "Sweden",
    "NO": "Norway",
    "FI": "Finland",
    "DK": "Denmark",
    "IS": "Iceland",
    "EE": "Estonia",
    "LV": "Latvia",
    "LT": "Lithuania",
    
    # Eastern Europe
    "PL": "Poland",
    "CZ": "Czech Republic",
    "SK": "Slovakia",
    "HU": "Hungary",
    "RO": "Romania",
    "BG": "Bulgaria",
    "UA": "Ukraine",
    "RS": "Serbia",
    "HR": "Croatia",
    "SI": "Slovenia",
    "GR": "Greece",
    
    # Russia & Turkey
    "RU": "Russia",
    "TR": "Turkey",
    
    # Middle East
    "IL": "Israel",
    "SA": "Saudi Arabia",
    "AE": "United Arab Emirates",
    
    # Africa
    "ZA": "South Africa",
    "NG": "Nigeria",
    "EG": "Egypt",
    "KE": "Kenya",
    "MA": "Morocco",
    
    # South Asia
    "IN": "India",
    "PK": "Pakistan",
    
    # East Asia
    "JP": "Japan",
    "CN": "China",
    "KR": "South Korea",
    "TW": "Taiwan",
    "HK": "Hong Kong",
    
    # Southeast Asia
    "TH": "Thailand",
    "VN": "Vietnam",
    "ID": "Indonesia",
    "MY": "Malaysia",
    "SG": "Singapore",
    "PH": "Philippines",
    
    # Oceania
    "AU": "Australia",
    "NZ": "New Zealand",
}

# ── Tag → mood dimension mapping ─────────────────────────────────────────────
# Each tag maps to (valence_shift, energy_shift, weight)

TAG_MOOD_MAP: dict[str, tuple[float, float, float]] = {
    # Happy / upbeat
    "happy": (0.9, 0.7, 1.0),
    "upbeat": (0.8, 0.8, 0.9),
    "fun": (0.8, 0.7, 0.8),
    "feel good": (0.85, 0.6, 0.9),
    "party": (0.7, 0.9, 0.8),
    "dance": (0.7, 0.85, 0.8),
    "summer": (0.75, 0.7, 0.6),
    "pop": (0.65, 0.65, 0.5),
    "disco": (0.7, 0.8, 0.7),
    "reggae": (0.7, 0.5, 0.6),
    "funk": (0.7, 0.75, 0.7),
    "soul": (0.6, 0.5, 0.6),
    "love": (0.7, 0.4, 0.6),
    "romantic": (0.65, 0.35, 0.6),

    # Calm / chill
    "chill": (0.55, 0.25, 0.9),
    "relax": (0.55, 0.2, 0.9),
    "ambient": (0.5, 0.15, 0.8),
    "acoustic": (0.5, 0.3, 0.7),
    "mellow": (0.5, 0.25, 0.8),
    "downtempo": (0.45, 0.3, 0.7),
    "lounge": (0.5, 0.25, 0.6),
    "jazz": (0.55, 0.35, 0.5),
    "classical": (0.5, 0.3, 0.5),
    "instrumental": (0.5, 0.3, 0.5),
    "folk": (0.5, 0.35, 0.5),
    "indie": (0.5, 0.45, 0.4),
    "singer-songwriter": (0.5, 0.3, 0.5),

    # Sad / melancholic
    "sad": (0.15, 0.2, 1.0),
    "melancholy": (0.15, 0.2, 0.9),
    "melancholic": (0.15, 0.2, 0.9),
    "emotional": (0.3, 0.3, 0.7),
    "heartbreak": (0.1, 0.25, 0.9),
    "lonely": (0.15, 0.2, 0.8),
    "depressing": (0.1, 0.15, 0.9),
    "emo": (0.2, 0.45, 0.7),
    "blues": (0.25, 0.35, 0.6),
    "slow": (0.3, 0.2, 0.5),
    "ballad": (0.3, 0.2, 0.6),

    # Angry / aggressive
    "angry": (0.1, 0.9, 1.0),
    "aggressive": (0.1, 0.9, 0.9),
    "metal": (0.15, 0.95, 0.8),
    "heavy metal": (0.1, 0.95, 0.8),
    "death metal": (0.05, 1.0, 0.9),
    "black metal": (0.05, 0.95, 0.8),
    "hardcore": (0.1, 0.95, 0.8),
    "punk": (0.25, 0.85, 0.7),
    "thrash": (0.1, 0.95, 0.8),
    "grunge": (0.2, 0.7, 0.6),
    "hard rock": (0.25, 0.85, 0.6),
    "nu metal": (0.15, 0.85, 0.7),

    # Anxious / tense
    "dark": (0.2, 0.6, 0.8),
    "intense": (0.25, 0.8, 0.7),
    "electronic": (0.45, 0.7, 0.4),
    "industrial": (0.15, 0.8, 0.7),
    "experimental": (0.3, 0.6, 0.5),
    "noise": (0.1, 0.8, 0.7),
    "gothic": (0.2, 0.55, 0.6),
    "trip-hop": (0.35, 0.45, 0.5),
    "dubstep": (0.3, 0.8, 0.5),
    "techno": (0.4, 0.8, 0.4),
    "trance": (0.45, 0.75, 0.4),

    # Energetic (neutral-positive)
    "rock": (0.45, 0.75, 0.4),
    "alternative": (0.4, 0.6, 0.4),
    "hip-hop": (0.45, 0.7, 0.4),
    "rap": (0.4, 0.75, 0.4),
    "rnb": (0.55, 0.5, 0.4),
    "r&b": (0.55, 0.5, 0.4),
    "k-pop": (0.7, 0.75, 0.5),
    "j-pop": (0.65, 0.7, 0.5),
    "latin": (0.65, 0.7, 0.5),
}


class LastFmService:
    """Fetch top tracks per country and derive mood features from tags."""

    def __init__(self) -> None:
        self.api_key = settings.LASTFM_API_KEY

    async def _api_call(self, client: httpx.AsyncClient, params: dict) -> dict:
        """Make a Last.fm API call."""
        params = {
            **params,
            "api_key": self.api_key,
            "format": "json",
        }
        resp = await client.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    async def fetch_country_features(self, country_code: str, limit: int = 50) -> dict:
        """Fetch top tracks for a country, get their tags, and derive mood features.

        Returns dict with: valence, energy, danceability, acousticness,
        top_genre, top_track.
        """
        country_name = SUPPORTED_COUNTRIES.get(country_code, country_code)

        try:
            async with httpx.AsyncClient() as client:
                # 1. Get top tracks for this country
                data = await self._api_call(client, {
                    "method": "geo.getTopTracks",
                    "country": country_name,
                    "limit": limit,
                })

                tracks = data.get("tracks", {}).get("track", [])
                if not tracks:
                    logger.warning("No tracks for %s, using fallback", country_code)
                    return self._fallback(country_code)

                top_track_name = tracks[0].get("name", "Unknown")
                top_artist = tracks[0].get("artist", {}).get("name", "Unknown")

                # 2. Get tags for top tracks (sample first 15 for speed)
                sample = tracks[:15]
                tag_tasks = [
                    self._get_track_tags(client, t["artist"]["name"], t["name"])
                    for t in sample
                    if t.get("artist", {}).get("name") and t.get("name")
                ]
                all_tags = await asyncio.gather(*tag_tasks, return_exceptions=True)

                # 3. Flatten all tags
                flat_tags: list[tuple[str, int]] = []
                for result in all_tags:
                    if isinstance(result, list):
                        flat_tags.extend(result)

                # 4. Derive mood features from tags
                features = self._tags_to_features(flat_tags)
                features["top_track"] = f"{top_track_name} – {top_artist}"

                # 5. Determine top genre from tags
                features["top_genre"] = self._top_genre(flat_tags)

                return features

        except Exception:
            logger.exception("Last.fm fetch failed for %s", country_code)
            return self._fallback(country_code)

    async def _get_track_tags(
        self, client: httpx.AsyncClient, artist: str, track: str
    ) -> list[tuple[str, int]]:
        """Get tags for a single track. Returns list of (tag_name, count)."""
        try:
            data = await self._api_call(client, {
                "method": "track.getTopTags",
                "artist": artist,
                "track": track,
            })
            tags = data.get("toptags", {}).get("tag", [])
            return [
                (t["name"].lower().strip(), int(t.get("count", 0)))
                for t in tags[:10]
                if t.get("name")
            ]
        except Exception:
            return []

    @staticmethod
    def _tags_to_features(tags: list[tuple[str, int]]) -> dict:
        """Convert a list of (tag, count) into valence/energy/danceability/acousticness."""
        if not tags:
            return {
                "valence": 0.5,
                "energy": 0.5,
                "danceability": 0.5,
                "acousticness": 0.5,
            }

        valence_sum = 0.0
        energy_sum = 0.0
        weight_sum = 0.0

        dance_signals = 0.0
        acoustic_signals = 0.0
        signal_count = 0

        dance_tags = {"dance", "disco", "party", "electronic", "techno", "trance", "dubstep", "k-pop", "latin", "funk", "hip-hop", "rap"}
        acoustic_tags = {"acoustic", "folk", "singer-songwriter", "classical", "instrumental", "ambient", "jazz", "blues", "ballad"}

        for tag_name, count in tags:
            weight = max(count, 1)

            if tag_name in TAG_MOOD_MAP:
                v, e, tag_weight = TAG_MOOD_MAP[tag_name]
                effective_weight = weight * tag_weight
                valence_sum += v * effective_weight
                energy_sum += e * effective_weight
                weight_sum += effective_weight

            if tag_name in dance_tags:
                dance_signals += weight
            if tag_name in acoustic_tags:
                acoustic_signals += weight
            signal_count += weight

        if weight_sum > 0:
            valence = valence_sum / weight_sum
            energy = energy_sum / weight_sum
        else:
            valence = 0.5
            energy = 0.5

        if signal_count > 0:
            danceability = 0.3 + 0.5 * (dance_signals / signal_count)
            acousticness = 0.2 + 0.6 * (acoustic_signals / signal_count)
        else:
            danceability = 0.5
            acousticness = 0.5

        return {
            "valence": round(float(np.clip(valence, 0, 1)), 3),
            "energy": round(float(np.clip(energy, 0, 1)), 3),
            "danceability": round(float(np.clip(danceability, 0, 1)), 3),
            "acousticness": round(float(np.clip(acousticness, 0, 1)), 3),
        }

    @staticmethod
    def _top_genre(tags: list[tuple[str, int]]) -> str:
        """Pick the most common genre-like tag."""
        genre_tags = {
            "pop", "rock", "hip-hop", "rap", "electronic", "metal", "jazz",
            "classical", "folk", "indie", "r&b", "rnb", "country", "blues",
            "reggae", "punk", "soul", "funk", "latin", "k-pop", "j-pop",
            "ambient", "dance", "techno", "trance",
        }
        genre_counts: dict[str, int] = {}
        for tag_name, count in tags:
            if tag_name in genre_tags:
                genre_counts[tag_name] = genre_counts.get(tag_name, 0) + count

        if genre_counts:
            return max(genre_counts, key=genre_counts.get)
        return "pop"

    @staticmethod
    def _fallback(country_code: str) -> dict:
        """Deterministic synthetic data for when API fails."""
        import hashlib
        seed = int(hashlib.md5(country_code.encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        return {
            "valence": round(float(rng.uniform(0.2, 0.85)), 3),
            "energy": round(float(rng.uniform(0.25, 0.9)), 3),
            "danceability": round(float(rng.uniform(0.3, 0.8)), 3),
            "acousticness": round(float(rng.uniform(0.1, 0.7)), 3),
            "top_genre": "pop",
            "top_track": f"Top Hit ({country_code})",
        }

    async def fetch_all_markets(self) -> dict[str, dict]:
        """Fetch features for all supported countries concurrently."""
        # Rate-limit friendly: batch in groups of 5
        results: dict[str, dict] = {}
        codes = list(SUPPORTED_COUNTRIES.keys())

        for i in range(0, len(codes), 5):
            batch = codes[i:i + 5]
            tasks = {cc: self.fetch_country_features(cc) for cc in batch}
            batch_results = await asyncio.gather(*tasks.values())
            for cc, result in zip(tasks.keys(), batch_results):
                results[cc] = result
            if i + 5 < len(codes):
                await asyncio.sleep(0.5)  # respect rate limits

        return results
