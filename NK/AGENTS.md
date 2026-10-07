# AGENTS.md — NK (Nilai Kalor prediction)

Read `../AGENTS.md` first, then `README_WebApp.md` and `PI_MAPPING.md`.

## Mission and stack

Continue the existing Streamlit coal calorific value predictor with manual
and PI Collector input. Reuse pandas, scikit-learn, joblib and the existing
model/scaler artifacts. The entrypoint is `nk_web_app.py`; PI input validation
is in `pi_input.py`, the panel is in `pi_panel.py`, and persisted mapping
configuration is in `pi_feature_mapping.json`.

## No new database or collector

- NK **has no application database**. Do not add Postgres, SQLite persistence,
  a DB container, SQL credentials, or a duplicate PI collector for this feature.
- Manual mode uses sliders/CSV. PI mode reads already stored collector data
  via `GET /attributes` and `GET /snapshots?limit=5000`. It must not call PI
  production, trigger collection or run a historical backfill.
- Host-local `PI_COLLECTOR_API_BASE` defaults to `http://127.0.0.1:8001`.
  A future container deployment must use a reachable collector service address;
  do not assume container localhost is the host. Reuse the existing API.
- Optional NK `.env` contains API base and validation limits only. Preserve
  existing env files; do not put passwords in API URLs or copy source secrets.
- Prediction history is session-local, bounded to 50 distinct PI batches with
  JSON export. Mapping JSON is configuration, not a new time-series store.
  Permanent prediction storage would need a separate explicit design request.

## Feature mapping and prediction integrity

1. Preserve all 13 training features, their exact names/order, and the
   compatible model/scaler pair. Do not retrain or replace artifacts incidentally.
2. Candidate PI tags are search hints, not approved training-feature mappings.
   Use registry `verified` / stream `ok` identities and explicit evidence for
   feature meaning, source units and training units. Initial mappings are
   `unknown`; do not silently mark them verified or invent tag identifiers.
3. **PS = pemakaian sendiri**, confirmed by the user. Exact tag and whether
   training/source values use W or MW are unconfirmed. It is not confirmed as
   a percentage. Auxiliary power candidates must not be summed automatically.
4. SFC needs an approved source or formula. APH inlet and outlet temperatures
   are different measurements; do not substitute based on a similar tag name.
5. On every PI refresh validate identity, finite numeric values, quality flags,
   units, timezone-aware timestamps, source age and inter-feature time skew.
   Defaults: max age 900s, max skew 300s, refresh 60s; see `.env.example`.
6. Missing, stale, questionable, substituted, or invalid inputs block automatic
   predictions. Never silently fall back to manual values, zero or dummy data.
   Switching input modes must not display a previous mode's result as current.
7. Preserve supported unit conversions and do not infer gauge/absolute pressure
   conversions or derived features without evidence. Successful integration
   does not validate production prediction accuracy.

## Current source handoff

As of 2026-10-07 PI source authentication returned HTTP 401. The user explicitly
asked to skip credentials for now. Do not retry authentication or enable root
Compose's `pi-collection` profile until the user requests resumption. Stored
collector data remains readable; its age may correctly block NK PI prediction.
Manual mode remains available independently.

## Run and check

NK runs separately from the root Compose services. Check for an existing
Streamlit process first, reuse the existing venv, and run from `NK/`:

```bash
.venv/bin/streamlit run nk_web_app.py --server.address 127.0.0.1 --server.port 8501
MPLCONFIGDIR=/tmp/nk-matplotlib .venv/bin/python -m unittest discover -s tests
```

Tests use local fakes and temporary fixtures; no production calls or operational
DB are needed. Inspect dependencies in `requirements.txt` before changing the
environment. Keep tests for missing/invalid/stale input and mode switching
hermetic, and preserve unrelated model/data files and workspace changes.
