"""GET /mood/global  – returns mood data for all countries."""

from __future__ import annotations

import datetime as dt
import json
import logging

from fastapi import APIRouter, Depends, BackgroundTasks

from app.api.deps import get_redis, get_db
from app.config import get_settings
from app.models.schemas import GlobalMoodResponse, CountryMoodResponse
from app.services.trends_service import TrendsService
from app.services.lastfm_service import LastFmService, SUPPORTED_COUNTRIES
from app.services.news_service import NewsService
from app.core.mood_engine import compute_mood
from app.db.session import async_session_factory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mood", tags=["mood"])
settings = get_settings()

CACHE_KEY = "mood:global:latest"


@router.get("/global", response_model=GlobalMoodResponse)
async def get_global_mood(
    cache=Depends(get_redis),
    db=Depends(get_db),
):
    # 1. Try cache
    if cache:
        try:
            cached = await cache.get(CACHE_KEY)
            if cached:
                return GlobalMoodResponse(**json.loads(cached))
        except Exception:
            pass

    # 2. Try DB
    if db:
        try:
            svc = TrendsService(db)
            rows = await svc.get_latest_global()
            if rows:
                countries = [CountryMoodResponse.model_validate(r) for r in rows]
                resp = GlobalMoodResponse(updated_at=dt.datetime.utcnow(), countries=countries)
                if cache:
                    await cache.setex(CACHE_KEY, settings.CACHE_TTL_SECONDS, resp.model_dump_json())
                return resp
        except Exception:
            pass

    # 3. Compute on-the-fly from Last.fm
    lastfm = LastFmService()
    news = NewsService()

    market_features = await lastfm.fetch_all_markets()
    countries: list[CountryMoodResponse] = []

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
        
        # Generate AI mood summary
        country_name = SUPPORTED_COUNTRIES.get(cc, cc)
        summary = await news.generate_mood_summary(
            country_code=cc,
            country_name=country_name,
            mood_label=mood.mood_label,
            valence=feat["valence"],
            energy=feat["energy"],
            top_track=feat.get("top_track"),
            top_genre=feat.get("top_genre"),
            headlines=headlines[:5] if headlines else None,
        )
        
        countries.append(
            CountryMoodResponse(
                country_code=cc,
                country_name=country_name,
                date=dt.datetime.utcnow(),
                mood_score=mood.mood_score,
                mood_label=mood.mood_label,
                color_code=mood.color_code,
                valence=feat["valence"],
                energy=feat["energy"],
                danceability=feat.get("danceability"),
                acousticness=feat.get("acousticness"),
                top_genre=feat.get("top_genre"),
                top_track=feat.get("top_track"),
                news_sentiment=sentiment,
                news_headlines=headlines[:5] if headlines else None,
                news_summary=summary,
            )
        )

    resp = GlobalMoodResponse(updated_at=dt.datetime.utcnow(), countries=countries)

    # 4. Save to DB in background
    if db:
        try:
            svc = TrendsService(db)
            for country in countries:
                # Convert headlines list to JSON string for DB storage
                headlines_json = json.dumps(country.news_headlines) if country.news_headlines else None
                
                await svc.upsert_mood({
                    "country_code": country.country_code,
                    "country_name": country.country_name,
                    "date": country.date,
                    "mood_score": country.mood_score,
                    "mood_label": country.mood_label,
                    "color_code": country.color_code,
                    "valence": country.valence,
                    "energy": country.energy,
                    "danceability": country.danceability,
                    "acousticness": country.acousticness,
                    "top_genre": country.top_genre,
                    "top_track": country.top_track,
                    "news_sentiment": country.news_sentiment,
                    "news_headlines": headlines_json,
                    "news_summary": country.news_summary if hasattr(country, 'news_summary') else None,
                })
            logger.info("Saved %d mood records to database", len(countries))
        except Exception as e:
            logger.error("Failed to save mood to DB: %s", e)

    if cache:
        try:
            await cache.setex(CACHE_KEY, settings.CACHE_TTL_SECONDS, resp.model_dump_json())
        except Exception:
            pass

    return resp


# _country_names removed - using SUPPORTED_COUNTRIES from lastfm_service instead
