from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None
    reference: Optional[str] = None


class UserBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    shift: Optional[str] = None
    zone_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: Optional[str] = Field(None, description="Password placeholder for future use")


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class CatalogItem(BaseModel):
    id: int
    type: str
    name: str
    value: Optional[str] = None

    class Config:
        orm_mode = True


class CallBase(BaseModel):
    caller_id: str
    operator_id: int
    motive_id: Optional[int] = None
    description: Optional[str] = None
    recording_url: Optional[str] = None
    incident_id: Optional[int] = None


class CallCreate(CallBase):
    pass


class Call(CallBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class EvidenceBase(BaseModel):
    type: str
    url: str
    thumbnail_url: Optional[str] = None
    author_id: int


class EvidenceCreate(EvidenceBase):
    pass


class Evidence(EvidenceBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class DispatchBase(BaseModel):
    unit_id: int
    unit_status: str
    eta: Optional[int] = None


class DispatchCreate(DispatchBase):
    pass


class Dispatch(DispatchBase):
    id: int
    incident_id: int
    acknowledged_at: Optional[datetime]
    en_route_at: Optional[datetime]
    on_site_at: Optional[datetime]
    closed_at: Optional[datetime]

    class Config:
        orm_mode = True


class IncidentBase(BaseModel):
    motive_id: Optional[int] = None
    description: Optional[str] = None
    priority: str = "media"
    status: str = "pendiente"
    location: Optional[Location] = None
    zone_id: Optional[int] = None
    suggested_camera_id: Optional[int] = None


class IncidentCreate(IncidentBase):
    creator_id: int


class IncidentUpdate(BaseModel):
    motive_id: Optional[int] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    location: Optional[Location] = None
    zone_id: Optional[int] = None
    suggested_camera_id: Optional[int] = None


class Incident(IncidentBase):
    id: int
    folio: str
    timestamp: datetime
    creator_id: int
    dispatches: List[Dispatch] = Field(default_factory=list)
    evidences: List[Evidence] = Field(default_factory=list)

    class Config:
        orm_mode = True


class IncidentLogBase(BaseModel):
    user_id: int
    action: str
    detail: Optional[str] = None


class IncidentLogCreate(IncidentLogBase):
    pass


class IncidentLog(IncidentLogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class GPSPing(BaseModel):
    unit_id: int
    lat: float
    lng: float
    speed: Optional[int] = 0
    heading: Optional[int] = 0
    timestamp: Optional[datetime] = None


class KPIResponse(BaseModel):
    created: int
    attended: int
    closed: int
    avg_dispatch_minutes: Optional[float]
    avg_arrival_minutes: Optional[float]
    avg_resolution_minutes: Optional[float]


class DashboardResponse(BaseModel):
    kpis: KPIResponse
    top_motives: List[dict]
    top_zones: List[dict]
    time_series: List[dict]
    heatmap: List[dict]
    stacked_status_priority: List[dict]
    performance: List[dict]


class CameraBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    stream_url: Optional[str] = None
    coverage: Optional[int] = 100
    is_active: bool = True


class CameraCreate(CameraBase):
    pass


class Camera(CameraBase):
    id: int

    class Config:
        orm_mode = True


class UnitBase(BaseModel):
    type: str
    code: str
    user_id: Optional[int] = None
    operational_state: str = "disponible"


class UnitCreate(UnitBase):
    pass


class Unit(UnitBase):
    id: int
    last_gps: Optional[dict] = None

    class Config:
        orm_mode = True
