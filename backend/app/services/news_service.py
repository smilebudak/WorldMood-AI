"""
NewsService – fetches headline sentiment per country to supplement the
music-based mood signal.  Uses NewsAPI (newsapi.org) by default.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx
import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# Minimal keyword-based sentiment (replace with a real NLP model in prod)
POSITIVE_WORDS = frozenset(
    ["win", "celebrate", "peace", "growth", "success", "record", "breakthrough"]
)
NEGATIVE_WORDS = frozenset(
    ["war", "crisis", "attack", "death", "crash", "protest", "disaster", "flood"]
)


class NewsService:
    async def fetch_sentiment(self, country_code: str) -> Optional[float]:
        """Return a sentiment score between -1.0 and 1.0 for a country's
        current headlines, or ``None`` if unavailable."""
        if not settings.NEWS_API_KEY:
            return self._fallback_sentiment(country_code)

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    NEWS_API_URL,
                    params={
                        "country": country_code.lower(),
                        "pageSize": 20,
                        "apiKey": settings.NEWS_API_KEY,
                    },
                    timeout=10,
                )
                resp.raise_for_status()
                articles = resp.json().get("articles", [])
                return self._score_articles(articles)
        except Exception:
            logger.warning("News fetch failed for %s, using fallback", country_code)
            return self._fallback_sentiment(country_code)

    @staticmethod
    def _score_articles(articles: list[dict]) -> float:
        """Naive keyword sentiment scoring.  Replace with transformer-based
        model (e.g. HuggingFace pipeline) for production accuracy."""
        if not articles:
            return 0.0

        scores: list[float] = []
        for a in articles:
            text = f"{a.get('title', '')} {a.get('description', '')}".lower()
            pos = sum(1 for w in POSITIVE_WORDS if w in text)
            neg = sum(1 for w in NEGATIVE_WORDS if w in text)
            total = pos + neg
            if total == 0:
                scores.append(0.0)
            else:
                scores.append((pos - neg) / total)

        return float(np.clip(np.mean(scores), -1.0, 1.0))

    @staticmethod
    def _fallback_sentiment(country_code: str) -> float:
        """Deterministic synthetic sentiment for demo mode."""
        import hashlib

        seed = int(hashlib.md5(f"news-{country_code}".encode()).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        return round(float(rng.uniform(-0.3, 0.5)), 3)
