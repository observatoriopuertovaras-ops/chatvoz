from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Emergent CAD", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.get("/users", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@app.post("/incidentes", response_model=schemas.Incident)
def create_incident(incident: schemas.IncidentCreate, db: Session = Depends(get_db)):
    return crud.create_incident(db, incident)


@app.get("/incidentes", response_model=List[schemas.Incident])
def list_incidents(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_incidents(db, skip=skip, limit=limit, status=status, priority=priority)


@app.get("/incidentes/{incident_id}", response_model=schemas.Incident)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = crud.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.patch("/incidentes/{incident_id}", response_model=schemas.Incident)
def update_incident(
    incident_id: int, payload: schemas.IncidentUpdate, db: Session = Depends(get_db)
):
    incident = crud.update_incident(db, incident_id, payload)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.post("/incidentes/{incident_id}/despachos", response_model=schemas.Dispatch)
def create_dispatch(
    incident_id: int, payload: schemas.DispatchCreate, db: Session = Depends(get_db)
):
    return crud.create_dispatch(db, incident_id, payload)


@app.post("/incidentes/{incident_id}/bitacora")
def create_log(
    incident_id: int, payload: schemas.IncidentLogCreate, db: Session = Depends(get_db)
):
    crud.log_action(db, incident_id, payload.user_id, payload.action, payload.detail or "")
    return {"status": "ok"}


@app.post("/incidentes/{incident_id}/evidencias", response_model=schemas.Evidence)
def create_evidence(
    incident_id: int, payload: schemas.EvidenceCreate, db: Session = Depends(get_db)
):
    return crud.add_evidence(db, incident_id, payload)


@app.post("/llamadas", response_model=schemas.Call)
def create_call(payload: schemas.CallCreate, db: Session = Depends(get_db)):
    return crud.create_call(db, payload)


@app.post("/webhooks/call")
def webhook_call(payload: schemas.CallCreate, db: Session = Depends(get_db)):
    call = crud.create_call(db, payload)
    return {"id": call.id, "status": "registered"}


@app.post("/webhooks/gps")
def webhook_gps(payload: schemas.GPSPing, db: Session = Depends(get_db)):
    gps = crud.record_gps(db, payload)
    return {"id": gps.id, "status": "registered"}


@app.get("/dashboard", response_model=schemas.DashboardResponse)
def dashboard(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    start = start or now - timedelta(days=1)
    end = end or now
    return crud.get_dashboard_metrics(db, start, end)


@app.post("/unidades", response_model=schemas.Unit)
def upsert_unit(payload: schemas.UnitCreate, db: Session = Depends(get_db)):
    return crud.upsert_unit(db, payload)


@app.get("/unidades", response_model=List[schemas.Unit])
def list_units(db: Session = Depends(get_db)):
    return db.query(models.Unit).all()


@app.post("/camaras", response_model=schemas.Camera)
def create_camera(payload: schemas.CameraCreate, db: Session = Depends(get_db)):
    camera = models.Camera(**payload.dict())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@app.get("/camaras", response_model=List[schemas.Camera])
def list_cameras(db: Session = Depends(get_db)):
    return db.query(models.Camera).all()


@app.get("/export")
def export_data(format: str = "csv"):
    return {"format": format, "url": f"/exports/mock.{format}"}
