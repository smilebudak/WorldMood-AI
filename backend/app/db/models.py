from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CountryMood(Base):
    """Aggregated mood snapshot per country per day."""

    __tablename__ = "country_mood"
    __table_args__ = (
        UniqueConstraint("country_code", "date", name="uq_country_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), nullable=False, index=True)
    country_name = Column(String(120), nullable=False)
    date = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    # Mood metrics
    mood_score = Column(Float, nullable=False)  # -1.0 … 1.0
    mood_label = Column(String(20), nullable=False)  # Happy | Calm | Sad | Angry | Anxious
    color_code = Column(String(7), nullable=False)  # hex

    # Audio feature averages
    valence = Column(Float, nullable=True)
    energy = Column(Float, nullable=True)
    danceability = Column(Float, nullable=True)
    acousticness = Column(Float, nullable=True)

    # Supplementary
    top_genre = Column(String(60), nullable=True)
    top_track = Column(String(200), nullable=True)
    news_sentiment = Column(Float, nullable=True)
    news_headlines = Column(Text, nullable=True)  # JSON array of headlines
    news_summary = Column(Text, nullable=True)    # AI-generated summary

    created_at = Column(DateTime, server_default=func.now())


class MoodSpike(Base):
    """Detected mood anomalies / spikes per country."""

    __tablename__ = "mood_spike"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), nullable=False, index=True)
    detected_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    previous_label = Column(String(20), nullable=False)
    new_label = Column(String(20), nullable=False)
    delta = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
