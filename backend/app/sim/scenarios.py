"""
Named simulator scenarios.
Each scenario defines per-zone delta functions: (count, tick_num) -> new_count.
Zone IDs MUST match those in data/zones.geojson.
"""
from __future__ import annotations
from typing import Callable

DeltaFn = Callable[[int, int], int]


def _clamp(v: int, lo: int = 0, hi: int = 1_000_000) -> int:
    return max(lo, min(hi, v))


# ── Scenario: calm (idle) ─────────────────────────────────────────────────────
# Small random-ish drift to keep numbers alive

def _calm_drift(count: int, tick: int) -> int:
    # Gentle sine-like drift using tick parity
    delta = 5 if tick % 4 < 2 else -3
    return _clamp(count + delta, lo=10)


CALM: dict[str, DeltaFn] = {
    "har-ki-pauri":      _calm_drift,
    "brahmakund":        _calm_drift,
    "ganga-ghat-upper":  _calm_drift,
    "subhash-ghat":      _calm_drift,
    "moti-bazaar":       _calm_drift,
    "railway-road":      _calm_drift,
}


# ── Scenario: peak_snan_morning ───────────────────────────────────────────────
# Har Ki Pauri main ghat fills fast; surrounding zones fill more slowly.

def _hkp_main_delta(count: int, tick: int) -> int:
    return _clamp(count + 200)


def _hkp_upper_delta(count: int, tick: int) -> int:
    return _clamp(count + 90)


def _subhash_ghat_delta(count: int, tick: int) -> int:
    return _clamp(count + 60)


def _approach_north_delta(count: int, tick: int) -> int:
    return _clamp(count + 70)


def _approach_south_delta(count: int, tick: int) -> int:
    return _clamp(count + 70)


def _other_moderate_delta(count: int, tick: int) -> int:
    return _clamp(count + 30)


PEAK_SNAN_MORNING: dict[str, DeltaFn] = {
    "har-ki-pauri":      _hkp_main_delta,
    "ganga-ghat-upper":  _hkp_upper_delta,
    "subhash-ghat":      _subhash_ghat_delta,
    "moti-bazaar":       _approach_south_delta,
    "railway-road":      _approach_north_delta,
    "brahmakund":        _other_moderate_delta,
}


# ── Scenario: evening_aarti ───────────────────────────────────────────────────

def _evening_hkp_delta(count: int, tick: int) -> int:
    return _clamp(count + 140)


def _evening_adj_delta(count: int, tick: int) -> int:
    return _clamp(count + 50)


EVENING_AARTI: dict[str, DeltaFn] = {
    "har-ki-pauri":      _evening_hkp_delta,
    "ganga-ghat-upper":  _evening_adj_delta,
    "subhash-ghat":      _evening_adj_delta,
    "moti-bazaar":       _evening_adj_delta,
    "railway-road":      _evening_adj_delta,
    "brahmakund":        _evening_adj_delta,
}


# ── Scenario: stampede_risk ───────────────────────────────────────────────────
# Stress test: all zones fill rapidly to force RED levels quickly

def _stampede_delta(count: int, tick: int) -> int:
    return _clamp(count + 400)


STAMPEDE_RISK: dict[str, DeltaFn] = {
    "har-ki-pauri":      _stampede_delta,
    "brahmakund":        _stampede_delta,
    "ganga-ghat-upper":  _stampede_delta,
    "subhash-ghat":      _stampede_delta,
    "moti-bazaar":       _stampede_delta,
    "railway-road":      _stampede_delta,
}


# ── Registry ──────────────────────────────────────────────────────────────────

SCENARIOS: dict[str, dict[str, DeltaFn]] = {
    "calm":               CALM,
    "peak_snan_morning":  PEAK_SNAN_MORNING,
    "evening_aarti":      EVENING_AARTI,
    "stampede_risk":      STAMPEDE_RISK,
}

DEFAULT_SCENARIO = "calm"
