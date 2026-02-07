from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


# ---------- Mood ----------


class MoodBase(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=3)
    country_name: str
    mood_score: float = Field(..., ge=-1.0, le=1.0)
    mood_label: str
    color_code: str

    valence: Optional[float] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    acousticness: Optional[float] = None

    top_genre: Optional[str] = None
    top_track: Optional[str] = None
    news_sentiment: Optional[float] = None
    news_headlines: Optional[list[str]] = None
    news_summary: Optional[str] = None


class CountryMoodResponse(MoodBase):
    date: dt.datetime

    class Config:
        from_attributes = True


class GlobalMoodResponse(BaseModel):
    updated_at: dt.datetime
    countries: list[CountryMoodResponse]


# ---------- Trends ----------


class MoodTrendPoint(BaseModel):
    date: dt.date
    mood_score: float
    mood_label: str


class CountryDetailResponse(MoodBase):
    trend: list[MoodTrendPoint] = []
    spike_active: bool = False


# ---------- Spikes ----------


class SpikeResponse(BaseModel):
    id: int
    country_code: str
    detected_at: dt.datetime
    previous_label: str
    new_label: str
    delta: float
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class SpikeListResponse(BaseModel):
    spikes: list[SpikeResponse]
