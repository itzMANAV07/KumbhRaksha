"""
Lost-and-found scoring.
Implements AGENTS.md Section 7.5.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from app.schemas import MatchResult


def clothing_match(
    lost_color: Optional[str], lost_garment: Optional[str],
    found_color: Optional[str], found_garment: Optional[str],
) -> float:
    if not lost_color or not found_color:
        return 0.0
    color_match = lost_color.lower().strip() == found_color.lower().strip()
    garment_match = (
        lost_garment and found_garment
        and lost_garment.lower().strip() == found_garment.lower().strip()
    )
    if color_match and garment_match:
        return 1.0
    if color_match:
        return 0.5
    return 0.0


def age_match(lost_age: Optional[int], found_age: Optional[int]) -> float:
    if lost_age is None or found_age is None:
        return 0.0
    diff = abs(lost_age - found_age)
    if diff <= 2:
        return 1.0
    return max(0.0, 1.0 - diff / 10.0)


def location_proximity(
    lost_zone: Optional[str],
    found_zone: Optional[str],
    adjacency_map: dict[str, list[str]],
) -> float:
    if not lost_zone or not found_zone:
        return 0.0
    if lost_zone == found_zone:
        return 1.0
    if found_zone in adjacency_map.get(lost_zone, []):
        return 0.5
    return 0.0


def time_proximity(lost_at: datetime, found_at: datetime) -> float:
    hours = abs((lost_at - found_at).total_seconds()) / 3600
    if hours <= 1.0:
        return 1.0
    return max(0.0, 1.0 - hours / 6.0)


def score_pair(
    lost: dict,
    found: dict,
    adjacency_map: dict[str, list[str]],
) -> tuple[float, dict[str, float]]:
    cm = clothing_match(
        lost.get("clothing_color"), lost.get("clothing_garment"),
        found.get("clothing_color"), found.get("clothing_garment"),
    )
    am = age_match(lost.get("age"), found.get("age"))
    lp = location_proximity(lost.get("zone_id"), found.get("zone_id"), adjacency_map)
    tp = time_proximity(
        lost.get("reported_at", datetime.utcnow()),
        found.get("reported_at", datetime.utcnow()),
    )
    total = 0.4 * cm + 0.3 * am + 0.2 * lp + 0.1 * tp
    breakdown = {
        "clothing_match": round(cm, 3),
        "age_match": round(am, 3),
        "location_proximity": round(lp, 3),
        "time_proximity": round(tp, 3),
    }
    return round(total, 4), breakdown


MATCH_THRESHOLD = 0.6
TOP_K = 3


def find_matches(
    lost_report: dict,
    found_reports: list[dict],
    adjacency_map: dict[str, list[str]],
) -> list[MatchResult]:
    """Score all found reports against a lost report and return top-K."""
    results = []
    for found in found_reports:
        if found.get("status") != "open":
            continue
        score, breakdown = score_pair(lost_report, found, adjacency_map)
        results.append(
            MatchResult(
                found_report_id=found["id"],
                score=score,
                score_breakdown=breakdown,
                name=found.get("name"),
                age=found.get("age"),
                clothing_color=found.get("clothing_color"),
                clothing_garment=found.get("clothing_garment"),
                zone_id=found.get("zone_id"),
                reported_at=found.get("reported_at", datetime.utcnow()),
            )
        )
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:TOP_K]
