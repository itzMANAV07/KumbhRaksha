/**
 * ZoneMap : Leaflet map with zone polygons colored by risk level.
 * Uses react-leaflet v5 with TypeScript.
 * SOS incidents are rendered as pulsing red circle markers.
 */
import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polygon,
  Tooltip,
  CircleMarker,
  useMap,
} from "react-leaflet";
import type { LatLngExpression, LatLngBoundsExpression } from "leaflet";
import "leaflet/dist/leaflet.css";
import type { ZoneResponse } from "../api/client";

const KUMBH_CENTER: LatLngExpression = [29.9248, 78.0050];
const KUMBH_BOUNDS: LatLngBoundsExpression = [
  [29.9160, 77.9940],
  [29.9330, 78.0180],
];

const LEVEL_COLORS: Record<string, { fill: string; stroke: string }> = {
  green: { fill: "#00ff88", stroke: "#00cc6a" },
  yellow: { fill: "#ffde00", stroke: "#e6c700" },
  orange: { fill: "#ff7700", stroke: "#e66a00" },
  red: { fill: "#ff2244", stroke: "#e61a37" },
  unknown: { fill: "#475569", stroke: "#334155" },
};

interface Facility {
  id: string;
  name: string;
  type: string;
  lat: number;
  lon: number;
}

export interface Incident {
  id: number;
  lat: number;
  lon: number;
  facility_name?: string | null;
  status: string;
  created_at: string;
}

interface Props {
  zones: ZoneResponse[];
  facilities?: Facility[];
  incidents?: Incident[];
  selectedZoneId?: string | null;
  onZoneClick?: (zoneId: string) => void;
}

// GeoJSON polygon coordinates are [lon, lat]; Leaflet uses [lat, lon]
function toLatLng(coords: number[][]): LatLngExpression[] {
  return coords.map(([lon, lat]) => [lat, lon] as LatLngExpression);
}

function FlyToSelected({
  zones,
  selectedZoneId,
}: {
  zones: ZoneResponse[];
  selectedZoneId?: string | null;
}) {
  const map = useMap();
  useEffect(() => {
    if (!selectedZoneId) return;
    const zone = zones.find((z) => z.id === selectedZoneId);
    if (!zone || zone.geometry.type !== "Polygon") return;
    const coords = (zone.geometry as GeoJSON.Polygon).coordinates[0];
    const latlngs = toLatLng(coords);
    if (latlngs.length > 0) {
      const lats = latlngs.map((ll) => (ll as number[])[0]);
      const lons = latlngs.map((ll) => (ll as number[])[1]);
      const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
      const centerLon = (Math.min(...lons) + Math.max(...lons)) / 2;
      map.flyTo([centerLat, centerLon], 16, { duration: 1 });
    }
  }, [selectedZoneId, zones, map]);
  return null;
}

const FACILITY_COLORS: Record<string, string> = {
  medical: "#ef4444",
  hospital: "#dc2626",
  police: "#3b82f6",
  lost_found: "#a855f7",
  toilet: "#6b7280",
  water: "#06b6d4",
};

export function ZoneMap({
  zones,
  facilities = [],
  incidents = [],
  selectedZoneId,
  onZoneClick,
}: Props) {
  return (
    <MapContainer
      center={KUMBH_CENTER}
      zoom={16}
      minZoom={15}
      maxZoom={18}
      maxBounds={KUMBH_BOUNDS}
      maxBoundsViscosity={1.0}
      className="zone-map"
      zoomControl
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <FlyToSelected zones={zones} selectedZoneId={selectedZoneId} />

      {/* Zone polygons */}
      {zones.map((zone) => {
        if (zone.geometry.type !== "Polygon") return null;
        const coords = (zone.geometry as GeoJSON.Polygon).coordinates[0];
        const positions = toLatLng(coords);
        const level = zone.level ?? "unknown";
        const colors = LEVEL_COLORS[level] ?? LEVEL_COLORS.unknown;
        const isSelected = zone.id === selectedZoneId;

        return (
          <Polygon
            key={zone.id}
            positions={positions}
            pathOptions={{
              color: colors.stroke,
              fillColor: colors.fill,
              fillOpacity: isSelected ? 0.75 : 0.45,
              weight: isSelected ? 3 : 2,
            }}
            eventHandlers={{
              click: () => onZoneClick?.(zone.id),
            }}
          >
            <Tooltip sticky>
              <div className="zone-tooltip">
                <strong>{zone.name}</strong>
                <br />
                Level:{" "}
                <span
                  style={{
                    color: colors.stroke,
                    textTransform: "uppercase",
                    fontWeight: 700,
                  }}
                >
                  {level}
                </span>
                <br />
                Count: {zone.count ?? "-"} / {zone.capacity_assumed.toLocaleString()}
                <br />
                Density: {zone.density != null ? zone.density.toFixed(2) : "-"} p/m²
                {zone.forecast_minutes != null && (
                  <>
                    <br />
                    RED in ~{Math.round(zone.forecast_minutes)} min
                  </>
                )}
              </div>
            </Tooltip>
          </Polygon>
        );
      })}

      {/* Facility markers */}
      {facilities.map((f) => (
        <CircleMarker
          key={f.id}
          center={[f.lat, f.lon]}
          radius={6}
          pathOptions={{
            color: FACILITY_COLORS[f.type] ?? "#6b7280",
            fillColor: FACILITY_COLORS[f.type] ?? "#6b7280",
            fillOpacity: 0.9,
          }}
        >
          <Tooltip>
            <strong>{f.name}</strong>
            <br />
            Type: {f.type}
          </Tooltip>
        </CircleMarker>
      ))}

      {/* SOS incident markers */}
      {incidents.map((inc) => (
        <CircleMarker
          key={inc.id}
          center={[inc.lat, inc.lon]}
          radius={10}
          pathOptions={{
            color: "#ff2244",
            fillColor: "#ff2244",
            fillOpacity: 0.8,
            weight: 3,
          }}
        >
          <Tooltip>
            <div className="zone-tooltip">
              <strong>SOS #{inc.id}</strong>
              <br />
              Status: {inc.status}
              {inc.facility_name && (
                <>
                  <br />&#8594; {inc.facility_name}
                </>
              )}
              <br />
              {new Date(inc.created_at).toLocaleTimeString()}
            </div>
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
