"""GET /mood/global  – returns mood data for all countries."""

from __future__ import annotations

import datetime as dt
import json
import logging

from fastapi import APIRouter, Depends

from app.api.deps import get_redis, get_db
from app.config import get_settings
from app.models.schemas import GlobalMoodResponse, CountryMoodResponse
from app.services.trends_service import TrendsService
from app.services.lastfm_service import LastFmService
from app.services.news_service import NewsService
from app.core.mood_engine import compute_mood

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

    COUNTRY_NAMES = _country_names()

    for cc, feat in market_features.items():
        sentiment = await news.fetch_sentiment(cc)
        mood = compute_mood(
            valence=feat["valence"],
            energy=feat["energy"],
            danceability=feat.get("danceability", 0.5),
            acousticness=feat.get("acousticness", 0.5),
            news_sentiment=sentiment,
        )
        countries.append(
            CountryMoodResponse(
                country_code=cc,
                country_name=COUNTRY_NAMES.get(cc, cc),
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
            )
        )

    resp = GlobalMoodResponse(updated_at=dt.datetime.utcnow(), countries=countries)

    if cache:
        try:
            await cache.setex(CACHE_KEY, settings.CACHE_TTL_SECONDS, resp.model_dump_json())
        except Exception:
            pass

    return resp


def _country_names() -> dict[str, str]:
    return {
        "US": "United States", "GB": "United Kingdom", "DE": "Germany",
        "FR": "France", "JP": "Japan", "BR": "Brazil", "IN": "India",
        "AU": "Australia", "CA": "Canada", "MX": "Mexico", "KR": "South Korea",
        "SE": "Sweden", "NO": "Norway", "FI": "Finland", "ES": "Spain",
        "IT": "Italy", "NL": "Netherlands", "PL": "Poland", "TR": "Turkey",
        "ZA": "South Africa", "NG": "Nigeria", "EG": "Egypt",
        "AR": "Argentina", "CL": "Chile", "CO": "Colombia",
        "PH": "Philippines", "ID": "Indonesia", "TH": "Thailand",
        "VN": "Vietnam", "RU": "Russia",
    }
