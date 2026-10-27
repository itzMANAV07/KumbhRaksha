"""Tests for SOS utilities (M6)."""
import pytest
from app.sos import is_sos, haversine_km, find_nearest_facility, build_sos_reply

FACILITIES = [
    {"id": "f1", "name": "First Aid Post A", "lat": 29.9256, "lon": 78.1642},
    {"id": "f2", "name": "Police Post 1",    "lat": 29.9300, "lon": 78.1700},
]

def test_is_sos_english():
    assert is_sos("help") is True
    assert is_sos("I need help!") is True

def test_is_sos_hindi():
    assert is_sos("बचाओ") is True

def test_is_sos_false():
    assert is_sos("hello how are you") is False

def test_haversine_same_point():
    assert haversine_km(29.9, 78.1, 29.9, 78.1) == pytest.approx(0.0, abs=1e-6)

def test_haversine_known():
    # Rough check: two points ~1 km apart
    d = haversine_km(29.9256, 78.1642, 29.9300, 78.1700)
    assert 0.5 < d < 2.0

def test_nearest_facility():
    nearest = find_nearest_facility(29.9260, 78.1645, FACILITIES)
    assert nearest["id"] == "f1"

def test_build_sos_reply():
    reply = build_sos_reply(FACILITIES[0], 29.9260, 78.1645)
    assert "First Aid Post A" in reply
    assert "maps.google.com" in reply

def test_no_facilities():
    assert find_nearest_facility(0, 0, []) is None
