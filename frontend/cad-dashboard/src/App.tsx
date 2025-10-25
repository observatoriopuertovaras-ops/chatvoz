import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { MapContainer, TileLayer } from "react-leaflet";
import { IncidentMarkers } from "./components/IncidentMarkers";
import { UnitsLayer } from "./components/UnitsLayer";
import { CamerasLayer } from "./components/CamerasLayer";
import { IncidentList } from "./components/IncidentList";
import { IncidentDetail } from "./components/IncidentDetail";
import { DashboardButtonBar } from "./components/DashboardButtonBar";
import { NewCallForm } from "./components/NewCallForm";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export interface Incident {
  id: number;
  folio: string;
  timestamp: string;
  priority: string;
  status: string;
  description?: string;
  location?: { lat: number; lng: number; address?: string };
}

export interface Unit {
  id: number;
  code: string;
  type: string;
  operational_state: string;
  last_gps?: { lat: number; lng: number };
}

export interface Camera {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  stream_url?: string;
}

const fetchIncidents = async () => {
  const { data } = await axios.get<Incident[]>(`${API_BASE}/incidentes`);
  return data;
};

const fetchUnits = async () => {
  const { data } = await axios.get<Unit[]>(`${API_BASE}/unidades`);
  return data;
};

const fetchCameras = async () => {
  const { data } = await axios.get<Camera[]>(`${API_BASE}/camaras`);
  return data;
};

function App() {
  const [selectedIncidentId, setSelectedIncidentId] = useState<number | null>(null);

  const {
    data: incidents,
    isLoading: loadingIncidents,
    refetch: refetchIncidents,
  } = useQuery({ queryKey: ["incidentes"], queryFn: fetchIncidents, refetchInterval: 15000 });

  const { data: units } = useQuery({ queryKey: ["unidades"], queryFn: fetchUnits, refetchInterval: 10000 });
  const { data: cameras } = useQuery({ queryKey: ["camaras"], queryFn: fetchCameras, refetchInterval: 60000 });

  const selectedIncident = useMemo(
    () => incidents?.find((incident) => incident.id === selectedIncidentId) ?? null,
    [incidents, selectedIncidentId]
  );

  return (
    <div className="app-shell">
      <DashboardButtonBar onRefresh={refetchIncidents} />
      <div className="content">
        <aside className="left-panel">
          <IncidentList
            incidents={incidents || []}
            loading={loadingIncidents}
            onSelect={setSelectedIncidentId}
            selectedId={selectedIncidentId}
          />
          <NewCallForm />
        </aside>
        <main className="map-area">
          <MapContainer center={[-34.6037, -58.3816]} zoom={13} scrollWheelZoom style={{ height: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <IncidentMarkers incidents={incidents || []} onSelect={setSelectedIncidentId} />
            <UnitsLayer units={units || []} />
            <CamerasLayer cameras={cameras || []} />
          </MapContainer>
        </main>
        <aside className="right-panel">
          <IncidentDetail incident={selectedIncident} />
        </aside>
      </div>
    </div>
  );
}

export default App;
