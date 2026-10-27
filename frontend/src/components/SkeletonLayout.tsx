import React from "react";

export const SkeletonLayout: React.FC = () => {
  return (
    <div className="skeleton-dashboard-grid" aria-label="Loading layout skeleton" aria-busy="true">
      {/* Top Stepper Skeleton */}
      <div className="skeleton-box skeleton-stepper" />

      {/* Bento Grid Skeleton */}
      <div className="skeleton-bento-grid">
        {/* Main Map Tile Skeleton */}
        <div className="skeleton-box skeleton-map-tile">
          <div className="skeleton-map-radar-ring" />
          <div className="skeleton-map-badge" />
        </div>

        {/* Threat & Divert Radar Skeleton */}
        <div className="skeleton-box skeleton-card skeleton-divert-tile">
          <div className="skeleton-line skeleton-line--title" />
          <div className="skeleton-line skeleton-line--lg" />
          <div className="skeleton-line skeleton-line--md" />
          <div className="skeleton-line skeleton-line--sm" />
        </div>

        {/* Live Alerts Skeleton */}
        <div className="skeleton-box skeleton-card skeleton-alerts-tile">
          <div className="skeleton-line skeleton-line--title" />
          <div className="skeleton-alert-row" />
          <div className="skeleton-alert-row" />
          <div className="skeleton-alert-row" />
        </div>

        {/* Telegram & Bot Tile Skeleton */}
        <div className="skeleton-box skeleton-card skeleton-bot-tile">
          <div className="skeleton-line skeleton-line--title" />
          <div className="skeleton-line skeleton-line--md" />
          <div className="skeleton-line skeleton-line--btn" />
        </div>

        {/* Lost & Found Tile Skeleton */}
        <div className="skeleton-box skeleton-card skeleton-lost-tile">
          <div className="skeleton-line skeleton-line--title" />
          <div className="skeleton-line skeleton-line--md" />
          <div className="skeleton-line skeleton-line--sm" />
        </div>
      </div>
    </div>
  );
};
