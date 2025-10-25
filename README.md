# Emergent CAD

Este repositorio contiene una maqueta funcional para una plataforma CAD (Computer Aided Dispatch) orientada a la Central de Monitoreo Municipal. Incluye un backend FastAPI con SQLite y un frontend React + Vite que visualiza el mapa operativo, lista de incidentes y formularios básicos.

## Estructura del proyecto

- `backend/`: API REST construida con FastAPI.
  - `app/main.py`: puntos finales para usuarios, incidentes, despachos, webhooks de llamadas/GPS y métricas.
  - `app/models.py`: modelos SQLAlchemy que cubren entidades principales (usuarios, incidentes, unidades, despachos, bitácora, evidencias, cámaras, GPS).
  - `app/schemas.py`: esquemas Pydantic para validación y serialización.
  - `app/crud.py`: operaciones de base de datos y cálculo de métricas del dashboard.
  - `requirements.txt`: dependencias del backend.
- `frontend/cad-dashboard/`: interfaz web en React.
  - `src/App.tsx`: layout principal con mapa Leaflet y paneles laterales.
  - `src/components/`: componentes reutilizables (lista/detalle de incidentes, marcador de unidades, cámaras, formulario de llamadas, barra superior).
  - `src/index.css`: estilos principales para lograr un dashboard interactivo.

## Requisitos previos

- Python 3.11+
- Node.js 18+

## Puesta en marcha

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Los datos se almacenan en SQLite (`cad.db`). Puedes precargar catálogos y usuarios mediante llamadas a la API.

### Frontend

```bash
cd frontend/cad-dashboard
npm install
npm run dev
```

La aplicación se conecta al backend en `http://localhost:8000` por defecto. Puedes cambiar la URL creando un archivo `.env` con `VITE_API_BASE`.

## Próximos pasos sugeridos

- Integrar autenticación y control granular de permisos.
- Implementar streaming real para cámaras (ONVIF/RTSP) y WebSockets para notificaciones en vivo.
- Añadir generación de reportes PDF/CSV y exportaciones programadas.
- Completar flujos avanzados (chat interno, bitácoras enriquecidas, SLA configurables, dashboards guardados).
