# KumbhRaksha - Agent Operating Manual

Read this file first before touching any code. Every AI agent working in this
repo must follow the rules here. Humans should read Sections 1-5 before
starting a session.

---

## Section 1 - Project Purpose

KumbhRaksha is a real-time crowd-safety system for the Kumbh Mela pilgrimage.
It monitors crowd density across ghat zones, predicts risk, routes pilgrims away
from dangerous areas, and provides a Telegram / web chat interface in Hindi and
English. All data shown to users is clearly labelled SIMULATED DATA.

---

## Section 2 - Non-Negotiable Rules

1. Never fabricate coordinates. All GeoJSON must come from data/zones.geojson
   or data/facilities.json. If a required field is missing, raise a validation
   error; never invent a value.
2. No PII stored beyond the Mela window. Every report with personal data must
   be deleted by the scripts/purge_after_mela.py job.
3. Consent before subscription. Never store a chat_id for proactive alerts
   without an explicit yes / haan reply to the consent prompt.
4. LLM is optional. Every chat intent must have a keyword-rule fallback. If
   Gemini times out or returns invalid JSON, fall back to the template menu
   immediately - do not retry or block.
5. SOS path never touches the LLM. The keywords help, sos, bachao, madad must
   be handled in pure Python before any LLM call is attempted.
6. Lite mode cap. Any response on the /lite path must be <= 200 characters,
   plain text, no buttons, no media.
7. SIMULATED DATA badge. The dashboard must display a visible SIMULATED DATA
   badge at all times.
8. Tests before merge. Every module listed in Section 7 must have corresponding
   pytest tests. CI must pass before merging to main.

---

## Section 3 - Technology Choices (pinned after M0 install)

Layer       | Library                       | Notes
------------|-------------------------------|---------------------------
Backend     | FastAPI                       | async, with lifespan
DB          | SQLite via SQLAlchemy 2 async | file kumbh.db
Validation  | Pydantic v2                   | strict mode where noted
Simulator   | Pure Python + asyncio         | no external deps
Frontend    | React 19 + Vite               | TypeScript
Map         | Leaflet + react-leaflet       | no Mapbox key required
Chat        | python-telegram-bot v21       | webhook mode
LLM         | google-generativeai (Gemini)  | optional, timeout 3 s
Tests       | pytest + pytest-asyncio       |

Pin exact versions in backend/requirements.txt and frontend/package.json
after first install.

---

## Section 4 - Dev Workflow

    # Start backend
    cd backend && uvicorn app.main:app --reload --port 8000

    # Start frontend
    cd frontend && npm run dev

    # Run tests
    cd backend && pytest -v

    # Reset seed data
    python scripts/reset_seed.py

Health check: GET http://localhost:8000/health -> {"status":"ok"}

---

## Section 5 - Environment Variables

All secrets live in .env (gitignored). Copy .env.example and fill in.

Variable                  | Required | Description
--------------------------|----------|------------------------------------------
TELEGRAM_BOT_TOKEN        | Yes (M7) | From BotFather
TELEGRAM_WEBHOOK_SECRET   | Yes (M7) | Random string
GEMINI_API_KEY            | No       | Falls back to keyword rules if absent
DATABASE_URL              | No       | Defaults to sqlite+aiosqlite:///./kumbh.db
SIM_TICK_SECONDS          | No       | Simulator tick interval, default 5
ALERT_COOLDOWN_MINUTES    | No       | Per-user alert cooldown, default 10

---

