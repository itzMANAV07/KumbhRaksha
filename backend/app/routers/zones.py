"""GET /zones and GET /zones/{zone_id}"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Zone
from app.schemas import ZoneResponse
from app.sim import engine as sim_engine

router = APIRouter(prefix="/zones", tags=["zones"])


def _enrich(zone: Zone) -> ZoneResponse:
    state = sim_engine.zone_state.get(zone.id)
    return ZoneResponse(
        id=zone.id,
        name=zone.name,
        area_m2=zone.area_m2,
        capacity_assumed=zone.capacity_assumed,
        adjacency=zone.adjacency,
        geometry=zone.geometry,
        count=state.count if state else None,
        density=round(state.density, 4) if state else None,
        level=state.level if state else None,
        forecast_minutes=state.forecast_minutes if state else None,
        divert_to=state.divert_to if state else None,
    )


@router.get("", response_model=list[ZoneResponse])
async def list_zones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone))
    zones = result.scalars().all()
    return [_enrich(z) for z in zones]


@router.get("/{zone_id}", response_model=ZoneResponse)
async def get_zone(zone_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if zone is None:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id!r} not found")
    return _enrich(zone)
