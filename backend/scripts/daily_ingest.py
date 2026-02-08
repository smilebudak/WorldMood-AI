#!/usr/bin/env python3
"""
daily_ingest.py – Run once per day (via cron / scheduler) to pull fresh music
features + news sentiment, compute mood, detect spikes, and persist to Postgres.

Usage:
    python -m scripts.daily_ingest
"""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_settings
from app.db.session import async_session_factory, engine
from app.db.models import Base
from app.services.lastfm_service import LastFmService, SUPPORTED_COUNTRIES
from app.services.news_service import NewsService
from app.services.trends_service import TrendsService
from app.core.mood_engine import compute_mood
from app.core.spike_detector import detect_spike
from app.services.gemini_service import GeminiService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ingest")
settings = get_settings()

# Using SUPPORTED_COUNTRIES from lastfm_service


async def run() -> None:
    # Ensure tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    lastfm = LastFmService()
    news = NewsService()
    gemini = GeminiService()

    market_features = await lastfm.fetch_all_markets()
    logger.info("Fetched features for %d markets", len(market_features))

    async with async_session_factory() as db:
        svc = TrendsService(db)

        for cc, feat in market_features.items():
            sentiment = await news.fetch_sentiment(cc)
            headlines = await news.fetch_headlines(cc)
            mood = compute_mood(
                valence=feat["valence"],
                energy=feat["energy"],
                danceability=feat.get("danceability", 0.5),
                acousticness=feat.get("acousticness", 0.5),
                news_sentiment=sentiment,
            )

            # Generate AI Summary
            ai_summary = None
            if headlines:
                try:
                    ai_summary = await gemini.generate_mood_summary(
                        country_name=SUPPORTED_COUNTRIES.get(cc, cc),
                        headlines=headlines[:5],
                        mood_label=mood.mood_label
                    )
                except Exception as e:
                    logger.error(f"Gemini failed for {cc}: {e}")

            # Convert headlines to JSON for storage
            import json
            headlines_json = json.dumps(headlines[:5]) if headlines else None

            # Persist mood
            await svc.upsert_mood(
                {
                    "country_code": cc,
                    "country_name": SUPPORTED_COUNTRIES.get(cc, cc),
                    "date": dt.datetime.utcnow(),
                    "mood_score": mood.mood_score,
                    "mood_label": mood.mood_label,
                    "color_code": mood.color_code,
                    "valence": feat["valence"],
                    "energy": feat["energy"],
                    "danceability": feat.get("danceability"),
                    "acousticness": feat.get("acousticness"),
                    "top_genre": feat.get("top_genre"),
                    "top_track": feat.get("top_track"),
                    "news_sentiment": sentiment,
                    "news_headlines": headlines_json,
                    "news_summary": ai_summary,
                }
            )

            # Spike detection
            trend = await svc.get_country_trend(cc, days=14)
            if len(trend) >= 3:
                evt = detect_spike(
                    country_code=cc,
                    history_scores=[t.mood_score for t in trend[:-1]],
                    history_labels=[t.mood_label for t in trend[:-1]],
                    current_score=mood.mood_score,
                    current_label=mood.mood_label,
                )
                if evt:
                    await svc.insert_spike(
                        {
                            "country_code": cc,
                            "detected_at": dt.datetime.utcnow(),
                            "previous_label": evt.previous_label,
                            "new_label": evt.new_label,
                            "delta": evt.delta,
                            "reason": evt.reason,
                        }
                    )
                    logger.warning("SPIKE %s: %s → %s (Δ%.3f)", cc, evt.previous_label, evt.new_label, evt.delta)

            logger.info("✓ %s – %s (%.3f)", cc, mood.mood_label, mood.mood_score)

    await engine.dispose()
    logger.info("Daily ingest complete.")


if __name__ == "__main__":
    asyncio.run(run())
