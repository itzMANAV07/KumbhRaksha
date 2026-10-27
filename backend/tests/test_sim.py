"""Tests for the simulator engine (M2)."""
import asyncio
import pytest
from app.risk import ZoneState
from app.sim import engine


def setup_engine():
    engine.zone_state.clear()
    engine._seed_counts.clear()
    engine._active_scenario = "idle"
    engine._tick_num = 0
    engine._subscribers.clear()
    zones = [
        {"id": "z1", "name": "Zone 1", "area_m2": 500.0,
         "capacity_assumed": 2000, "adjacency": ["z2"]},
        {"id": "z2", "name": "Zone 2", "area_m2": 300.0,
         "capacity_assumed": 1200, "adjacency": ["z1"]},
    ]
    engine.init_from_zones(zones)


@pytest.mark.asyncio
async def test_tick_increases_count_with_scenario():
    setup_engine()
    from app.sim.scenarios import SCENARIOS
    SCENARIOS["test_up"] = {
        "z1": lambda count, tick: count + 100,
    }
    await engine.set_scenario("test_up")
    initial = engine.zone_state["z1"].count
    await engine.tick()
    assert engine.zone_state["z1"].count == initial + 100
    del SCENARIOS["test_up"]


@pytest.mark.asyncio
async def test_reset_restores_seed():
    setup_engine()
    engine.zone_state["z1"].count = 99999
    await engine.reset()
    assert engine.zone_state["z1"].count == engine._seed_counts["z1"]


@pytest.mark.asyncio
async def test_tick_emits_event():
    setup_engine()
    q = asyncio.Queue()
    engine._subscribers.append(q)
    await engine.tick()
    assert not q.empty()
    import json
    event = json.loads(q.get_nowait())
    assert event["type"] == "tick"
