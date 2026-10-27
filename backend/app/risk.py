"""
Risk engine: density -> level -> forecast -> divert suggestion.
Implements AGENTS.md Sections 7.2, 7.3, 7.4.
"""
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

from app.config import settings

if TYPE_CHECKING:
    pass


@dataclass
class ZoneState:
    zone_id: str
    count: int = 0
    count_prev: int = 0
    area_m2: float = 1.0
    adjacency: list[str] = field(default_factory=list)
    density: float = 0.0
    level: str = "green"
    forecast_minutes: Optional[float] = None
    divert_to: Optional[str] = None
    updated_at: datetime = field(default_factory=datetime.utcnow)


def compute_density(count: int, area_m2: float) -> float:
    """Return people per square metre."""
    if area_m2 <= 0:
        raise ValueError(f"area_m2 must be positive, got {area_m2}")
    return count / area_m2


def compute_level(density: float) -> str:
    """Map density to risk level per AGENTS.md Section 7.2."""
    if density >= settings.density_red:
        return "red"
    if density >= settings.density_orange:
        return "orange"
    if density >= settings.density_yellow:
        return "yellow"
    return "green"


def forecast_minutes(
    count_now: int,
    count_prev: int,
    tick_seconds: int,
    area_m2: float,
) -> Optional[float]:
    """
    Estimate minutes until red threshold is reached.
    Returns None if already red, decreasing, or > 30 min away.
    Implements AGENTS.md Section 7.3.
    """
    net_rate = (count_now - count_prev) / tick_seconds  # people/second
    if net_rate <= 0:
        return None
    red_count = settings.density_red * area_m2
    if count_now >= red_count:
        return None  # already red
    minutes = (red_count - count_now) / (net_rate * 60)
    if minutes >= settings.forecast_window_minutes:
        return None
    return round(minutes, 1)


def suggest_divert(
    zone_id: str,
    zone_states: dict[str, ZoneState],
) -> Optional[str]:
    """
    Return the id of the safest adjacent zone (lowest density, not red).
    Returns None if no safe adjacent zone exists.
    Implements AGENTS.md Section 7.4.
    """
    state = zone_states.get(zone_id)
    if state is None:
        return None
    candidates = [
        zone_states[adj_id]
        for adj_id in state.adjacency
        if adj_id in zone_states and zone_states[adj_id].level != "red"
    ]
    if not candidates:
        return None
    best = min(candidates, key=lambda z: z.density)
    return best.zone_id


def update_state(state: ZoneState) -> ZoneState:
    """Recompute density, level, forecast and divert for a zone in place."""
    state.density = compute_density(state.count, state.area_m2)
    state.level = compute_level(state.density)
    state.forecast_minutes = forecast_minutes(
        state.count, state.count_prev,
        settings.sim_tick_seconds, state.area_m2
    )
    state.updated_at = datetime.utcnow()
    return state
