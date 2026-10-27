"""
SQLAlchemy ORM models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
import json

from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    area_m2: Mapped[float] = mapped_column(Float, nullable=False)
    capacity_assumed: Mapped[int] = mapped_column(Integer, nullable=False)
    # Store adjacency as JSON list
    adjacency_json: Mapped[str] = mapped_column(Text, default="[]")
    # Store GeoJSON geometry as text
    geometry_json: Mapped[str] = mapped_column(Text, nullable=False)

    @property
    def adjacency(self):
        return json.loads(self.adjacency_json)

    @adjacency.setter
    def adjacency(self, value):
        self.adjacency_json = json.dumps(value)

    @property
    def geometry(self):
        return json.loads(self.geometry_json)

    @geometry.setter
    def geometry(self, value):
        self.geometry_json = json.dumps(value)


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    zone_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    demo: Mapped[bool] = mapped_column(Boolean, default=True)


class LostReport(Base):
    __tablename__ = "lost_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # lost | found
    reporter_chat_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    clothing_color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    clothing_garment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    zone_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String, default="open")  # open | resolved


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nearest_facility_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String, nullable=False)
    zone_id: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_alerted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
