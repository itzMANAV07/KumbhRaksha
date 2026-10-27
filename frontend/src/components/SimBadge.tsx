/**
 * SimBadge : always-visible "SIMULATED DATA" badge (AGENTS.md Rule 7)
 */
export function SimBadge() {
  return (
    <div className="sim-badge" aria-label="All data shown is simulated">
      <span className="sim-badge__dot" />
      SIMULATED DATA
    </div>
  );
}
