"""
SOS handling: nearest facility lookup and incident creation.
Implements AGENTS.md Section 7.6.
NOTE: This module must NEVER call the LLM.
"""
from __future__ import annotations
import math
from typing import Optional

import re

SOS_KEYWORDS_EN = {"help", "sos", "emergency"}
SOS_KEYWORDS_HI = {"बचाओ", "मदद", "आपातकाल", "bachao", "madad", "aapatkal"}
SOS_KEYWORDS_REGIONAL = {
    # Bengali
    "জরুরি", "বাঁচাও",
    # Marathi
    "मदत", "आपत्कालीन", "वाचवा",
    # Gujarati
    "કટોકટી", "બચાવો",
    # Telugu
    "అత్యవసర", "రక్షించండి",
    # Tamil
    "அவசர", "காப்பாற்று", "காப்பாற்றுங்கள்",
}
ALL_SOS_KEYWORDS = SOS_KEYWORDS_EN | SOS_KEYWORDS_HI | SOS_KEYWORDS_REGIONAL


def is_sos(text: str) -> bool:
    """Return True if the message contains an SOS keyword."""
    lower = text.lower()
    words = set(re.findall(r"[\w\u0900-\u0DFF]+", lower))
    lowered_keywords = {k.lower() for k in ALL_SOS_KEYWORDS}
    if words & lowered_keywords:
        return True
    return any(k.lower() in lower for k in lowered_keywords)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_facility(
    lat: float,
    lon: float,
    facilities: list[dict],
) -> Optional[dict]:
    """Return the facility dict closest to (lat, lon)."""
    if not facilities:
        return None
    return min(
        facilities,
        key=lambda f: haversine_km(lat, lon, f["lat"], f["lon"]),
    )


def build_sos_reply(facility: Optional[dict], lat: float, lon: float) -> str:
    """Build the SOS reply message (no LLM, template only)."""
    if facility is None:
        return (
            "SOS received. No facility data available. "
            "Please contact authorities immediately."
        )
    dist = haversine_km(lat, lon, facility["lat"], facility["lon"])
    maps_link = f"https://maps.google.com/?q={facility['lat']},{facility['lon']}"
    return (
        f"SOS received. Nearest facility: {facility['name']} "
        f"({dist:.2f} km away). {maps_link}"
    )
