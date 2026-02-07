"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import async_session_factory
from app.services.trends_service import TrendsService

settings = get_settings()

# ── Redis singleton ───────────────────────────────────────────────────────────

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True
        )
    return _redis


# ── DB session ────────────────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# ── Trend service ─────────────────────────────────────────────────────────────


async def get_trends_service(
    db: AsyncSession = None,  # injected via Depends in routes
) -> TrendsService:
    # When called from Depends chain, db comes from get_db
    async for session in get_db():
        return TrendsService(session)
