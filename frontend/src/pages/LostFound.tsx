/**
 * LostFound : tab for submitting lost/found person reports and viewing matches.
 */
import { useState } from "react";
import { api, type MatchResult } from "../api/client";
import { SimBadge } from "../components/SimBadge";

const ZONES = [
  { id: "har-ki-pauri", name: "Har Ki Pauri" },
  { id: "brahmakund", name: "Brahmakund" },
  { id: "ganga-ghat-upper", name: "Ganga Ghat (Upper)" },
  { id: "subhash-ghat", name: "Subhash Ghat" },
  { id: "moti-bazaar", name: "Moti Bazaar" },
  { id: "railway-road", name: "Railway Road Entry" },
];

interface FormState {
  type: "lost" | "found";
  name: string;
  age: string;
  clothing_color: string;
  clothing_garment: string;
  zone_id: string;
}

const DEFAULT_FORM: FormState = {
  type: "lost",
  name: "",
  age: "",
  clothing_color: "",
  clothing_garment: "",
  zone_id: "",
};

export function LostFound() {
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [reportId, setReportId] = useState<number | null>(null);
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await api.submitReport({
        type: form.type,
        reporter_chat_id: `web-${Date.now()}`,
        name: form.name || undefined,
        age: form.age ? parseInt(form.age) : undefined,
        clothing_color: form.clothing_color || undefined,
        clothing_garment: form.clothing_garment || undefined,
        zone_id: form.zone_id || undefined,
      });
      setReportId(res.report_id);
      setSuccess(true);

      if (form.type === "lost") {
        const m = await api.getMatches(res.report_id);
        setMatches(m);
      }
    } catch (err) {
      setError("Failed to submit report. Is the backend running?");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setForm(DEFAULT_FORM);
    setReportId(null);
    setMatches([]);
    setError(null);
    setSuccess(false);
  };

  return (
    <div className="lost-found">
      <div className="lost-found__header">
        <div>
          <h1 className="page-title">Lost &amp; Found</h1>
          <p className="page-subtitle">Report a missing person or a found wanderer</p>
        </div>
        <SimBadge />
      </div>

      {!success ? (
        <form className="lf-form" onSubmit={handleSubmit} id="lf-form">
          {/* Type selector */}
          <div className="lf-form__type-tabs">
            {(["lost", "found"] as const).map((t) => (
              <button
                key={t}
                type="button"
                id={`lf-type-${t}`}
                className={`lf-form__type-tab ${form.type === t ? "lf-form__type-tab--active" : ""}`}
                onClick={() => setForm({ ...form, type: t })}
              >
              {t === "lost" ? "Report Lost Person" : "Report Found Person"}
              </button>
            ))}
          </div>

          <div className="lf-form__grid">
            <div className="lf-form__field">
              <label htmlFor="lf-name">Name (if known)</label>
              <input
                id="lf-name"
                type="text"
                placeholder="e.g. Ramesh Kumar"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>

            <div className="lf-form__field">
              <label htmlFor="lf-age">Age (approx.)</label>
              <input
                id="lf-age"
                type="number"
                min={0}
                max={120}
                placeholder="e.g. 45"
                value={form.age}
                onChange={(e) => setForm({ ...form, age: e.target.value })}
              />
            </div>

            <div className="lf-form__field">
              <label htmlFor="lf-color">Clothing Color</label>
              <input
                id="lf-color"
                type="text"
                placeholder="e.g. saffron, white, blue"
                value={form.clothing_color}
                onChange={(e) => setForm({ ...form, clothing_color: e.target.value })}
              />
            </div>

            <div className="lf-form__field">
              <label htmlFor="lf-garment">Garment Type</label>
              <input
                id="lf-garment"
                type="text"
                placeholder="e.g. dhoti, kurta, saree"
                value={form.clothing_garment}
                onChange={(e) => setForm({ ...form, clothing_garment: e.target.value })}
              />
            </div>

            <div className="lf-form__field lf-form__field--full">
              <label htmlFor="lf-zone">Last Seen Zone</label>
              <select
                id="lf-zone"
                value={form.zone_id}
                onChange={(e) => setForm({ ...form, zone_id: e.target.value })}
              >
                <option value="">Select zone</option>
                {ZONES.map((z) => (
                  <option key={z.id} value={z.id}>{z.name}</option>
                ))}
              </select>
            </div>
          </div>

          {error && <div className="lf-form__error">{error}</div>}

          <button
            id="lf-submit-btn"
            type="submit"
            className="btn btn--primary"
            disabled={submitting}
          >
            {submitting ? "Submitting…" : "Submit Report"}
          </button>
        </form>
      ) : (
        <div className="lf-result">
          <div className="lf-result__success">
            Report #{reportId} submitted successfully
          </div>

          {form.type === "lost" && (
            <div className="lf-matches">
              <h2>Potential Matches</h2>
              {matches.length === 0 ? (
                <p className="lf-matches__empty">No matches found above threshold (0.6).</p>
              ) : (
                <ul className="lf-matches__list">
                  {matches.map((m) => (
                    <li key={m.found_report_id} className="lf-match-card">
                      <div className="lf-match-card__score">
                        <span className="lf-match-card__score-val">
                          {(m.score * 100).toFixed(0)}%
                        </span>
                        <span className="lf-match-card__score-label">match</span>
                      </div>
                      <dl className="lf-match-card__details">
                        {m.name && <><dt>Name</dt><dd>{m.name}</dd></>}
                        {m.age != null && <><dt>Age</dt><dd>{m.age}</dd></>}
                        {m.clothing_color && <><dt>Color</dt><dd>{m.clothing_color}</dd></>}
                        {m.clothing_garment && <><dt>Garment</dt><dd>{m.clothing_garment}</dd></>}
                        {m.zone_id && <><dt>Found in</dt><dd>{m.zone_id}</dd></>}
                        <dt>Reported</dt>
                        <dd>{new Date(m.reported_at).toLocaleString()}</dd>
                      </dl>
                      <div className="lf-match-card__breakdown">
                        {Object.entries(m.score_breakdown).map(([k, v]) => (
                          <span key={k} className="score-chip">
                            {k}: {(v * 100).toFixed(0)}%
                          </span>
                        ))}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <button id="lf-new-report-btn" className="btn btn--secondary" onClick={handleReset}>
            + New Report
          </button>
        </div>
      )}
    </div>
  );
}
