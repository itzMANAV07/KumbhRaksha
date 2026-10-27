"""
Pydantic v2 schemas for request/response validation.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


# ── Zone ────────────────────────────────────────────────────────────────────

class ZoneFeatureProperties(BaseModel):
    id: str
    name: str
    area_m2: float = Field(gt=0)
    capacity_assumed: int = Field(gt=0)
    adjacency: list[str] = Field(default_factory=list)

    @field_validator("area_m2")
    @classmethod
    def area_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("area_m2 must be positive")
        return v


class ZoneFeature(BaseModel):
    type: str
    properties: ZoneFeatureProperties
    geometry: dict[str, Any]


class ZoneGeoJSON(BaseModel):
    type: str
    features: list[ZoneFeature]


class ZoneResponse(BaseModel):
    id: str
    name: str
    area_m2: float
    capacity_assumed: int
    adjacency: list[str]
    geometry: dict[str, Any]
    # Runtime state (may be None if simulator not started)
    count: Optional[int] = None
    density: Optional[float] = None
    level: Optional[str] = None
    forecast_minutes: Optional[float] = None
    divert_to: Optional[str] = None


# ── Facility ─────────────────────────────────────────────────────────────────

class FacilitySchema(BaseModel):
    id: str
    name: str
    type: str
    lat: float
    lon: float
    zone_id: Optional[str] = None
    demo: bool = True


class FacilitiesList(BaseModel):
    facilities: list[FacilitySchema]

    @field_validator("facilities")
    @classmethod
    def must_not_be_empty(cls, v):
        if not v:
            raise ValueError("facilities list must not be empty")
        return v


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    chat_id: str
    text: str
    language: str = "en"
    lat: Optional[float] = None
    lon: Optional[float] = None


class ChatResponse(BaseModel):
    text: str
    buttons: Optional[list[str]] = None


# ── SOS ──────────────────────────────────────────────────────────────────────

class SOSRequest(BaseModel):
    chat_id: str
    lat: float
    lon: float


class SOSResponse(BaseModel):
    incident_id: int
    reply: str


# ── Lost & Found ─────────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    type: str  # lost | found
    reporter_chat_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    clothing_color: Optional[str] = None
    clothing_garment: Optional[str] = None
    zone_id: Optional[str] = None


class ReportResponse(BaseModel):
    report_id: int


class MatchResult(BaseModel):
    found_report_id: int
    score: float
    score_breakdown: dict[str, float]
    name: Optional[str]
    age: Optional[int]
    clothing_color: Optional[str]
    clothing_garment: Optional[str]
    zone_id: Optional[str]
    reported_at: datetime


# ── Incidents ────────────────────────────────────────────────────────────────

class IncidentResponse(BaseModel):
    id: int
    chat_id: str
    lat: Optional[float]
    lon: Optional[float]
    nearest_facility_id: Optional[str]
    status: str
    created_at: datetime


# ── Sim control ──────────────────────────────────────────────────────────────

class ScenarioRequest(BaseModel):
    scenario: str


# ── LLM intent (Gemini response) ─────────────────────────────────────────────

class LLMIntentResponse(BaseModel):
    intent: str
    zone_id: Optional[str] = None
    language: Optional[str] = None
