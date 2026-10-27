# KumbhRaksha — Technical Blueprint

## 1. Overview

KumbhRaksha is a crowd-safety command-and-control system for the Kumbh Mela.
It comprises:
- A FastAPI backend that runs a crowd simulator, a risk engine, and a chat
  processor.
- A React + Leaflet dashboard with live SSE updates.
- A Telegram bot (plus web fallback) for pilgrim interaction.
- A lost-and-found matching engine and an SOS/incident system.

All data presented to users is labelled **SIMULATED DATA**. No real location
data from pilgrims is collected or stored beyond the Mela window.

---

## 2. System Architecture

    Browser (React)
        |  SSE stream (GET /events)
        |  REST calls  (GET /zones, POST /chat, POST /report, POST /sos)
        v
    FastAPI backend   <---> SQLite (kumbh.db)
        |
        |- sim/engine.py    (asyncio background task)
        |- risk.py          (density, level, forecast, divert)
        |- chat/intent.py   (keyword rules + optional Gemini)
        |- matching.py      (lost & found scoring)
        |- sos.py           (SOS, nearest facility)
        `- adapters/telegram.py  (webhook -> POST /chat)

---

## 3. Data Model

### Zone
- id (str, PK, e.g. "hkp_main")
- name (str)
- area_m2 (float)
- capacity_assumed (int)
- adjacency (list[str])  <- zone ids
- geometry (GeoJSON polygon, from zones.geojson)

### Facility
- id (str, PK)
- name (str)
- type (str, e.g. "first_aid", "police", "water")
- lat (float)
- lon (float)
- demo (bool, always true for seed data)

### ZoneState (in-memory, not persisted)
- zone_id (str)
- count (int)
- count_prev (int)
- density (float)
- level (str: green|yellow|orange|red)
- forecast_minutes (float | None)
- divert_to (str | None)
- updated_at (datetime)

### LostReport
- id (int, PK, autoincrement)
- type (str: lost|found)
- reporter_chat_id (str)
- name (str | None)
- age (int | None)
- clothing_color (str | None)
- clothing_garment (str | None)
- zone_id (str | None)
- reported_at (datetime)
- status (str: open|resolved)

### Incident
- id (int, PK, autoincrement)
- chat_id (str)
- lat (float | None)
- lon (float | None)
- nearest_facility_id (str | None)
- status (str: open|acknowledged|resolved)
- created_at (datetime)

### Subscription
- id (int, PK, autoincrement)
- chat_id (str)
- zone_id (str)
- language (str: en|hi)
- created_at (datetime)
- last_alerted_at (datetime | None)

---

## 4. API Endpoints

### Health
    GET  /health                -> {"status": "ok"}

### Zones
    GET  /zones                 -> list[ZoneResponse]
    GET  /zones/{zone_id}       -> ZoneResponse

### Simulator control
    POST /sim/scenario          -> {"scenario": "peak_snan_morning"}
    POST /sim/reset             -> {"ok": true}

### SSE
    GET  /events                -> text/event-stream
         event: tick            -> ZoneTick[]
         event: incident        -> IncidentEvent
         event: alert           -> AlertEvent

### Chat
    POST /chat                  -> {"text": "...", "buttons": [...] | null}
    Body: {"chat_id": str, "text": str, "language": "en"|"hi",
           "lat": float|null, "lon": float|null}

### SOS
    POST /sos                   -> {"incident_id": int, "reply": str}
    Body: {"chat_id": str, "lat": float, "lon": float}

### Lost & Found
    POST /report                -> {"report_id": int}
    GET  /matches/{report_id}   -> list[MatchResult]
    POST /matches/{match_id}/confirm -> {"ok": true}

### Incidents
    GET  /incidents             -> list[IncidentResponse]
    PATCH /incidents/{id}       -> {"status": "acknowledged"|"resolved"}

---

## 5. Simulator Scenarios

Scenarios are defined in sim/scenarios.py as dicts:
    {
      "name": str,
      "description": str,
      "deltas": {zone_id: Callable[[int, int], int]}
        # (count, tick_num) -> new_count
    }

Built-in scenarios:
- idle              : no change, counts stay at seed values
- peak_snan_morning : har_ki_pauri_main +180/tick, approach roads +60/tick
- evening_aarti     : har_ki_pauri_main +120/tick, adjoining ghats +40/tick
- emergency_drill   : all zones +10/tick until red, then plateau

---

## 6. Risk Engine Logic (see AGENTS.md Section 7.2-7.4)

Implemented in risk.py. Functions:
- compute_density(count, area_m2) -> float
- compute_level(density) -> str
- forecast_minutes(count_now, count_prev, tick_seconds, area_m2) -> float|None
- suggest_divert(zone_id, zone_states, adjacency) -> str|None

---

## 7. Chat Flow

1. POST /chat receives {chat_id, text, language, lat?, lon?}.
2. intent.py.classify(text, language) -> Intent (keyword rules first).
3. If no keyword match and GEMINI_API_KEY set: call Gemini with 3 s timeout.
   Validate response with Pydantic. On failure, intent = "menu".
4. Handler looks up real-time zone data from ZoneState.
5. templates.py.render(intent, data, language) -> reply str.
6. Return {"text": reply, "buttons": [...] | null}.

---

## 8. Lost & Found Flow

1. User sends "I lost my child" -> intent = lost_person.
2. Bot collects: name, age, clothing_color, clothing_garment, zone_id via
   multi-turn conversation (state stored in session dict keyed by chat_id).
3. On final confirmation, POST /report creates a LostReport.
4. GET /matches/{report_id} runs matching.py against open found-person reports.
5. Dashboard shows candidates with score breakdown.
6. Confirm button -> both reports status = resolved.

---

## 9. SOS Flow

1. SOS keywords detected in intent.py BEFORE any other processing.
2. sos.py.handle(chat_id, lat, lon) called synchronously.
3. Haversine distance to all facilities -> nearest returned.
4. Incident created, SSE event emitted, reply returned within 2 s.

---

## 10. Subscription & Alert Flow

1. User asks about a zone -> bot offers subscription with consent prompt.
2. User says yes -> subscription row inserted.
3. On every simulator tick, engine.py calls alert_subscribers(old_states, new_states).
4. For each zone that changed to orange or red:
   - Query subscriptions for that zone.
   - Filter by last_alerted_at > cooldown.
   - Send templated alert via Telegram bot (or log if no bot token).
   - Update last_alerted_at.

---

## 11. Frontend Pages

### Dashboard (default)
- ZoneMap: Leaflet map with coloured GeoJSON polygons.
- Side panel: selected zone detail (count, density, level, forecast, divert).
- AlertFeed: scrolling list of SSE alert events.
- ScenarioSelector: dropdown + start/reset buttons.
- SimBadge: always-visible SIMULATED DATA warning.

### Lost & Found tab
- Form to submit lost/found report.
- Candidate list with score bars.
- Confirm button per candidate.

### ChatSim page (M7)
- Full-page chat UI calling POST /chat.
- Language toggle (EN/HI).
- Location picker for SOS testing.

---

## 12. Deployment (demo / hackathon)

- Run backend with: uvicorn app.main:app --host 0.0.0.0 --port 8000
- Run frontend with: npm run dev (Vite dev server, port 5173)
- Use ngrok for Telegram webhook if no public IP.
- SQLite is ephemeral; reset with scripts/reset_seed.py between demos.

---

## 13. Security & Privacy Notes

- No real pilgrim data. Seed/demo data only.
- chat_id stored only after explicit consent.
- purge_after_mela.py deletes all LostReports, Incidents, Subscriptions.
- Bot token and webhook secret are never committed; live only in .env.
