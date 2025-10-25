from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        shift=user.shift,
        zone_id=user.zone_id,
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


def create_incident(db: Session, incident: schemas.IncidentCreate) -> models.Incident:
    folio = f"INC-{int(datetime.utcnow().timestamp())}"
    db_incident = models.Incident(
        folio=folio,
        creator_id=incident.creator_id,
        motive_id=incident.motive_id,
        description=incident.description,
        priority=incident.priority,
        status=incident.status,
        location=incident.location.dict() if incident.location else None,
        zone_id=incident.zone_id,
        suggested_camera_id=incident.suggested_camera_id,
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident


def get_incidents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[models.Incident]:
    query = db.query(models.Incident)
    if status:
        query = query.filter(models.Incident.status == status)
    if priority:
        query = query.filter(models.Incident.priority == priority)
    return query.order_by(models.Incident.timestamp.desc()).offset(skip).limit(limit).all()


def get_incident(db: Session, incident_id: int) -> Optional[models.Incident]:
    return db.query(models.Incident).filter(models.Incident.id == incident_id).first()


def update_incident(
    db: Session, incident_id: int, incident_update: schemas.IncidentUpdate
) -> Optional[models.Incident]:
    db_incident = get_incident(db, incident_id)
    if not db_incident:
        return None
    for key, value in incident_update.dict(exclude_unset=True).items():
        if key == "location" and value is not None:
            setattr(db_incident, key, value.dict())
        else:
            setattr(db_incident, key, value)
    db.commit()
    db.refresh(db_incident)
    return db_incident


def create_dispatch(
    db: Session, incident_id: int, payload: schemas.DispatchCreate
) -> models.Dispatch:
    dispatch = models.Dispatch(
        incident_id=incident_id,
        unit_id=payload.unit_id,
        unit_status=payload.unit_status,
        eta=payload.eta,
    )
    db.add(dispatch)
    db.flush()
    unit = db.query(models.Unit).filter(models.Unit.id == payload.unit_id).first()
    actor_id = unit.user_id if unit and unit.user_id else 0
    log = models.IncidentLog(
        incident_id=incident_id,
        user_id=actor_id,
        action="dispatch_created",
        detail=f"Unidad {payload.unit_id} asignada",
    )
    db.add(log)
    db.commit()
    db.refresh(dispatch)
    return dispatch


def log_action(db: Session, incident_id: int, user_id: int, action: str, detail: str) -> None:
    log = models.IncidentLog(
        incident_id=incident_id,
        user_id=user_id,
        action=action,
        detail=detail,
    )
    db.add(log)
    db.commit()


def add_evidence(
    db: Session, incident_id: int, payload: schemas.EvidenceCreate
) -> models.Evidence:
    evidence = models.Evidence(
        incident_id=incident_id,
        type=payload.type,
        url=payload.url,
        thumbnail_url=payload.thumbnail_url,
        author_id=payload.author_id,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def create_call(db: Session, payload: schemas.CallCreate) -> models.Call:
    call = models.Call(
        caller_id=payload.caller_id,
        operator_id=payload.operator_id,
        motive_id=payload.motive_id,
        description=payload.description,
        recording_url=payload.recording_url,
        incident_id=payload.incident_id,
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


def upsert_unit(db: Session, payload: schemas.UnitCreate) -> models.Unit:
    unit = db.query(models.Unit).filter(models.Unit.code == payload.code).first()
    if unit:
        for key, value in payload.dict(exclude_unset=True).items():
            setattr(unit, key, value)
    else:
        unit = models.Unit(**payload.dict())
        db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


def record_gps(db: Session, payload: schemas.GPSPing) -> models.GPSPosition:
    unit = db.query(models.Unit).filter(models.Unit.id == payload.unit_id).first()
    if not unit:
        raise ValueError("Unit not found")
    gps = models.GPSPosition(
        unit_id=payload.unit_id,
        lat=payload.lat,
        lng=payload.lng,
        speed=payload.speed or 0,
        heading=payload.heading or 0,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    unit.last_gps = {
        "lat": payload.lat,
        "lng": payload.lng,
        "speed": payload.speed,
        "heading": payload.heading,
        "timestamp": (payload.timestamp or datetime.utcnow()).isoformat(),
    }
    db.add(gps)
    db.commit()
    db.refresh(gps)
    return gps


def get_dashboard_metrics(db: Session, start: datetime, end: datetime) -> schemas.DashboardResponse:
    incidents = (
        db.query(models.Incident)
        .filter(models.Incident.timestamp >= start, models.Incident.timestamp <= end)
        .all()
    )
    created = len(incidents)
    attended = len([i for i in incidents if i.status not in {"pendiente"}])
    closed = len([i for i in incidents if i.status == "cerrado"])

    def avg_delta(start_attr: str, end_attr: str) -> Optional[float]:
        deltas: List[float] = []
        for incident in incidents:
            dispatch = next(iter(incident.dispatches or []), None)
            if dispatch:
                start_ts = getattr(dispatch, start_attr)
                end_ts = getattr(dispatch, end_attr)
                if start_ts and end_ts:
                    deltas.append((end_ts - start_ts).total_seconds() / 60)
        if not deltas:
            return None
        return round(sum(deltas) / len(deltas), 2)

    avg_dispatch = avg_delta("created_at", "acknowledged_at")
    avg_arrival = avg_delta("acknowledged_at", "on_site_at")
    avg_resolution = avg_delta("created_at", "closed_at")

    top_motives = (
        db.query(models.CatalogItem.name, func.count(models.Incident.id))
        .join(models.Incident, models.Incident.motive_id == models.CatalogItem.id)
        .filter(models.Incident.timestamp >= start, models.Incident.timestamp <= end)
        .group_by(models.CatalogItem.name)
        .order_by(func.count(models.Incident.id).desc())
        .limit(5)
        .all()
    )
    top_zones = (
        db.query(models.Zone.name, func.count(models.Incident.id))
        .join(models.Incident, models.Incident.zone_id == models.Zone.id)
        .filter(models.Incident.timestamp >= start, models.Incident.timestamp <= end)
        .group_by(models.Zone.name)
        .order_by(func.count(models.Incident.id).desc())
        .limit(5)
        .all()
    )

    time_series = [
        {"timestamp": incident.timestamp.isoformat(), "status": incident.status}
        for incident in incidents
    ]

    heatmap = [
        {
            "lat": incident.location.get("lat") if incident.location else None,
            "lng": incident.location.get("lng") if incident.location else None,
            "status": incident.status,
        }
        for incident in incidents
        if incident.location
    ]

    stacked = {}
    for incident in incidents:
        key = (incident.status, incident.priority)
        stacked[key] = stacked.get(key, 0) + 1
    stacked_status_priority = [
        {"status": status, "priority": priority, "count": count}
        for (status, priority), count in stacked.items()
    ]

    performance = []
    for incident in incidents:
        for dispatch in incident.dispatches:
            performance.append(
                {
                    "unit_id": dispatch.unit_id,
                    "incident": incident.folio,
                    "status": dispatch.unit_status,
                    "closed_at": dispatch.closed_at.isoformat() if dispatch.closed_at else None,
                }
            )

    return schemas.DashboardResponse(
        kpis=schemas.KPIResponse(
            created=created,
            attended=attended,
            closed=closed,
            avg_dispatch_minutes=avg_dispatch,
            avg_arrival_minutes=avg_arrival,
            avg_resolution_minutes=avg_resolution,
        ),
        top_motives=[{"name": name, "count": count} for name, count in top_motives],
        top_zones=[{"name": name, "count": count} for name, count in top_zones],
        time_series=time_series,
        heatmap=heatmap,
        stacked_status_priority=stacked_status_priority,
        performance=performance,
    )
