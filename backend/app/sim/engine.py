"""
Simulator engine.
Runs as an asyncio background task. Manages zone_state dict and broadcasts
SSE events after each tick.
Implements AGENTS.md Section 7.1.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import AsyncIterator, Optional

from app.config import settings
from app.risk import ZoneState, update_state, suggest_divert
from app.sim.scenarios import SCENARIOS, DEFAULT_SCENARIO

logger = logging.getLogger(__name__)

# ── Shared state ──────────────────────────────────────────────────────────────

zone_state: dict[str, ZoneState] = {}
_active_scenario: str = DEFAULT_SCENARIO
_tick_num: int = 0

# SSE subscriber queues
_subscribers: list[asyncio.Queue] = []

# Seed counts per zone (reset target)
_seed_counts: dict[str, int] = {}


# ── Initialise ────────────────────────────────────────────────────────────────

def init_from_zones(zones: list[dict]) -> None:
    """
    Populate zone_state from a list of zone dicts loaded from the DB.
    Called from the FastAPI lifespan after DB seed.
    """
    global zone_state, _seed_counts
    for z in zones:
        seed = max(1, int(z["area_m2"] * 0.1))  # ~10% capacity as start count
        state = ZoneState(
            zone_id=z["id"],
            count=seed,
            count_prev=seed,
            area_m2=z["area_m2"],
            adjacency=z.get("adjacency", []),
        )
        update_state(state)
        zone_state[z["id"]] = state
        _seed_counts[z["id"]] = seed
    logger.info(f"Simulator initialised with {len(zone_state)} zones")


# ── Scenario control ──────────────────────────────────────────────────────────

async def set_scenario(name: str) -> None:
    global _active_scenario, _tick_num
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}. Available: {list(SCENARIOS)}")
    _active_scenario = name
    _tick_num = 0
    logger.info(f"Scenario set to: {name}")


async def reset() -> None:
    global _active_scenario, _tick_num
    _active_scenario = DEFAULT_SCENARIO
    _tick_num = 0
    for zone_id, state in zone_state.items():
        seed = _seed_counts.get(zone_id, 0)
        state.count = seed
        state.count_prev = seed
        update_state(state)
    await _broadcast({"type": "reset"})
    logger.info("Simulator reset")


# ── Tick ──────────────────────────────────────────────────────────────────────

async def tick() -> None:
    global _tick_num
    _tick_num += 1
    scenario_deltas = SCENARIOS.get(_active_scenario, {})

    old_levels = {zid: s.level for zid, s in zone_state.items()}

    for zone_id, state in zone_state.items():
        state.count_prev = state.count
        delta_fn = scenario_deltas.get(zone_id)
        if delta_fn is not None:
            state.count = delta_fn(state.count, _tick_num)
        update_state(state)
        # Compute divert suggestion
        state.divert_to = suggest_divert(zone_id, zone_state)

    new_levels = {zid: s.level for zid, s in zone_state.items()}

    # Build SSE payload
    zones_payload = []
    for state in zone_state.values():
        zones_payload.append({
            "zone_id": state.zone_id,
            "count": state.count,
            "density": round(state.density, 4),
            "level": state.level,
            "forecast_minutes": state.forecast_minutes,
            "divert_to": state.divert_to,
            "updated_at": state.updated_at.isoformat(),
        })

    event = {
        "type": "tick",
        "tick_num": _tick_num,
        "scenario": _active_scenario,
        "zones": zones_payload,
    }
    await _broadcast(event)

    # Return level changes for subscription alerting
    return {
        "old_levels": old_levels,
        "new_levels": new_levels,
    }


# ── Background task ───────────────────────────────────────────────────────────

async def run_forever() -> None:
    logger.info(f"Simulator starting (tick every {settings.sim_tick_seconds}s)")
    while True:
        await asyncio.sleep(settings.sim_tick_seconds)
        try:
            await tick()
        except Exception as exc:
            logger.error(f"Simulator tick error: {exc}", exc_info=True)


# ── SSE broadcast ─────────────────────────────────────────────────────────────

async def _broadcast(event: dict) -> None:
    data = json.dumps(event)
    dead = []
    for q in _subscribers:
        try:
            q.put_nowait(data)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        _subscribers.remove(q)


async def subscribe() -> AsyncIterator[str]:
    """Yield SSE-formatted event strings for a new subscriber."""
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.append(q)
    try:
        # Send current state immediately on connect
        zones_payload = [
            {
                "zone_id": s.zone_id,
                "count": s.count,
                "density": round(s.density, 4),
                "level": s.level,
                "forecast_minutes": s.forecast_minutes,
                "divert_to": s.divert_to,
                "updated_at": s.updated_at.isoformat(),
            }
            for s in zone_state.values()
        ]
        initial = json.dumps({"type": "init", "zones": zones_payload})
        yield f"data: {initial}\n\n"

        while True:
            data = await q.get()
            yield f"data: {data}\n\n"
    finally:
        if q in _subscribers:
            _subscribers.remove(q)


async def broadcast_incident(incident_data: dict) -> None:
    """Broadcast an SOS incident event to all SSE subscribers."""
    await _broadcast({"type": "incident", "incident": incident_data})
