"""POST /sos — SOS / incident endpoint."""
from __future__ import annotations
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Incident, Facility
from app.schemas import SOSRequest, SOSResponse, ChatResponse, IncidentResponse
from app.sos import find_nearest_facility, haversine_km, build_sos_reply
from app.chat import templates
from app.sim import engine as sim_engine

router = APIRouter(tags=["sos"])
logger = logging.getLogger(__name__)


async def _handle_sos(
    chat_id: str,
    lat: float,
    lon: float,
    language: str,
    lite_mode: bool,
    db: AsyncSession,
) -> ChatResponse:
    result = await db.execute(select(Facility))
    facilities = [
        {"id": f.id, "name": f.name, "lat": f.lat, "lon": f.lon}
        for f in result.scalars().all()
    ]
    nearest = find_nearest_facility(lat, lon, facilities)

    # Create incident
    incident = Incident(
        chat_id=chat_id,
        lat=lat,
        lon=lon,
        nearest_facility_id=nearest["id"] if nearest else None,
        status="open",
        created_at=datetime.utcnow(),
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    # Broadcast SSE
    incident_data = {
        "id": incident.id,
        "chat_id": chat_id,
        "lat": lat,
        "lon": lon,
        "nearest_facility_id": incident.nearest_facility_id,
        "status": "open",
        "created_at": incident.created_at.isoformat(),
        "facility_name": nearest["name"] if nearest else None,
    }
    await sim_engine.broadcast_incident(incident_data)

    # Build reply
    if nearest:
        dist = haversine_km(lat, lon, nearest["lat"], nearest["lon"])
        maps_link = f"https://maps.google.com/?q={nearest['lat']},{nearest['lon']}"
        if language == "hi":
            reply = templates.sos_reply_hi(nearest["name"], dist, maps_link)
        else:
            reply = templates.sos_reply_en(nearest["name"], dist, maps_link)
    else:
        reply = build_sos_reply(None, lat, lon)

    if lite_mode:
        reply = templates.lite(reply)

    logger.info(f"SOS incident {incident.id} created for chat {chat_id}")
    return ChatResponse(text=reply)


@router.post("/sos", response_model=SOSResponse)
async def sos(req: SOSRequest, db: AsyncSession = Depends(get_db)):
    response = await _handle_sos(req.chat_id, req.lat, req.lon, "en", False, db)
    # Fetch the last incident
    result = await db.execute(
        select(Incident)
        .where(Incident.chat_id == req.chat_id)
        .order_by(Incident.created_at.desc())
    )
    incident = result.scalars().first()
    return SOSResponse(incident_id=incident.id if incident else -1, reply=response.text)


@router.get("/incidents", response_model=list[IncidentResponse])
async def list_incidents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).order_by(Incident.created_at.desc()))
    return [
        IncidentResponse(
            id=i.id, chat_id=i.chat_id, lat=i.lat, lon=i.lon,
            nearest_facility_id=i.nearest_facility_id,
            status=i.status, created_at=i.created_at,
        )
        for i in result.scalars().all()
    ]


@router.patch("/incidents/{incident_id}")
async def update_incident(
    incident_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    new_status = body.get("status")
    if new_status not in {"acknowledged", "resolved"}:
        raise HTTPException(status_code=422, detail="Invalid status")
    incident.status = new_status
    await db.commit()
    return {"ok": True, "status": new_status}
