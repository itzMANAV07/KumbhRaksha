# Sample Data and Test Cases

This file indexes the checked-in demo inputs and automated test modules for submission reviewers. Geographic data are not reproduced here; use the repository files as the source of truth. All facilities are marked `demo: true`, and simulator counts are generated at runtime.

## Sample data

### Zones

Canonical source: [`../data/zones.geojson`](../data/zones.geojson). The current file contains six polygon features; each includes an ID, name, area, assumed capacity, adjacency list and geometry.

| ID | Name | Area (m²) | Assumed capacity | Adjacent zone IDs |
|---|---|---:|---:|---|
| `har-ki-pauri` | Har Ki Pauri | 12,000 | 40,000 | `brahmakund`, `ganga-ghat-upper` |
| `brahmakund` | Brahmakund | 8,000 | 25,000 | `har-ki-pauri`, `subhash-ghat` |
| `ganga-ghat-upper` | Ganga Ghat (Upper) | 15,000 | 35,000 | `har-ki-pauri`, `moti-bazaar` |
| `subhash-ghat` | Subhash Ghat | 10,000 | 30,000 | `brahmakund`, `moti-bazaar`, `railway-road` |
| `moti-bazaar` | Moti Bazaar | 20,000 | 50,000 | `ganga-ghat-upper`, `subhash-ghat`, `railway-road` |
| `railway-road` | Railway Road Entry | 18,000 | 45,000 | `subhash-ghat`, `moti-bazaar` |

Areas, capacities and links are assumptions in sample data. Verify them with the relevant authorities before operational use. Never add coordinates by hand; edit only from verified source data and keep the required source/license attribution.

### Facilities

Canonical source: [`../data/facilities.json`](../data/facilities.json). It has eight records, all marked `demo: true`:

| ID | Sample name | Type | Zone ID |
|---|---|---|---|
| `med-hkp-1` | Medical Post – Har Ki Pauri | medical | `har-ki-pauri` |
| `med-bk-1` | Medical Post – Brahmakund | medical | `brahmakund` |
| `police-hkp-1` | Police Post – Har Ki Pauri Main | police | `har-ki-pauri` |
| `police-sg-1` | Police Post – Subhash Ghat | police | `subhash-ghat` |
| `lost-found-mb-1` | Lost & Found Centre – Moti Bazaar | lost_found | `moti-bazaar` |
| `toilet-ggu-1` | Toilet Block – Upper Ghat | toilet | `ganga-ghat-upper` |
| `water-rr-1` | Water Point – Railway Road | water | `railway-road` |
| `hospital-main` | District Hospital – Emergency | hospital | `railway-road` |

The exact coordinate pairs are maintained only in the JSON source file. Names and locations are demo inputs and are not confirmation that a service exists or is open.

### Simulator fixtures

The simulator has four scenario keys in `backend/app/sim/scenarios.py`:

- `calm` — default, gentle deterministic count drift.
- `peak_snan_morning` — faster illustrative growth across the six zones.
- `evening_aarti` — alternate illustrative growth pattern.
- `stampede_risk` — stress scenario that increases all sample zones rapidly.

Counts are not sourced from real-time observations. Seed counts currently use 10% of zone area, not the sample capacity field.

## Test inventory

Run from `backend/` with `python -m pytest -v`. The repository currently has five focused pytest modules (40 test functions by inspection); this inventory is not a report that they were run or passed.

| Test module | Existing cases |
|---|---|
| [`test_risk.py`](../backend/tests/test_risk.py) | Density calculation; zero-area error; green/yellow/orange/red boundaries; positive and zero-rate forecast; safest adjacent zone; no non-red adjacent zone. |
| [`test_matching.py`](../backend/tests/test_matching.py) | Exact clothing and color-only match; clothing mismatch; near/far age; same/adjacent location; time proximity; one high- and one low-score pair. |
| [`test_chat.py`](../backend/tests/test_chat.py) | English/Hindi crowd intent; divert; lost; SOS keywords; menu fallback; ticket/facility keywords; language switch; zone name mapping; transliterated/regional SOS; website intent. |
| [`test_sim.py`](../backend/tests/test_sim.py) | Scenario tick changes a count; reset restores seed count; tick emits an event. |
| [`test_sos.py`](../backend/tests/test_sos.py) | English/Hindi SOS detection; non-SOS text; Haversine same/roughly-near points; nearest facility; reply link; no facilities. |

Tests use inline dictionaries and synthetic reports for scoring; geographic examples are read from the project data files during application startup. No test fixture should introduce invented geographic coordinates.

## Important coverage gaps before submission

- No full API integration tests for lifespan seeding, missing/malformed files, status codes, invalid coordinates or database failures.
- No browser/component tests, frontend build result, Telegram polling/consent tests, SSE reconnect tests, or end-to-end demo automation are represented by these five modules.
- Risk tests do not cover every exact boundary of the 30-minute forecast, invalid tick duration, negative/non-finite counts, or stale event behavior.
- Matching tests do not verify the route-level 0.6 cutoff, top-three tie ordering, duplicate/self matches, status transitions, authorization or timezone edge cases.
- Subscription consent/persistence, cooldowns, unsubscribe and post-Mela purge verification are not covered.
- Add tests alongside implementation changes, and run the required suite/build before claiming a submission-ready result.
