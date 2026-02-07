from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Application ---
    APP_NAME: str = "MoodAtlas API"
    DEBUG: bool = False

    # --- Database ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://moodatlas:moodatlas@localhost:5432/moodatlas",
    )

    # --- Redis ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL_SECONDS: int = 600  # 10 minutes

    # --- Music data provider ---
    MUSIC_PROVIDER: str = os.getenv("MUSIC_PROVIDER", "lastfm")
    LASTFM_API_KEY: str = os.getenv("LASTFM_API_KEY", "")

    # --- News / sentiment ---
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

    # --- Google Trends ---
    TRENDS_ENABLED: bool = True

    # --- Mapbox (passed to frontend, but backend may proxy) ---
    MAPBOX_TOKEN: str = os.getenv("MAPBOX_TOKEN", "")

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
