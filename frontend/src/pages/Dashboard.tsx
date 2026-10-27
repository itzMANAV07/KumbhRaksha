/**
 * Dashboard : State-of-the-art Bento Grid interface for KumbhRaksha.
 * Features:
 * - Hero reveal animation
 * - Social proof compliance & authority benchmarks
 * - Bento Grid architecture (Map, Divert Radar, Event Stream, Telegram Bot, Lost & Found)
 * - Single-line horizontal process stepper (01 Sense -> 02 Predict -> 03 Divert -> 04 Dispatch -> 05 Reunite)
 * - Interactive Cursor Demo Tour
 * - One Primary Action per screen (dynamic high-contrast CTA)
 * - Skeleton state preview
 * - Ink & greys aesthetic with single saffron accent
 * - Slide-in Zone Inspector & Rise-for-task cards
 */
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ZoneMap, type Incident } from "../components/ZoneMap";
import { AlertFeed, type Alert } from "../components/AlertFeed";
import { ScenarioSelector } from "../components/ScenarioSelector";
import { HeroSection } from "../components/HeroSection";
import { ProcessStepper } from "../components/ProcessStepper";
import { SkeletonLayout } from "../components/SkeletonLayout";
import { useSSE, type SSEEvent } from "../hooks/useSSE";
import { api, type ZoneResponse } from "../api/client";

interface ZoneRuntimeState {
  count: number;
  density: number;
  level: string;
  forecast_minutes: number | null;
  divert_to: string | null;
}

const ZONE_NAMES: Record<string, string> = {};

