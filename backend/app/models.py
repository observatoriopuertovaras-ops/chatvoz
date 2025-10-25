from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, nullable=False)
    shift = Column(String, nullable=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    zone = relationship("Zone", back_populates="users")
    unit = relationship("Unit", uselist=False, back_populates="user")


class Zone(Base, TimestampMixin):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    geojson = Column(JSON, nullable=True)

    users = relationship("User", back_populates="zone")
    incidents = relationship("Incident", back_populates="zone")


class Unit(Base, TimestampMixin):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    operational_state = Column(String, default="disponible")
    last_gps = Column(JSON, nullable=True)

    user = relationship("User", back_populates="unit")
    gps_positions = relationship("GPSPosition", back_populates="unit")
    dispatches = relationship("Dispatch", back_populates="unit")


class CatalogItem(Base, TimestampMixin):
    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=True)


class Call(Base, TimestampMixin):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    caller_id = Column(String, nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    motive_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=True)
    description = Column(Text, nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    recording_url = Column(String, nullable=True)

    operator = relationship("User")
    incident = relationship("Incident", back_populates="calls")


class Camera(Base, TimestampMixin):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    stream_url = Column(String, nullable=True)
    coverage = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    motive_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=True)
    description = Column(Text, nullable=True)
    priority = Column(String, default="media")
    status = Column(String, default="pendiente")
    location = Column(JSON, nullable=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    suggested_camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)

    creator = relationship("User")
    zone = relationship("Zone", back_populates="incidents")
    calls = relationship("Call", back_populates="incident")
    dispatches = relationship("Dispatch", back_populates="incident")
    logs = relationship("IncidentLog", back_populates="incident")
    evidences = relationship("Evidence", back_populates="incident")


class Dispatch(Base, TimestampMixin):
    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    unit_status = Column(String, default="despachado")
    eta = Column(Integer, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    en_route_at = Column(DateTime, nullable=True)
    on_site_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="dispatches")
    unit = relationship("Unit", back_populates="dispatches")


class IncidentLog(Base, TimestampMixin):
    __tablename__ = "incident_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="logs")
    user = relationship("User")


class Evidence(Base, TimestampMixin):
    __tablename__ = "evidences"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="evidences")
    author = relationship("User")


class GPSPosition(Base, TimestampMixin):
    __tablename__ = "gps_positions"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    speed = Column(Integer, default=0)
    heading = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    unit = relationship("Unit", back_populates="gps_positions")
