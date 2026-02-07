"""
TrendsService – provides mood trend history for a country (last N days).
Reads from the database and is also the write-path after daily ingestion.
"""

from __future__ import annotations

import datetime as dt
import logging
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CountryMood, MoodSpike
from app.models.schemas import MoodTrendPoint

logger = logging.getLogger(__name__)


class TrendsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_latest_global(self) -> list[CountryMood]:
        """Return the most recent mood row for every country."""
        subq = (
            select(
                CountryMood.country_code,
                CountryMood.date,
            )
            .distinct(CountryMood.country_code)
            .order_by(CountryMood.country_code, desc(CountryMood.date))
            .subquery()
        )
        stmt = (
            select(CountryMood)
            .join(
                subq,
                (CountryMood.country_code == subq.c.country_code)
                & (CountryMood.date == subq.c.date),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_country_trend(
        self, country_code: str, days: int = 7
    ) -> list[MoodTrendPoint]:
        """Return last *days* mood snapshots for a single country."""
        since = dt.datetime.utcnow() - dt.timedelta(days=days)
        stmt = (
            select(CountryMood)
            .where(
                CountryMood.country_code == country_code.upper(),
                CountryMood.date >= since,
            )
            .order_by(CountryMood.date)
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [
            MoodTrendPoint(
                date=r.date.date(),
                mood_score=r.mood_score,
                mood_label=r.mood_label,
            )
            for r in rows
        ]

    async def get_latest_country(self, country_code: str) -> Optional[CountryMood]:
        stmt = (
            select(CountryMood)
            .where(CountryMood.country_code == country_code.upper())
            .order_by(desc(CountryMood.date))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def has_active_spike(self, country_code: str) -> bool:
        """Check if a spike was detected in the last 24 hours."""
        since = dt.datetime.utcnow() - dt.timedelta(hours=24)
        stmt = (
            select(MoodSpike)
            .where(
                MoodSpike.country_code == country_code.upper(),
                MoodSpike.detected_at >= since,
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_recent_spikes(self, limit: int = 20) -> list[MoodSpike]:
        stmt = (
            select(MoodSpike)
            .order_by(desc(MoodSpike.detected_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def upsert_mood(self, data: dict) -> CountryMood:
        """Insert or update a daily mood row."""
        row = CountryMood(**data)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def insert_spike(self, data: dict) -> MoodSpike:
        row = MoodSpike(**data)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row
