"""GET /mood/country/{country_code} – detail + 7-day trend for one country."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.models.schemas import CountryDetailResponse
from app.services.trends_service import TrendsService
from app.services.lastfm_service import LastFmService, SUPPORTED_COUNTRIES
from app.services.news_service import NewsService
from app.core.mood_engine import compute_mood

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mood", tags=["mood"])


@router.get("/country/{country_code}", response_model=CountryDetailResponse)
async def get_country_mood(
    country_code: str,
    db=Depends(get_db),
):
    cc = country_code.upper()

    # Try DB first
    if db:
        try:
            svc = TrendsService(db)
            latest = await svc.get_latest_country(cc)
            if latest:
                trend = await svc.get_country_trend(cc)
                spike = await svc.has_active_spike(cc)
                return CountryDetailResponse(
                    country_code=latest.country_code,
                    country_name=latest.country_name,
                    mood_score=latest.mood_score,
                    mood_label=latest.mood_label,
                    color_code=latest.color_code,
                    valence=latest.valence,
                    energy=latest.energy,
                    danceability=latest.danceability,
                    acousticness=latest.acousticness,
                    top_genre=latest.top_genre,
                    top_track=latest.top_track,
                    news_sentiment=latest.news_sentiment,
                    trend=trend,
                    spike_active=spike,
                )
        except Exception:
            pass

    # Fallback: compute live from Last.fm
    lastfm = LastFmService()
    news = NewsService()
    feat = await lastfm.fetch_country_features(cc)
    sentiment = await news.fetch_sentiment(cc)
    mood = compute_mood(
        valence=feat["valence"],
        energy=feat["energy"],
        danceability=feat.get("danceability", 0.5),
        acousticness=feat.get("acousticness", 0.5),
        news_sentiment=sentiment,
    )

    return CountryDetailResponse(
        country_code=cc,
        country_name=SUPPORTED_COUNTRIES.get(cc, cc),
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
        trend=[],
        spike_active=False,
    )
