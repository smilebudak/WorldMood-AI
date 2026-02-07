"""GET /spikes – recent mood anomalies."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_db
from app.models.schemas import SpikeListResponse, SpikeResponse
from app.services.trends_service import TrendsService

router = APIRouter(tags=["spikes"])


@router.get("/spikes", response_model=SpikeListResponse)
async def get_spikes(
    limit: int = 20,
    db=Depends(get_db),
):
    if not db:
        return SpikeListResponse(spikes=[])

    try:
        svc = TrendsService(db)
        rows = await svc.get_recent_spikes(limit=limit)
        return SpikeListResponse(
            spikes=[SpikeResponse.model_validate(r) for r in rows]
        )
    except Exception:
        return SpikeListResponse(spikes=[])
