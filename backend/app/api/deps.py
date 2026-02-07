"""Shared FastAPI dependencies – graceful fallback when DB/Redis unavailable."""

from __future__ import annotations

import logging
from typing import AsyncGenerator, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Redis ─────────────────────────────────────────────────────────────────────

_redis = None
_redis_failed = False


async def get_redis():
    global _redis, _redis_failed
    if _redis_failed:
        return None
    if _redis is None:
        try:
            import redis.asyncio as aioredis
            _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await _redis.ping()
        except Exception:
            logger.warning("Redis unavailable – running without cache")
            _redis_failed = True
            return None
    return _redis


# ── DB session ────────────────────────────────────────────────────────────────

_db_failed = False


async def get_db():
    global _db_failed
    if _db_failed:
        yield None
        return
    try:
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            yield session
    except Exception:
        logger.warning("Database unavailable – running in live-only mode")
        _db_failed = True
        yield None