export function Dashboard() {
  const [zones, setZones] = useState<ZoneResponse[]>([]);
  const [runtimeState, setRuntimeState] = useState<Record<string, ZoneRuntimeState>>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);
  const [scenario, setScenario] = useState("calm");
  const [alertCount, setAlertCount] = useState(0);
  const [activeStep, setActiveStep] = useState<string>("predict");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Load zone geometry
  useEffect(() => {
    setIsLoading(true);
    api.getZones()
      .then((data) => {
        setZones(data);
        data.forEach((z) => {
          ZONE_NAMES[z.id] = z.name;
        });
        setTimeout(() => setIsLoading(false), 300);
      })
      .catch((err) => {
        console.error(err);
        setIsLoading(false);
      });
  }, []);

  // Poll for incidents every 10 s
  useEffect(() => {
    const fetchIncidents = () => {
      api
        .getIncidents()
        .then(
          (
            data: Array<{
              id: number;
              lat: number;
              lon: number;
              nearest_facility_id?: string | null;
              status: string;
              created_at: string;
            }>
          ) => {
            setIncidents(
              data.map((i) => ({
                id: i.id,
                lat: i.lat,
                lon: i.lon,
                facility_name: i.nearest_facility_id ?? null,
                status: i.status,
                created_at: i.created_at,
              }))
            );
          }
        )
        .catch(() => {});
    };
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 10_000);
    return () => clearInterval(interval);
  }, []);

  const handleSSEMessage = useCallback((event: SSEEvent) => {
    if (event.type === "init" || event.type === "tick") {
      const zonesList = event.zones as Array<{
        zone_id: string;
        count: number;
        density: number;
        level: string;
        forecast_minutes: number | null;
        divert_to: string | null;
      }>;

      setRuntimeState((prev) => {
        const next = { ...prev };
        const newAlerts: Alert[] = [];

        zonesList.forEach((z) => {
          const prevLevel = prev[z.zone_id]?.level;
          next[z.zone_id] = {
            count: z.count,
            density: z.density,
            level: z.level,
            forecast_minutes: z.forecast_minutes,
            divert_to: z.divert_to,
          };

          if (
            event.type === "tick" &&
            prevLevel !== z.level &&
            (z.level === "orange" || z.level === "red")
          ) {
            setAlertCount((c) => c + 1);
            newAlerts.push({
              id: `${z.zone_id}-${Date.now()}`,
              zone_id: z.zone_id,
              zone_name: ZONE_NAMES[z.zone_id] ?? z.zone_id,
              level: z.level,
              message:
                z.level === "red"
                  ? `Critical density reached! Immediate diversion advised.`
                  : `Zone approaching danger threshold (${z.density.toFixed(2)} p/m²)`,
              forecast_minutes: z.forecast_minutes,
              divert_to: z.divert_to,
              timestamp: Date.now(),
            });
          }
        });

        if (newAlerts.length > 0) {
          setAlerts((p) => [...newAlerts, ...p].slice(0, 50));
        }

        return next;
      });
    } else if (event.type === "incident") {
      const inc = event.incident as {
        id: number;
        lat: number;
        lon: number;
        facility_name?: string | null;
        status: string;
        created_at: string;
      };
      setIncidents((prev) => {
        if (prev.some((i) => i.id === inc.id)) return prev;
        return [
          {
            id: inc.id,
            lat: inc.lat,
            lon: inc.lon,
            facility_name: inc.facility_name ?? null,
            status: inc.status,
            created_at: inc.created_at,
          },
          ...prev,
        ].slice(0, 20);
      });
      setAlertCount((c) => c + 1);
      setAlerts((prev) => [
        {
          id: `sos-${inc.id}-${Date.now()}`,
          zone_id: "sos",
          zone_name: "SOS BEACON",
          level: "red",
          message: `Incident #${inc.id} routed to ${inc.facility_name ?? "Emergency Response Unit"}`,
          forecast_minutes: null,
          divert_to: null,
          timestamp: Date.now(),
        },
        ...prev,
      ].slice(0, 50));
    } else if (event.type === "reset") {
      setRuntimeState({});
      setAlerts([]);
      setAlertCount(0);
    }
  }, []);

  const connected = useSSE(handleSSEMessage);

  // Merge runtime state into zone objects
  const zonesWithState: ZoneResponse[] = zones.map((z) => ({
    ...z,
    ...(runtimeState[z.id] ?? {}),
  }));

  // Identify highest risk zone
  const highestRiskZone = zonesWithState.reduce<ZoneResponse | null>((worst, cur) => {
    if (!worst) return cur;
    return (cur.density ?? 0) > (worst.density ?? 0) ? cur : worst;
  }, null);

  const selectedZone = selectedZoneId
    ? zonesWithState.find((z) => z.id === selectedZoneId) ?? null
    : null;

  const totalCrowd = zonesWithState.reduce((acc, z) => acc + (z.count ?? 0), 0);

  // Calculate dynamic primary action per screen
  const isSurge = Boolean(
    scenario === "peak_snan_morning" ||
    scenario === "stampede_risk" ||
    (highestRiskZone && (highestRiskZone.level === "orange" || highestRiskZone.level === "red"))
  );

  let primaryActionLabel = "Run Peak Snan Surge Simulation";
  if (selectedZone && selectedZone.divert_to) {
    primaryActionLabel = `Execute Corridor Divert: Avoid ${selectedZone.name}`;
  } else if (highestRiskZone && (highestRiskZone.level === "orange" || highestRiskZone.level === "red")) {
    primaryActionLabel = `Inspect Danger Zone: ${highestRiskZone.name}`;
  } else if (isSurge) {
    primaryActionLabel = `Monitor Influx: ${highestRiskZone?.name ?? "Haridwar Perimeter"}`;
  }

  const handlePrimaryAction = () => {
    if (selectedZone && selectedZone.divert_to) {
      setSelectedZoneId(selectedZone.divert_to);
      setActiveStep("divert");
    } else if (highestRiskZone && (highestRiskZone.level === "orange" || highestRiskZone.level === "red")) {
      setSelectedZoneId(highestRiskZone.id);
      setActiveStep("predict");
    } else if (isSurge) {
      if (highestRiskZone) setSelectedZoneId(highestRiskZone.id);
      setActiveStep("predict");
    } else {
      api.setScenario("peak_snan_morning").then(() => setScenario("peak_snan_morning"));
      setActiveStep("predict");
    }
  };

  const handleStepClick = (stepId: string) => {
    setActiveStep(stepId);
    if (stepId === "sense" && zonesWithState.length > 0) {
      setSelectedZoneId(null);
    } else if (stepId === "predict" && highestRiskZone) {
      setSelectedZoneId(highestRiskZone.id);
    } else if (stepId === "divert" && highestRiskZone?.divert_to) {
      setSelectedZoneId(highestRiskZone.divert_to);
    }
  };

  return (
    <div className="dashboard-page">
      {/* 1. HERO REVEAL & SOCIAL PROOF : Full width, no padding */}
      <HeroSection
        primaryActionLabel={primaryActionLabel}
        onPrimaryAction={handlePrimaryAction}
        isSimulating={isSurge}
        totalCrowd={totalCrowd}
        criticalZoneName={
          highestRiskZone && (highestRiskZone.level === "red" || highestRiskZone.level === "orange")
            ? highestRiskZone.name
            : null
        }
      />

      <div className="dashboard-root">
      {/* 2. ONE-LINE STEP BY STEP PROCESS PIPELINE */}
      <section className="stepper-section-wrap">
        <ProcessStepper activeStep={activeStep} onStepClick={handleStepClick} />
      </section>

      {/* 3. SCENARIO RADAR CONTROLS */}
      <div className="dashboard-control-strip">
        <div className="control-strip-left">
          <span className="control-label">SIMULATION SCENARIO:</span>
          <ScenarioSelector current={scenario} onChange={setScenario} />
        </div>

        <div className="control-strip-right">
          <div className="density-legend-bar">
            <span className="legend-title">RISK INDEX:</span>
            <span className="legend-chip legend-chip--green">NORMAL &lt;1.0</span>
            <span className="legend-chip legend-chip--yellow">ELEVATED 1.0-2.5</span>
            <span className="legend-chip legend-chip--orange">HIGH RISK 2.5-4.0</span>
            <span className="legend-chip legend-chip--red">CRITICAL &ge;4.0</span>
          </div>

          <div
            className={`connection-dot ${connected ? "connection-dot--on" : "connection-dot--off"}`}
            title={connected ? "Streaming Live SSE Events" : "Connecting..."}
          >
            {connected ? "● LIVE 5s STREAM" : "○ RECONNECTING"}
          </div>
        </div>
      </div>

      {/* 4. SKELETON / BENTO GRID LAYOUT */}
      {isLoading ? (
        <SkeletonLayout />
      ) : (
        <div className="bento-container">
          {/* Bento Cell 1: Main Leaflet Spatial GIS Radar */}
          <div className="bento-card bento-card--map">
            <div className="bento-card-header">
              <div className="bento-header-left">
                <span className="bento-radar-icon bento-radar-icon--map" aria-hidden="true" />
                <div>
                  <h2 className="bento-title">Spatial GIS Density Radar</h2>
                  <span className="bento-subtitle">6 Haridwar Ghat Polygons: Real-time Influx</span>
                </div>
              </div>
              <div className="bento-header-badges">
                {incidents.length > 0 && (
                  <span className="sos-beacon-badge">
                    {incidents.length} ACTIVE INCIDENT{incidents.length > 1 ? "S" : ""}
                  </span>
                )}
                <span className="bento-live-badge">REAL-TIME TELEMETRY</span>
              </div>
            </div>

            <div className="bento-map-canvas">
              <ZoneMap
                zones={zonesWithState}
                incidents={incidents}
                selectedZoneId={selectedZoneId}
                onZoneClick={(id) => setSelectedZoneId(id)}
              />
            </div>
          </div>

          {/* Bento Cell 2: Threat & Divert Radar (Rise for task) */}
          <div className="bento-card bento-card--divert rise-for-task">
            <div className="bento-card-header">
              <div className="bento-header-left">
                <span className="bento-radar-icon bento-radar-icon--neon bento-radar-icon--divert" aria-hidden="true" />
                <div>
                  <h3 className="bento-title">Predictive Threat Radar</h3>
                  <span className="bento-subtitle">30-Min Influx Gradient</span>
                </div>
              </div>
              <span className={`bento-risk-pill bento-risk-pill--${highestRiskZone?.level ?? "green"}`}>
                {(highestRiskZone?.level ?? "GREEN").toUpperCase()}
              </span>
            </div>

            <div className="divert-body">
              {highestRiskZone ? (
                <>
                  <div className="threat-stat-row">
                    <div className="threat-stat">
                      <span className="threat-stat-label">MAX CONCENTRATION</span>
                      <span className="threat-stat-val">{highestRiskZone.name}</span>
                    </div>
                    <div className="threat-stat">
                      <span className="threat-stat-label">CURRENT DENSITY</span>
                      <span className="threat-stat-val threat-stat-val--accent">
                        {highestRiskZone.density?.toFixed(2) ?? "0.10"} p/m²
                      </span>
                    </div>
                  </div>

                  {highestRiskZone.forecast_minutes != null ? (
                    <div className="forecast-banner rise-for-task">
                      <span className="forecast-icon forecast-icon--warn" aria-hidden="true" />
                      <div className="forecast-text">
                        <strong>Projected RED in ~{Math.round(highestRiskZone.forecast_minutes)} min</strong>
                        <span>Influx exceeds corridor capacity limit</span>
                      </div>
                    </div>
                  ) : (
                    <div className="forecast-banner forecast-banner--safe">
                      <span className="forecast-icon forecast-icon--ok" aria-hidden="true" />
                      <div className="forecast-text">
                        <strong>Density Gradient Stable</strong>
                        <span>No surge above threshold detected</span>
                      </div>
                    </div>
                  )}

                  <div className="divert-recommendation-card">
                    <span className="divert-lead-label">RECOMMENDED ESCAPE CORRIDOR:</span>
                    <div className="divert-target-row">
                      <span className="divert-arrow-icon" aria-hidden="true">&#8594;</span>
                      <span className="divert-zone-name">
                        {highestRiskZone.divert_to
                          ? ZONE_NAMES[highestRiskZone.divert_to] ?? highestRiskZone.divert_to
                          : "Maintain Current Dispersion"}
                      </span>
                      {highestRiskZone.divert_to && (
                        <button
                          className="divert-inspect-btn"
                          onClick={() => setSelectedZoneId(highestRiskZone.divert_to ?? null)}
                          type="button"
                        >
                          View Zone
                        </button>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-telemetry">Monitoring zone state...</div>
              )}
            </div>
          </div>

          {/* Bento Cell 3: Telegram Live Assistant Dispatch */}
          <div className="bento-card bento-card--telegram rise-for-task">
            <div className="bento-card-header">
              <div className="bento-header-left">
                <span className="bento-radar-icon bento-radar-icon--telegram" aria-hidden="true" />
                <div>
                  <h3 className="bento-title">Safety Bot &amp; Snan Pass</h3>
                  <span className="bento-subtitle">7 Languages, E-Pass &amp; Amenities</span>
                </div>
              </div>
              <span className="telegram-status-pill">ONLINE</span>
            </div>

            <div className="telegram-card-body">
              <p className="telegram-desc">
                Interactive assistant for crowd telemetry, free Snan E-Pass tokens,
                safe corridor diversions, and 24x7 medical or lost-person assistance.
              </p>

              <div className="sample-prompts-tray">
                <span className="prompt-pill">"Book Free Snan Pass"</span>
                <span className="prompt-pill">"Har Ki Pauri crowd"</span>
                <span className="prompt-pill">"Doctor &amp; drinking water"</span>
                <span className="prompt-pill">"help / bachao"</span>
              </div>

              <div className="telegram-action-row">
                <Link to="/chat" className="telegram-open-btn">
                  <span>Open Safety Assistant</span>
                  <span>&#8594;</span>
                </Link>

                <a
                  href="https://t.me/kumbh_raksha_safety_bot"
                  target="_blank"
                  rel="noreferrer"
                  className="telegram-simulator-link"
                >
                  Telegram Bot ↗
                </a>
              </div>
            </div>
          </div>

          {/* Bento Cell 4: Explainable Lost & Found Gateway */}
          <div className="bento-card bento-card--lostfound">
            <div className="bento-card-header">
              <div className="bento-header-left">
                <span className="bento-radar-icon bento-radar-icon--search" aria-hidden="true" />
                <div>
                  <h3 className="bento-title">Lost &amp; Found Radar</h3>
                  <span className="bento-subtitle">Biometric-Free Multi-Factor Matcher</span>
                </div>
              </div>
              <Link to="/lost-found" className="bento-link-action">
                Report &amp; Match ↗
              </Link>
            </div>

            <div className="lostfound-card-body">
              <div className="scoring-formula-strip">
                <span className="formula-tag">0.4 Clothing</span>
                <span className="formula-tag">0.3 Age</span>
                <span className="formula-tag">0.2 Zone</span>
                <span className="formula-tag">0.1 Time</span>
                <span className="formula-threshold">&ge; 0.6 MATCH</span>
              </div>
              <p className="lostfound-sub-info">
                Text-based clothing and proximity scoring protects pilgrim privacy with zero face
                recognition or permanent biometrics.
              </p>
              <div className="lostfound-action-bar">
                <Link to="/lost-found" className="lostfound-primary-btn">
                  Launch Lost &amp; Found Portal →
                </Link>
              </div>
            </div>
          </div>

          {/* Bento Cell 5: Live Streaming Alerts Feed (Rise for task) */}
          <div className="bento-card bento-card--alerts rise-for-task">
            <div className="bento-card-header">
              <div className="bento-header-left">
                <span className="bento-radar-icon bento-radar-icon--alert" aria-hidden="true" />
                <div>
                  <h3 className="bento-title">Live Alert Feed</h3>
                  <span className="bento-subtitle">Autonomous Safety Broadcasts</span>
                </div>
              </div>
              {alertCount > 0 && <span className="alert-count-pill">{alertCount} NEW</span>}
            </div>

            <div className="bento-alerts-body">
              <AlertFeed alerts={alerts} />
            </div>
          </div>
        </div>
      )}

      {/* 5. SLIDE TO DRILL IN: ZONE INSPECTOR DRAWER */}
      <div
        className={`zone-inspector-drawer ${selectedZone ? "zone-inspector-drawer--open" : ""}`}
        role="dialog"
        aria-label="Zone Inspector Drawer"
      >
        {selectedZone && (
          <div className="zone-inspector-inner">
            <div className="drawer-header">
              <div>
                <span className="drawer-pretitle">SPATIAL SECTOR DETAIL</span>
                <h2 className="drawer-title">{selectedZone.name}</h2>
              </div>
              <button
                className="drawer-close-btn"
                onClick={() => setSelectedZoneId(null)}
                aria-label="Close sector details"
                type="button"
              >
                &times;
              </button>
            </div>

            <div className={`drawer-risk-ribbon drawer-risk-ribbon--${selectedZone.level ?? "green"}`}>
              <span>CURRENT STATUS: {(selectedZone.level ?? "GREEN").toUpperCase()}</span>
              <span className="drawer-density-badge">
                {selectedZone.density?.toFixed(2) ?? "0.10"} p/m²
              </span>
            </div>

            <div className="drawer-metrics-grid">
              <div className="drawer-metric-card">
                <span className="drawer-metric-label">ESTIMATED COUNT</span>
                <span className="drawer-metric-val">
                  {selectedZone.count?.toLocaleString() ?? "-"}
                </span>
              </div>
              <div className="drawer-metric-card">
                <span className="drawer-metric-label">SECTOR CAPACITY</span>
                <span className="drawer-metric-val">
                  {selectedZone.capacity_assumed.toLocaleString()}
                </span>
              </div>
              <div className="drawer-metric-card">
                <span className="drawer-metric-label">SURFACE AREA</span>
                <span className="drawer-metric-val">{selectedZone.area_m2.toLocaleString()} m²</span>
              </div>
              <div className="drawer-metric-card">
                <span className="drawer-metric-label">TIME TO RED</span>
                <span className="drawer-metric-val drawer-metric-val--alert">
                  {selectedZone.forecast_minutes != null
                    ? `~${Math.round(selectedZone.forecast_minutes)} min`
                    : "Stable"}
                </span>
              </div>
            </div>

            {selectedZone.divert_to && (
              <div className="drawer-corridor-box">
                <span className="corridor-label">SAFE ESCAPE CORRIDOR:</span>
                <div className="corridor-dest">
                  <span className="corridor-dest-arrow" aria-hidden="true">&#8594;</span>
                  <span className="corridor-dest-name">
                    {ZONE_NAMES[selectedZone.divert_to] ?? selectedZone.divert_to}
                  </span>
                </div>
                <button
                  className="corridor-switch-btn"
                  onClick={() => setSelectedZoneId(selectedZone.divert_to ?? null)}
                  type="button"
                >
                  Inspect Corridor Sector &#8594;
                </button>
              </div>
            )}

            <div className="drawer-adjacency-wrap">
              <span className="drawer-subhead">ADJACENT PERIMETER SECTORS</span>
              <div className="adjacency-chips">
                {selectedZone.adjacency.map((adj) => (
                  <button
                    key={adj}
                    className="adj-chip"
                    onClick={() => setSelectedZoneId(adj)}
                    type="button"
                  >
                    <span>{ZONE_NAMES[adj] ?? adj}</span>
                    <span className="adj-chip-arrow">→</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Drawer Overlay Backdrop */}
      {selectedZone && (
        <div
          className="drawer-backdrop"
          onClick={() => setSelectedZoneId(null)}
          aria-hidden="true"
        />
      )}
      </div>{/* end dashboard-root */}
    </div>
  );
}
