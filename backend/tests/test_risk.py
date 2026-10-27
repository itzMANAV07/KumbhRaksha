"""Tests for the risk engine (M2)."""
import pytest
from app.risk import compute_density, compute_level, forecast_minutes, suggest_divert, ZoneState


def test_density_math():
    assert compute_density(1000, 500) == pytest.approx(2.0)
    assert compute_density(0, 100) == pytest.approx(0.0)

def test_density_zero_area_raises():
    with pytest.raises(ValueError):
        compute_density(100, 0)

def test_level_boundaries():
    assert compute_level(0.5) == "green"
    assert compute_level(1.0) == "yellow"
    assert compute_level(2.5) == "orange"
    assert compute_level(4.0) == "red"
    assert compute_level(5.0) == "red"

def test_forecast_positive_rate():
    result = forecast_minutes(count_now=1000, count_prev=800, tick_seconds=5, area_m2=500)
    assert result is not None
    assert result > 0

def test_forecast_zero_rate():
    result = forecast_minutes(count_now=1000, count_prev=1000, tick_seconds=5, area_m2=500)
    assert result is None

def test_divert_selects_safest():
    states = {
        "a": ZoneState(zone_id="a", count=200, area_m2=100, adjacency=["b", "c"]),
        "b": ZoneState(zone_id="b", count=50, area_m2=100, adjacency=["a"]),
        "c": ZoneState(zone_id="c", count=300, area_m2=100, adjacency=["a"]),
    }
    from app.risk import update_state
    for s in states.values():
        update_state(s)
    result = suggest_divert("a", states)
    assert result == "b"

def test_divert_no_safe_zone():
    states = {
        "a": ZoneState(zone_id="a", count=5000, area_m2=100, adjacency=["b"]),
        "b": ZoneState(zone_id="b", count=5000, area_m2=100, adjacency=["a"]),
    }
    from app.risk import update_state
    for s in states.values():
        update_state(s)
    result = suggest_divert("a", states)
    assert result is None
