/**
 * ScenarioSelector : dropdown + reset button to control the simulator scenario.
 */
import { api } from "../api/client";

const SCENARIOS = [
  { id: "calm", label: "Calm (Default)" },
  { id: "peak_snan_morning", label: "Peak Snan: Morning" },
  { id: "evening_aarti", label: "Evening Aarti Rush" },
  { id: "stampede_risk", label: "Stampede Risk (Stress Test)" },
];

interface Props {
  current: string;
  onChange: (s: string) => void;
}

export function ScenarioSelector({ current, onChange }: Props) {
  const handleChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    try {
      await api.setScenario(val);
      onChange(val);
    } catch (err) {
      console.error("Failed to set scenario:", err);
    }
  };

  const handleReset = async () => {
    try {
      await api.resetSim();
      onChange("calm");
    } catch (err) {
      console.error("Failed to reset:", err);
    }
  };

  return (
    <div className="scenario-selector">
      <label htmlFor="scenario-select" className="scenario-selector__label">
        Scenario
      </label>
      <select
        id="scenario-select"
        className="scenario-selector__select"
        value={current}
        onChange={handleChange}
      >
        {SCENARIOS.map((s) => (
          <option key={s.id} value={s.id}>
            {s.label}
          </option>
        ))}
      </select>
      <button
        id="reset-sim-btn"
        className="scenario-selector__reset"
        onClick={handleReset}
        title="Reset all zones to calm state"
      >
        ↺ Reset
      </button>
    </div>
  );
}
