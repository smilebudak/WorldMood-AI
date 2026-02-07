"""
SpotifyService – fetches top-chart audio features per country.

Architecture note:  This module is the sole integration point with Spotify.
To swap in TIDAL, implement the same public interface (``fetch_country_features``)
in a ``tidal_service.py`` and update ``MUSIC_PROVIDER`` in config.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

TOKEN_URL = "https://accounts.spotify.com/api/token"
BROWSE_URL = "https://api.spotify.com/v1/browse/categories"
FEATURES_URL = "https://api.spotify.com/v1/audio-features"
TOP_TRACKS_URL = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

# ISO-3166-1 alpha-2 codes supported by Spotify charts
SUPPORTED_MARKETS = [
    "US", "GB", "DE", "FR", "JP", "BR", "IN", "AU", "CA", "MX",
    "KR", "SE", "NO", "FI", "ES", "IT", "NL", "PL", "TR", "ZA",
    "NG", "EG", "AR", "CL", "CO", "PH", "ID", "TH", "VN", "RU",
]


class SpotifyService:
    def __init__(self) -> None:
        self._token: Optional[str] = None

    async def _authenticate(self) -> str:
        """Client-credentials flow."""
        if self._token:
            return self._token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
            )
            resp.raise_for_status()
            self._token = resp.json()["access_token"]
            return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._authenticate()
        return {"Authorization": f"Bearer {token}"}

    async def fetch_country_features(
        self, country_code: str, limit: int = 30
    ) -> dict:
        """Return aggregated audio features for a market's top tracks.

        Returns dict with keys: valence, energy, danceability, acousticness,
        top_genre, top_track.
        """
        try:
            headers = await self._headers()
            # Fetch "Top 50" playlist for market via Spotify catalog
            # (In production you'd resolve the actual playlist ID per market)
            playlist_id = await self._resolve_top_playlist(country_code, headers)
            if not playlist_id:
                return self._fallback(country_code)

            track_ids, top_track_name = await self._get_track_ids(
                playlist_id, headers, limit
            )
            if not track_ids:
                return self._fallback(country_code)

            features = await self._get_audio_features(track_ids, headers)
            return self._aggregate(features, top_track_name)

        except Exception:
            logger.exception("Spotify fetch failed for %s", country_code)
            return self._fallback(country_code)

    async def _resolve_top_playlist(
        self, country_code: str, headers: dict
    ) -> Optional[str]:
        """Resolve the Top-50 playlist for a market.
        Placeholder – replace with real catalog lookup or hardcoded map."""
        # For hackathon: return None to trigger fallback with synthetic data
        return None

    async def _get_track_ids(
        self, playlist_id: str, headers: dict, limit: int
    ) -> tuple[list[str], str]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                TOP_TRACKS_URL.format(playlist_id=playlist_id),
                headers=headers,
                params={"limit": limit, "fields": "items(track(id,name))"},
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            ids = [i["track"]["id"] for i in items if i.get("track")]
            top = items[0]["track"]["name"] if items else "Unknown"
            return ids, top

    async def _get_audio_features(
        self, track_ids: list[str], headers: dict
    ) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                FEATURES_URL,
                headers=headers,
                params={"ids": ",".join(track_ids[:100])},
            )
            resp.raise_for_status()
            return [f for f in resp.json().get("audio_features", []) if f]

    @staticmethod
    def _aggregate(features: list[dict], top_track: str) -> dict:
        if not features:
            return SpotifyService._fallback("XX")
        import numpy as np

        vals = {
            k: float(np.mean([f[k] for f in features]))
            for k in ("valence", "energy", "danceability", "acousticness")
        }
        vals["top_genre"] = "pop"  # would come from artist endpoint
        vals["top_track"] = top_track
        return vals

    @staticmethod
    def _fallback(country_code: str) -> dict:
        """Synthetic data for demo / hackathon mode."""
        import hashlib

        seed = int(hashlib.md5(country_code.encode()).hexdigest()[:8], 16)
        rng = __import__("numpy").random.default_rng(seed)
        return {
            "valence": round(float(rng.uniform(0.2, 0.85)), 3),
            "energy": round(float(rng.uniform(0.25, 0.9)), 3),
            "danceability": round(float(rng.uniform(0.3, 0.8)), 3),
            "acousticness": round(float(rng.uniform(0.1, 0.7)), 3),
            "top_genre": "pop",
            "top_track": f"Top Hit ({country_code})",
        }

    async def fetch_all_markets(self) -> dict[str, dict]:
        """Fetch features for every supported market concurrently."""
        tasks = {
            cc: self.fetch_country_features(cc) for cc in SUPPORTED_MARKETS
        }
        results = await asyncio.gather(*tasks.values())
        return dict(zip(tasks.keys(), results))
