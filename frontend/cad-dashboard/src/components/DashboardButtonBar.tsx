interface Props {
  onRefresh: () => void;
}

export const DashboardButtonBar = ({ onRefresh }: Props) => {
  return (
    <header className="top-bar">
      <div className="top-bar__left">
        <input type="search" placeholder="Buscar folio, dirección o inspector" />
        <input type="datetime-local" />
        <input type="datetime-local" />
      </div>
      <div className="top-bar__actions">
        <button onClick={onRefresh}>Actualizar</button>
        <button>Dashboard</button>
        <button>Reportes</button>
      </div>
    </header>
  );
};
