import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { Camera } from "../App";

const cameraIcon = L.divIcon({
  className: "camera-icon",
  html: '<span class="camera-marker">📹</span>',
});

interface Props {
  cameras: Camera[];
}

export const CamerasLayer = ({ cameras }: Props) => {
  return (
    <>
      {cameras.map((camera) => (
        <Marker key={camera.id} position={[camera.latitude, camera.longitude]} icon={cameraIcon}>
          <Popup>
            <strong>{camera.name}</strong>
            {camera.stream_url ? (
              <div>
                <em>Stream:</em>
                <br />
                <code>{camera.stream_url}</code>
              </div>
            ) : (
              <p>Stream simulado</p>
            )}
          </Popup>
        </Marker>
      ))}
    </>
  );
};
