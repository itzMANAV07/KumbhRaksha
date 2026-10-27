# KumbhRaksha

**A simulated-data crowd-safety prototype for a Kumbh Mela setting.**

KumbhRaksha combines a zone map, a deterministic crowd simulator, density-based risk bands, a short-horizon threshold estimate, adjacent-zone suggestions, chat, SOS incident logging and text-only lost-and-found matching. The browser dashboard must always be read as a demo: counts and facility records are labelled simulated/demo data. It is not connected to live crowd sensors or emergency dispatch.

## Current demo status

- Six sample zones load from `data/zones.geojson`; eight sample facilities load from `data/facilities.json`.
- The backend serves FastAPI REST endpoints and an SSE stream. The React/Leaflet frontend renders the dashboard, chat and lost-and-found pages.
- Telegram long polling is optional. **Do not enable a Telegram token until request logging is redacted and any previously exposed token has been rotated.** The HTTP client emitted a bot API URL containing its token during startup in a local run.
- Subscription consent text exists, but durable subscription creation and proactive alert delivery are incomplete.
- Lost-and-found returns up to three candidates; the documented 0.6 score threshold is not currently enforced by the matching endpoint.
- The technical design and known gaps are in [`docs/TECHNICAL_DESIGN.md`](docs/TECHNICAL_DESIGN.md). The sample data and test inventory are in [`docs/SAMPLE_DATA_AND_TESTS.md`](docs/SAMPLE_DATA_AND_TESTS.md).

## Requirements

- Python with `pip` (the backend dependencies are pinned in `backend/requirements.txt`).
- Node.js and npm (the frontend lockfile is `frontend/package-lock.json`).
- For map tiles, a browser connection to the configured OpenStreetMap tile service. Zone polygons and application controls are local data; base-map tiles are fetched by the browser.

## Setup and run

### 1. Configure the backend

From the repository root, copy the example environment file and edit it if needed. Keep secrets out of Git. Leave the Telegram and Gemini keys empty for a local web-only demo.

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
Set-Location backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**macOS / Linux**

```bash
cp .env.example .env
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The first start creates SQLite tables and seeds zones/facilities from the files under `data/`. The default database URL is relative to the process working directory; when running the backend from `backend/`, the default database file is `backend/kumbh.db`. Keep the same working directory and `DATABASE_URL` when resetting the database. The app currently warns and starts with empty geography if a required file is missing; this behavior should be made a startup validation error before real use.

### 2. Start the frontend

In a second terminal, from the repository root:

```powershell
Set-Location frontend
npm ci
npm run dev -- --host 127.0.0.1
```

The equivalent commands work in a macOS/Linux shell after `cd frontend`. In development, `VITE_API_URL` defaults to `http://localhost:8000`; leave it unset for the local backend. `frontend/.env.example` is for deployments that use a separate backend URL; replace its example URL before using it.

Open:

- Dashboard: <http://127.0.0.1:5173/>
- Chat simulator: <http://127.0.0.1:5173/chat>
- Lost and found: <http://127.0.0.1:5173/lost-found>
- FastAPI interactive docs: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

### Optional reload mode

For code development, add `--reload` to the Uvicorn command. If the reload subprocess fails on your Python/Windows combination, run the single-process command above and restart it after code edits.

## Environment variables

Values are read from the process environment and `.env` files. The backend loads a root `.env` or `backend/.env`. Never commit either file.

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./kumbh.db` | Async SQLAlchemy database URL. Relative SQLite paths resolve from the process working directory. |
| `SIM_TICK_SECONDS` | `5` | Simulator interval in seconds. |
| `ALERT_COOLDOWN_MINUTES` | `10` | Intended cooldown for subscription alerts; full alert delivery is not implemented yet. |
| `GEMINI_API_KEY` | empty | Optional intent-classification fallback. Keyword rules work without it. |
| `TELEGRAM_BOT_TOKEN` | empty | Optional Telegram long-polling adapter. Keep empty until token logging is fixed and the token is rotated. No webhook secret or public tunnel is used. |
| `DASHBOARD_URL` | project default | URL inserted into Telegram website replies. Set it to the actual public frontend URL only for a deployment. |
| `VITE_API_URL` | `http://localhost:8000` in Vite dev | Frontend API base URL. Usually leave unset locally. |

Risk thresholds are currently configured in `backend/app/config.py`: green below 1.0, yellow from 1.0 to below 2.5, orange from 2.5 to below 4.0, and red at 4.0 people/m². These are prototype assumptions, not validated operational limits.

## Demo workflow

1. Open the dashboard and confirm the **SIMULATED DATA** badge is visible.
2. Select `peak_snan_morning` or `evening_aarti`; watch the six sample zone states update.
3. Select a polygon to inspect count, density, level, forecast estimate and adjacent-zone suggestion.
4. Open Chat and ask for a zone's crowd status or diversion suggestion.
5. Use the Lost & Found page with text-only sample reports.
6. For SOS, use `POST /sos` in FastAPI docs with a valid sample location from `data/facilities.json`; the dashboard polls incidents and displays the incident. This logs a demo incident; it does not dispatch responders.
7. Reset the simulator with the dashboard control or `POST /sim/reset`.

Do not present the adjacency suggestion as a verified pedestrian route, the forecast as a stampede prediction, or sample facilities as confirmed/available services.

## Sample data and tests

- Geography and demo facilities: [`data/README.md`](data/README.md), [`data/zones.geojson`](data/zones.geojson), [`data/facilities.json`](data/facilities.json).
- Test modules and the cases they cover: [`docs/SAMPLE_DATA_AND_TESTS.md`](docs/SAMPLE_DATA_AND_TESTS.md).
- Run backend tests from `backend/`:

```powershell
python -m pytest -v
```

For a frontend production bundle, run `npm run build` from `frontend/`. These commands are documented checks; run them before publishing a submission.

## Reset and purge

For a local demo database, run the reset script with the backend as the current directory so the default relative database URL points to the same file as Uvicorn:

```powershell
# From backend/; this drops and recreates all database tables.
python ..\scripts\reset_seed.py
```

The reset is destructive to local database contents. `scripts/purge_after_mela.py` deletes rows from the lost-report, incident and subscription tables; it is a manual script, not a scheduled retention service, and does not erase backups, logs or in-memory chat sessions.

## Project documents

- [`docs/TECHNICAL_DESIGN.md`](docs/TECHNICAL_DESIGN.md) — current architecture, data flow, APIs and limitations.
- [`docs/SAMPLE_DATA_AND_TESTS.md`](docs/SAMPLE_DATA_AND_TESTS.md) — sample-data inventory and test-case index.
- [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md) — target technical specification.
- [`docs/HACKATHON_SUBMISSION_REPORT.md`](docs/HACKATHON_SUBMISSION_REPORT.md) — portal answers, seven-slide plan, edge cases and implementation roadmap.

## Map/data attribution and license

The frontend displays OpenStreetMap attribution for the map tiles. The project data notes identify the zone polygons as traced from OpenStreetMap; confirm exact source/provenance and license obligations before redistribution. See [OpenStreetMap copyright and attribution](https://www.openstreetmap.org/copyright).

The project is released under the MIT License; see [`LICENSE`](LICENSE). Review third-party data and dependency licenses separately.