## Section 6 - Repository Structure

    KumbhRaksha/
    |- AGENTS.md                  <- this file
    |- docs/
    |  `- BLUEPRINT.md            <- full technical specification
    |- .env.example
    |- data/
    |  |- zones.geojson           <- traced by Person B in M1
    |  `- facilities.json         <- demo facilities, labelled demo:true
    |- backend/
    |  |- requirements.txt
    |  `- app/
    |     |- main.py              <- FastAPI app, lifespan, /health
    |     |- config.py            <- thresholds, env vars
    |     |- database.py          <- SQLAlchemy async engine
    |     |- models.py            <- ORM models
    |     |- schemas.py           <- Pydantic schemas
    |     |- routers/
    |     |  |- zones.py          <- GET /zones, GET /zones/{id}
    |     |  |- chat.py           <- POST /chat
    |     |  |- sos.py            <- POST /sos
    |     |  |- lost_found.py     <- POST /report, GET /matches
    |     |  `- events.py         <- GET /events (SSE)
    |     |- sim/
    |     |  |- engine.py         <- simulator loop
    |     |  `- scenarios.py      <- named scenario definitions
    |     |- risk.py              <- density -> level -> forecast
    |     |- chat/
    |     |  |- intent.py         <- keyword rules + optional Gemini
    |     |  `- templates.py      <- Hindi / English reply templates
    |     |- matching.py          <- lost-and-found scoring
    |     |- sos.py               <- SOS handling, nearest facility
    |     `- adapters/
    |        `- telegram.py       <- Telegram webhook adapter
    |- backend/tests/
    |  |- test_risk.py
    |  |- test_matching.py
    |  |- test_chat.py
    |  |- test_sim.py
    |  `- test_sos.py
    |- frontend/
    |  |- package.json
    |  |- vite.config.ts
    |  |- index.html
    |  `- src/
    |     |- main.tsx
    |     |- App.tsx
    |     |- pages/
    |     |  |- Dashboard.tsx     <- map + side panel + alert feed
    |     |  |- LostFound.tsx     <- lost and found tab
    |     |  `- ChatSim.tsx       <- web chat simulator (M7 fallback)
    |     |- components/
    |     |  |- ZoneMap.tsx
    |     |  |- AlertFeed.tsx
    |     |  |- ScenarioSelector.tsx
    |     |  `- SimBadge.tsx      <- SIMULATED DATA badge
    |     |- hooks/
    |     |  `- useSSE.ts         <- SSE subscription hook
    |     `- api/
    |        `- client.ts         <- typed fetch wrappers
    `- scripts/
       |- reset_seed.py
       `- purge_after_mela.py

---

## Section 7 - Module Specifications

### 7.1 Simulator (sim/engine.py)

- Runs as an asyncio background task started in the FastAPI lifespan.
- Maintains an in-memory dict zone_state: dict[str, ZoneState].
- On each tick (default 5 s) applies the active scenario delta functions to
  each zone count.
- Emits an SSE event after every tick.
- Exposes set_scenario(name) and reset() coroutines.

### 7.2 Risk Engine (risk.py)

    density (p/m2) = count / area_m2
    level:
      green  -> density < 1.0
      yellow -> 1.0 <= density < 2.5
      orange -> 2.5 <= density < 4.0
      red    -> density >= 4.0

### 7.3 Forecast (risk.py - forecast_minutes)

    net_rate = (count_now - count_prev) / tick_seconds   # people/second
    if net_rate <= 0: return None
    minutes_to_red = (red_threshold * area_m2 - count_now) / (net_rate * 60)
    return minutes_to_red if minutes_to_red < 30 else None

### 7.4 Divert Selection (risk.py - suggest_divert)

Return the adjacent zone with the lowest density and level != red.
If all adjacent zones are red, return None (no safe divert).

### 7.5 Lost and Found (matching.py)

Score = 0.4 x clothing_match + 0.3 x age_match
      + 0.2 x location_proximity + 0.1 x time_proximity

Match threshold: 0.6. Return top-3 candidates sorted by score desc.

- clothing_match: 1.0 if identical colour+garment, 0.5 if colour only, 0.0 otherwise.
- age_match: 1.0 if |age_lost - age_found| <= 2, else max(0, 1 - |diff|/10).
- location_proximity: 1.0 if same zone, 0.5 if adjacent, 0.0 otherwise.
- time_proximity: 1.0 if |t_lost - t_found| <= 1 h, else max(0, 1 - hours/6).

### 7.6 SOS (sos.py)

1. Detect SOS keywords before any LLM call.
2. Extract lat/lon from Telegram location pin or /sos lat,lon text.
3. Find nearest facility from data/facilities.json (Haversine distance).
4. Create an Incident record (status=open).
5. Reply with facility name, distance, and a Google Maps link.
6. Emit SSE event with incident data.

---

## Section 8 - Risk Thresholds (from config.py)

    DENSITY_GREEN  = 1.0   # p/m2
    DENSITY_YELLOW = 2.5
    DENSITY_ORANGE = 4.0
    DENSITY_RED    = 4.0   # >= red
    FORECAST_WINDOW_MINUTES = 30
    ALERT_COOLDOWN_MINUTES  = 10
    SIM_TICK_SECONDS        = 5

---

## Section 9 - Chat Intent Taxonomy

Intent       | Keywords (EN)                    | Keywords (HI)
-------------|----------------------------------|-----------------------
crowd_status | crowd, density, safe, zone, ghat | bheed, ghat, surakshit
divert       | go, route, avoid, alternate      | jayen, rasta, bachen
lost_person  | lost, missing, child, separated  | khoya, gum, baccha
found_person | found, person, wandering         | mila, vyakti
sos          | help, sos, emergency             | bachao, madad
subscribe    | alert, notify, subscribe         | suchna, alert
unsubscribe  | unsubscribe, stop, off           | band, roko
lite         | /lite                            | /lite
menu         | hi, hello, start, help           | namaste, shuru

---

## Section 10 - Subscriptions

- Table: subscriptions(chat_id, zone_id, language, created_at, last_alerted_at)
- Consent: before inserting, send consent prompt and wait for yes/haan.
- On each simulator tick, compare old vs new level for each zone. If a zone
  changed to orange or red, find all subscribers for that zone whose
  last_alerted_at is > ALERT_COOLDOWN_MINUTES ago and send one alert.
- Unsubscribe command removes the row; send confirmation.

---

## Section 11 - Lite Mode

Triggered by /lite command or if the user previously sent /lite in this
session. All replies must be <= 200 characters, plain text, no InlineKeyboard,
no media. Store lite=True in the session dict keyed by chat_id.

---

## Section 12 - Contribution Rules (for AI agents)

1. Read this file and docs/BLUEPRINT.md before writing any code.
2. Match the structure in Section 6 exactly. Do not create files outside the
   listed paths without updating this file and the blueprint.
3. No invented coordinates or data. If a GeoJSON file is missing, raise
   FileNotFoundError with a clear message; never use placeholder coordinates.
4. Template-only replies. Chat responses must come from chat/templates.py
   filled with real DB values. No free-form LLM text to users.
5. Pydantic strict validation. Every external input (GeoJSON, Telegram payload,
   LLM JSON response) must pass a Pydantic model before use.
6. One alert per level change per user per cooldown window.
7. SOS is synchronous. The SOS handler must return a reply within 2 s; never
   await an LLM call inside it.
8. Update requirements.txt with pinned versions after every pip install.
9. Run pytest -v before marking any milestone done.
10. Commit message format: [Mn] short description where n is the milestone number.

### FREE-ONLY AND PRIVACY

17. Use only the free and open-source tools listed in Section 5. If a service
    needs a payment card, a paid tier, or an unverified signup, stop and ask
    the team before proceeding.
18. Do not call an external LLM during lost-and-found or SOS flows. For all
    other messages, strip digits from the user text before any LLM call. The
    app must work end-to-end with GEMINI_API_KEY unset.
19. Telegram runs in long-polling mode only. Do not generate webhook URLs, do
    not require a public IP or ngrok tunnel, and do not call setWebhook.
20. No face recognition, photo matching, or biometric data of any kind. The
    lost-and-found system uses text descriptors only (age, clothing colour,
    garment type, zone, time).

---

## Section 13 - Demo Script

Rehearse twice before the presentation. Keep a phone charged with Telegram.
Have the web ChatSim open as fallback.

1. Open the dashboard - show the map with zone polygons and the SIMULATED DATA badge.
2. Select scenario peak_snan_morning - watch zones turn yellow then orange.
3. Alert feed - point out the forecast alert Zone X will reach RED in ~N min.
4. Zone turns red - show the divert suggestion in the side panel.
5. Telegram chat (or ChatSim) - type Har Ki Pauri pe kitni bheed hai? and
   show the crowd-status reply in Hindi.
6. SOS demo - type help or drop a location pin, show the incident appear on the
   map and the nearest facility reply.
7. Lost and found - submit a lost-child report via the dashboard tab, then a
   found-person report, show the match with score >= 0.6.
8. Reset - press the Reset button, show all zones return to green.
