"""Tests for lost-and-found matching (M5)."""
import pytest
from datetime import datetime, timedelta
from app.matching import clothing_match, age_match, location_proximity, time_proximity, score_pair, find_matches

ADJ = {"zone_a": ["zone_b"], "zone_b": ["zone_a"]}

def make_report(**kwargs):
    base = {
        "id": 1, "type": "found", "reporter_chat_id": "x",
        "name": None, "age": None, "clothing_color": None,
        "clothing_garment": None, "zone_id": None,
        "reported_at": datetime.utcnow(), "status": "open",
    }
    base.update(kwargs)
    return base

def test_clothing_exact_match():
    assert clothing_match("red", "kurta", "red", "kurta") == 1.0

def test_clothing_colour_only():
    assert clothing_match("red", "kurta", "red", "saree") == 0.5

def test_clothing_no_match():
    assert clothing_match("red", "kurta", "blue", "saree") == 0.0

def test_age_exact():
    assert age_match(8, 9) == 1.0

def test_age_far():
    assert age_match(8, 20) == pytest.approx(0.0)

def test_location_same_zone():
    assert location_proximity("zone_a", "zone_a", ADJ) == 1.0

def test_location_adjacent():
    assert location_proximity("zone_a", "zone_b", ADJ) == 0.5

def test_time_within_hour():
    now = datetime.utcnow()
    assert time_proximity(now, now) == 1.0

def test_score_good_pair():
    lost = make_report(type="lost", age=8, clothing_color="red",
                       clothing_garment="kurta", zone_id="zone_a")
    found = make_report(type="found", age=9, clothing_color="red",
                        clothing_garment="kurta", zone_id="zone_a")
    score, _ = score_pair(lost, found, ADJ)
    assert score >= 0.6

def test_score_bad_pair():
    lost = make_report(type="lost", age=8, clothing_color="red",
                       clothing_garment="kurta", zone_id="zone_a")
    found = make_report(type="found", age=60, clothing_color="blue",
                        clothing_garment="saree", zone_id="zone_b",
                        reported_at=datetime.utcnow() - timedelta(hours=10))
    score, _ = score_pair(lost, found, ADJ)
    assert score < 0.6
