/**
 * AlertFeed : scrollable alert list driven by SSE tick events.
 */
import { useEffect, useRef } from "react";

export interface Alert {
  id: string;
  zone_id: string;
  zone_name: string;
  level: string;
  message: string;
  forecast_minutes?: number | null;
  divert_to?: string | null;
  timestamp: number;
}

interface Props {
  alerts: Alert[];
}

export function AlertFeed({ alerts }: Props) {
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = 0;
    }
  }, [alerts.length]);

  if (alerts.length === 0) {
    return (
      <div className="alert-feed alert-feed--empty">
        <p>No alerts. Watching zones.</p>
      </div>
    );
  }

  return (
    <ul className="alert-feed" ref={listRef} aria-label="Alert feed">
      {alerts.map((a) => (
        <li key={a.id} className={`alert-item alert-item--${a.level}`}>
          <div className="alert-item__header">
            <span className={`alert-item__level-dot alert-item__level-dot--${a.level}`} aria-label={a.level} />
            <span className="alert-item__zone">{a.zone_name}</span>
            <span className="alert-item__time">
              {new Date(a.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <p className="alert-item__msg">{a.message}</p>
          {a.forecast_minutes != null && (
            <p className="alert-item__forecast">
              Estimated RED in {Math.round(a.forecast_minutes)} min
            </p>
          )}
          {a.divert_to && (
            <p className="alert-item__divert">
              Divert to: <strong>{a.divert_to}</strong>
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}
