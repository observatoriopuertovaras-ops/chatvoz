import { Incident } from "../App";

interface Props {
  incident: Incident | null;
}

export const IncidentDetail = ({ incident }: Props) => {
  if (!incident) {
    return (
      <div className="panel">
        <h2>Selecciona un incidente</h2>
        <p>Explora el mapa o la lista para ver el detalle.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <header className="panel-header">
        <h2>{incident.folio}</h2>
        <span className={`badge priority-${incident.priority}`}>{incident.priority}</span>
      </header>
      <section className="detail-section">
        <h3>Resumen</h3>
        <p>{incident.description || "Sin descripción disponible"}</p>
        <dl>
          <div>
            <dt>Estado</dt>
            <dd>{incident.status}</dd>
          </div>
          <div>
            <dt>Creado</dt>
            <dd>{new Date(incident.timestamp).toLocaleString()}</dd>
          </div>
          {incident.location && (
            <div>
              <dt>Dirección</dt>
              <dd>{incident.location.address || `${incident.location.lat}, ${incident.location.lng}`}</dd>
            </div>
          )}
        </dl>
      </section>
      <section className="detail-section">
        <h3>Bitácora</h3>
        <p>Las entradas de bitácora aparecerán aquí en futuras iteraciones.</p>
      </section>
      <section className="detail-section">
        <h3>Evidencias</h3>
        <p>No hay evidencias adjuntas.</p>
      </section>
    </div>
  );
};
