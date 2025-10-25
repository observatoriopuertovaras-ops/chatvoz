import { CircleMarker, Tooltip } from "react-leaflet";
import { Unit } from "../App";

interface Props {
  units: Unit[];
}

export const UnitsLayer = ({ units }: Props) => {
  return (
    <>
      {units
        .filter((unit) => unit.last_gps)
        .map((unit) => (
          <CircleMarker
            key={`unit-${unit.id}`}
            center={[unit.last_gps!.lat, unit.last_gps!.lng]}
            pathOptions={{ color: "#2563eb" }}
            radius={10}
          >
            <Tooltip direction="top" offset={[0, -8]} opacity={1} permanent>
              {unit.code} · {unit.operational_state}
            </Tooltip>
          </CircleMarker>
        ))}
    </>
  );
};
