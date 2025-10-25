import { Incident } from "../App";

interface Props {
  incidents: Incident[];
  loading: boolean;
  onSelect: (id: number) => void;
  selectedId: number | null;
}

const statusLabels: Record<string, string> = {
  pendiente: "Pendiente",
  despachado: "Despachado",
  en_ruta: "En ruta",
  en_sitio: "En sitio",
  en_gestion: "En gestión",
  cerrado: "Cerrado",
  cancelado: "Cancelado",
};

export const IncidentList = ({ incidents, loading, onSelect, selectedId }: Props) => {
  if (loading) {
    return <div className="panel">Cargando incidentes…</div>;
  }

  return (
    <div className="panel">
      <header className="panel-header">
        <h2>Incidentes activos</h2>
        <span>{incidents.length} casos</span>
      </header>
      <ul className="incident-list">
        {incidents.map((incident) => {
          const isSelected = incident.id === selectedId;
          return (
            <li
              key={incident.id}
              className={isSelected ? "incident-card selected" : "incident-card"}
              onClick={() => onSelect(incident.id)}
            >
              <div className="incident-card__header">
                <strong>{incident.folio}</strong>
                <span className={`badge priority-${incident.priority}`}>{incident.priority}</span>
              </div>
              <p>{incident.description || "Sin descripción"}</p>
              <footer>
                <span className={`status status-${incident.status}`}>{statusLabels[incident.status] || incident.status}</span>
                <time>{new Date(incident.timestamp).toLocaleTimeString()}</time>
              </footer>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
