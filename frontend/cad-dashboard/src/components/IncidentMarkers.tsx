import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { Incident } from "../App";

const statusColors: Record<string, string> = {
  pendiente: "#f97316",
  despachado: "#f59e0b",
  en_ruta: "#38bdf8",
  en_sitio: "#22c55e",
  en_gestion: "#0ea5e9",
  cerrado: "#6b7280",
  cancelado: "#ef4444",
};

const iconCache: Record<string, L.Icon> = {};

const getIcon = (status: string) => {
  if (!iconCache[status]) {
    iconCache[status] = L.divIcon({
      className: "incident-icon",
      html: `<span style="background:${statusColors[status] || "#1e293b"};"></span>`,
    });
  }
  return iconCache[status];
};

interface Props {
  incidents: Incident[];
  onSelect: (id: number) => void;
}

export const IncidentMarkers = ({ incidents, onSelect }: Props) => {
  return (
    <>
      {incidents
        .filter((incident) => incident.location)
        .map((incident) => (
          <Marker
            key={incident.id}
            position={[incident.location!.lat, incident.location!.lng]}
            icon={getIcon(incident.status)}
            eventHandlers={{
              click: () => onSelect(incident.id),
            }}
          >
            <Popup>
              <strong>{incident.folio}</strong>
              <div>{incident.description}</div>
              <div>Prioridad: {incident.priority}</div>
              <div>Estado: {incident.status}</div>
            </Popup>
          </Marker>
        ))}
    </>
  );
};
