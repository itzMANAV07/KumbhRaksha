/**
 * Typed fetch wrappers for KumbhRaksha backend API.
 * Configured via VITE_API_URL for production deployments (e.g. Vercel),
 * falling back to local dev server only when running in development mode.
 */
export const BASE = (import.meta.env.VITE_API_URL as string)?.replace(/\/+$/, "") ||
  (import.meta.env.DEV ? "http://localhost:8000" : "");

export interface ZoneState {
  zone_id: string;
  count: number;
  density: number;
  level: "green" | "yellow" | "orange" | "red";
  forecast_minutes: number | null;
  divert_to: string | null;
  updated_at: string;
}

export interface ZoneResponse {
  id: string;
  name: string;
  area_m2: number;
  capacity_assumed: number;
  adjacency: string[];
  geometry: GeoJSON.Geometry;
  count?: number;
  density?: number;
  level?: string;
  forecast_minutes?: number | null;
  divert_to?: string | null;
}

export interface ChatRequest {
  chat_id: string;
  text: string;
  language?: string;
  lat?: number;
  lon?: number;
}

export interface ChatResponse {
  text: string;
  buttons?: string[];
}

export interface SOSRequest {
  chat_id: string;
  lat: number;
  lon: number;
}

export interface SOSResponse {
  incident_id: number;
  reply: string;
}

export interface ReportRequest {
  type: "lost" | "found";
  reporter_chat_id: string;
  name?: string;
  age?: number;
  clothing_color?: string;
  clothing_garment?: string;
  zone_id?: string;
}

export interface ReportResponse {
  report_id: number;
}

export interface MatchResult {
  found_report_id: number;
  score: number;
  score_breakdown: Record<string, number>;
  name?: string;
  age?: number;
  clothing_color?: string;
  clothing_garment?: string;
  zone_id?: string;
  reported_at: string;
}

// ── HTTP helpers ────────────────────────────────────────────────────────────

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return res.json();
}

// ── API functions ───────────────────────────────────────────────────────────

export const api = {
  getZones: () => get<ZoneResponse[]>("/zones"),
  getZone: (id: string) => get<ZoneResponse>(`/zones/${id}`),

  sendChat: (req: ChatRequest) => post<ChatResponse>("/chat", req),

  triggerSOS: (req: SOSRequest) => post<SOSResponse>("/sos", req),

  submitReport: (req: ReportRequest) => post<ReportResponse>("/report", req),
  getMatches: (reportId: number) => get<MatchResult[]>(`/matches/${reportId}`),
  getIncidents: () =>
    get<
      Array<{
        id: number;
        lat: number;
        lon: number;
        nearest_facility_id?: string | null;
        status: string;
        created_at: string;
      }>
    >("/incidents"),

  setScenario: (scenario: string) => post("/sim/scenario", { scenario }),
  resetSim: () => post("/sim/reset", {}),
};
