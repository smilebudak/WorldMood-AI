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
    """Get Redis connection with graceful fallback."""
    global _redis, _redis_failed
    if _redis_failed:
        return None
    if _redis is None:
        try:
            import redis.asyncio as aioredis
            _redis = aioredis.from_url(
                settings.REDIS_URL, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            await _redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e} – running without cache")
            _redis_failed = True
            return None
    return _redis


# ── DB session ────────────────────────────────────────────────────────────────

_db_failed = False


async def get_db():
    """Get database session with graceful fallback."""
    global _db_failed
    if _db_failed:
        yield None
        return
    try:
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            yield session
    except Exception as e:
        logger.warning(f"Database unavailable: {e} – running in live-only mode")
        _db_failed = True
        yield None
        _db_failed = True
        yield None
