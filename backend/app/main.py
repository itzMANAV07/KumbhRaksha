"""
FastAPI application entry point.
Lifespan: create DB tables, seed zones and facilities, start simulator.
"""
from __future__ import annotations

import json
import logging
import pathlib
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.database import engine as db_engine, Base, AsyncSessionLocal
from app.models import Zone, Facility
from app.schemas import ZoneGeoJSON, FacilitiesList
from app.sim import engine as sim_engine
from app.routers import events, zones, chat, sos, lost_found
from app.adapters import telegram as tg_adapter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data"


async def _seed_zones(session) -> list[dict]:
    """Load zones.geojson into DB if not already present. Return list of zone dicts."""
    geojson_path = DATA_DIR / "zones.geojson"
    if not geojson_path.exists():
        logger.warning(
            f"zones.geojson not found at {geojson_path}. "
            "Zones will be empty until M1 data is added."
        )
        return []

    raw = json.loads(geojson_path.read_text(encoding="utf-8"))
    validated = ZoneGeoJSON.model_validate(raw)

    seeded = []
    for feature in validated.features:
        props = feature.properties
        existing = await session.get(Zone, props.id)
        if existing is None:
            zone = Zone(id=props.id, name=props.name, area_m2=props.area_m2,
                        capacity_assumed=props.capacity_assumed)
            zone.adjacency = props.adjacency
            zone.geometry = feature.geometry
            session.add(zone)
            logger.info(f"Seeded zone: {props.id}")
        seeded.append({
            "id": props.id,
            "name": props.name,
            "area_m2": props.area_m2,
            "capacity_assumed": props.capacity_assumed,
            "adjacency": props.adjacency,
        })
    await session.commit()
    return seeded


async def _seed_facilities(session) -> None:
    """Load facilities.json into DB if not already present."""
    fac_path = DATA_DIR / "facilities.json"
    if not fac_path.exists():
        logger.warning(
            f"facilities.json not found at {fac_path}. "
            "Facilities will be empty until M1 data is added."
        )
        return

    raw = json.loads(fac_path.read_text(encoding="utf-8"))
    validated = FacilitiesList.model_validate(raw)

    for fac in validated.facilities:
        existing = await session.get(Facility, fac.id)
        if existing is None:
            facility = Facility(
                id=fac.id, name=fac.name, type=fac.type,
                lat=fac.lat, lon=fac.lon,
                zone_id=fac.zone_id, demo=fac.demo,
            )
            session.add(facility)
            logger.info(f"Seeded facility: {fac.id}")
    await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        zone_dicts = await _seed_zones(session)
        await _seed_facilities(session)

    # Initialise simulator
    sim_engine.init_from_zones(zone_dicts)

    # Start simulator background task
    sim_task = asyncio.create_task(sim_engine.run_forever())

    # Start Telegram long-polling adapter (optional — disabled if token not set)
    tg_task = asyncio.create_task(tg_adapter.run_polling())

    logger.info("KumbhRaksha backend ready.")
    yield

    # Shutdown
    for task in (sim_task, tg_task):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="KumbhRaksha API",
    version="0.1.0",
    description="Crowd safety system for Kumbh Mela — SIMULATED DATA",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Routers
app.include_router(events.router)
app.include_router(zones.router)
app.include_router(chat.router)
app.include_router(sos.router)
app.include_router(lost_found.router)

# Simulator control
from app.schemas import ScenarioRequest
from app.sim import engine as _sim


@app.post("/sim/scenario")
async def set_scenario(req: ScenarioRequest):
    await _sim.set_scenario(req.scenario)
    return {"ok": True, "scenario": req.scenario}


@app.post("/sim/reset")
async def reset_sim():
    await _sim.reset()
    return {"ok": True}
