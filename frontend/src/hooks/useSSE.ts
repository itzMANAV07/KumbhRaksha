/**
 * useSSE : subscribes to GET /events and forwards parsed JSON messages.
 * Implements AGENTS.md Section 7.1 SSE subscription.
 */
import { useEffect, useRef, useState } from "react";
import { BASE } from "../api/client";

const SSE_URL = `${BASE}/events`;

export interface SSEEvent {
  type: "init" | "tick" | "reset" | "incident";
  [key: string]: unknown;
}

export function useSSE(onMessage: (event: SSEEvent) => void) {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let es: EventSource;
    let retryTimeout: ReturnType<typeof setTimeout>;

    function connect() {
      es = new EventSource(SSE_URL);

      es.onopen = () => setConnected(true);

      es.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data) as SSEEvent;
          onMessageRef.current(data);
        } catch {
          // malformed event : ignore
        }
      };

      es.onerror = () => {
        setConnected(false);
        es.close();
        retryTimeout = setTimeout(connect, 3000);
      };
    }

    connect();

    return () => {
      es?.close();
      clearTimeout(retryTimeout);
    };
  }, []);

  return connected;
}
