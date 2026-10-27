import React from "react";
import { SimBadge } from "./SimBadge";
import kumbhHero from "../assets/kumbh_hero.jpg";

interface HeroSectionProps {
  primaryActionLabel: string;
  onPrimaryAction: () => void;
  isSimulating: boolean;
  totalCrowd: number;
  criticalZoneName?: string | null;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  primaryActionLabel,
  onPrimaryAction,
  totalCrowd,
  criticalZoneName,
}) => {
  return (
    <section
      className="hero-fullscreen"
      aria-label="KumbhRaksha Crowd Safety System"
      style={{ backgroundImage: `url(${kumbhHero})` }}
    >
      {/* Gradient overlay : left side for text legibility */}
      <div className="hero-overlay" />

      {/* Main content */}
      <div className="hero-content-wrap">
        <div className="hero-badges">
          <span className="hero-status-pill">
            <span className="hero-status-dot" />
            GIS RADAR ACTIVE
          </span>
          <SimBadge />
        </div>

        <div className="hero-eyebrow">
          <span className="hero-eyebrow-line" />
          <span className="hero-eyebrow-text">HARIDWAR CROWD SAFETY SYSTEM</span>
        </div>

        <h1 className="hero-headline">
          Kumbh<span className="hero-headline-accent">Raksha</span>
        </h1>

        <p className="hero-subtext">
          Real-time crowd density monitoring across 6 ghat zones. 30-minute surge forecasting,
          bilingual diversion alerts, and text-based lost-and-found matching for Kumbh Mela pilgrims.
        </p>

        {totalCrowd > 0 && (
          <div className="hero-telemetry">
            <span className="hero-telemetry-label">LIVE FOOTFALL:</span>
            <span className="hero-telemetry-value">{totalCrowd.toLocaleString()} pilgrims tracked</span>
          </div>
        )}

        <div className="hero-cta-wrap">
          <button
            id="hero-primary-action-btn"
            className="hero-cta-btn"
            onClick={onPrimaryAction}
            type="button"
          >
            <span className="hero-cta-shimmer" />
            {criticalZoneName && <span className="hero-cta-alert-indicator" />}
            <span className="hero-cta-text">{primaryActionLabel}</span>
            <span className="hero-cta-arrow">&#8594;</span>
          </button>
        </div>
      </div>

      {/* System specification bar */}
      <div className="hero-stats-bar">
        <div className="hero-stat">
          <span className="hero-stat-value">6</span>
          <span className="hero-stat-label">Monitored Ghat Zones</span>
        </div>
        <div className="hero-stat-divider" />
        <div className="hero-stat">
          <span className="hero-stat-value">5 s</span>
          <span className="hero-stat-label">SSE Tick Interval</span>
        </div>
        <div className="hero-stat-divider" />
        <div className="hero-stat">
          <span className="hero-stat-value">30 min</span>
          <span className="hero-stat-label">Density Forecast Window</span>
        </div>
        <div className="hero-stat-divider" />
        <div className="hero-stat">
          <span className="hero-stat-value">No PII</span>
          <span className="hero-stat-label">Text descriptors only: no biometrics</span>
        </div>
      </div>
    </section>
  );
};
