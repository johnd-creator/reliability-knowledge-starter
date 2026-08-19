# CONTEXT — Start Here (for AI tools & humans)

> Entry point for `pi-knowledge`. Read this first, then [`AGENTS.md`](./AGENTS.md).

## 1. What this is

`pi-knowledge` is a **read-only** knowledge base for the organization's PI Web API
(AVEVA / OSIsoft). It is **not an application**. It records *what PI data is
available, how to read it safely, and what it means* so a downstream app can pull
PI data without ever mutating production.

### Hard rules (non-negotiable)
- **READ ONLY.** No state-changing calls. Never create/update/delete PI Points,
  AF Elements, Attributes, analyses, event frames, or configuration.
- No brute-forcing WebIds or tag names.
- No storing credentials, cookies, NTLM/Kerberos artifacts, tokens, or session data.
- Save sanitized samples only.
- Record **units of measure** and **data type** with every discovered point/attribute.

Enforced in code by `scripts/discover_pi.py` (GET / HEAD / OPTIONS only).

## 2. Current maturity

## 2. Current maturity (instance-verified 2026-08-14)

- Server: `pivision.plnindonesiapower.co.id/piwebapi`, authenticated via Basic
  auth (`PI_USERNAME`/`PI_PASSWORD`). Reachability `verified` (HTTP 200).
- `discovery/endpoints.json`: **16 resources catalogued** (2026-08-18 re-probe):
  10 core endpoints `verified` (system, dataservers, points, point-by-path,
  stream-value, stream-recorded, stream-interpolated, assetdatabases,
  elements, attributes) plus **stream-plot `verified` (NEW)**,
  **stream-end `verified` (NEW)**, system-versions `verified`,
  streamsets `verified-empty` (200 but Items=[] — unusable here),
  batch `forbidden` (POST-only; read-only policy), system-status `forbidden` (401).
- `discovery/capabilities.json`: snapshot, recorded, interpolated, summary,
  plot, end all **verified**. OMF controller exists — write channel, forbidden.
  QUIRK: `selectedFields` query param returns `{}` on this instance — do not use.
- `discovery/dataservers.json`: **2 data servers verified** (`PI1`, `pi2`).
- `discovery/points.json`: sample point catalog (bearing/vibration tags, PI1).
- `discovery/attributes.json`: **541 verified AF attributes** across all BSR1
  systems (Boiler 358, NPHR 100, Turbine 71, Generator 12). 150 carry units.
- `mappings/bsr1-parameters.yaml`: **541 discovered BSR1 attributes**, including
  **150 semantically reviewed mappings** and **391 retained as `unclassified`**
  until their business meaning is reviewed. All entries carry their WebId and
  current stream health; 433 are currently collectable.
- `discovery/bsr1-key-parameters.json`: live snapshots for 21 reliability-critical
  attributes (Generator 498.5 MW, Speed 3003 rpm, bearing vibrations, etc.).
- `discovery/stream-verification.json`: **stream health for all 541 attributes**
  (verified 2026-08-14): 433 ok, 98 gone, 10 error. In the 150 reviewed
  mappings: 93 ok, 57 broken.
- **Key finding 1:** units are `null` at the PI Point level but present at the AF
  Attribute level (`DefaultUnitsName`). Map reliability parameters from AF
  **attributes**, not raw points.
- **Key finding 2 (dead references):** AF attributes can outlive their PI Points.
  98 attributes return **HTTP 410 "PI Point not found"** — the point named in
  the attribute's ConfigString was deleted/renamed on PI1 (e.g.
  `BSR1.Generator.Field Current` is gone; the working equivalent is
  `BSR1.Generator.Excitation Field Current`). The attribute's WebId stays valid
  in AF listings, so staleness is only visible when querying `/streams/...`.
  Broken entries are marked `status: broken` / `stream_status: gone` in the
  mapping and excluded by the collector. Data server `pi2` is disconnected
  (502) and holds no BSR1 points.

## 3. How to run discovery (operators only, when access is authorized)

```bash
# Offline: regenerate the documented endpoint catalog (no network)
python scripts/discover_pi.py --documented

# Reachability probe (GET / only, explicit --execute)
python scripts/discover_pi.py --probe-system --execute
```

Network access is opt-in via `--execute`. Credentials come from the environment
(`PI_USERNAME`/`PI_PASSWORD` for Basic auth, or `PI_TOKEN` for Bearer), are
used only in the request, and are never logged or saved.

Full command set (all need `--execute` for network):
```bash
python scripts/discover_pi.py --probe-system    --execute   # GET /
python scripts/discover_pi.py --list-dataservers --execute   # GET /dataservers
python scripts/discover_pi.py --list-points --server PI1 --name-filter '*BEARING*' --max-count 30 --execute
python scripts/discover_pi.py --point  --path '\\PIServers[PI1]\ADP1.BEARING #1 OIL TEMP' --execute
python scripts/discover_pi.py --stream-value    --webid <id> --execute
python scripts/discover_pi.py --stream-recorded  --webid <id> --start '*-1d' --end '*' --max-count 5 --execute
```

## 4. Status vocabulary

- `unknown` — not tested
- `documented` — present in the public PI Web API docs, not verified on this instance
- `verified` — tested successfully with authorized read-only access
- `forbidden` — endpoint exists but access is denied

Treat only `verified` records as a reliable contract.

## 5. Repository map

| Path | What it is |
|---|---|
| `CONTEXT.md` | this entry point |
| `AGENTS.md` | safety rules + preferred discovery order |
| `discovery/endpoints.json` | PI Web API endpoint catalog (16 resources; 12 verified, 2 forbidden, streamsets unusable) |
| `discovery/{dataservers,points,attributes}.json` | verified discovery data |
| `discovery/capabilities.json` | verified stream capabilities |
| `samples/stream-value.sample.json` | verified snapshot sample |
| `docs/authentication.md` | auth notes |
| `docs/hierarchy.md` | AF element/attribute hierarchy conventions |
| `docs/unit-specific.md` | site/unit tag naming (e.g. BSR) |
| `schemas/parameter.schema.json` | parameter contract |
| `mappings/parameter.example.yaml` | tag → semantic parameter mapping |
| `scripts/discover_pi.py` | read-only discovery CLI |

## 6. Link to downstream consumers

The reliability cockpit (`../reliability-cockpit`) has a PI adapter placeholder
(`src/adapters/pi/`) that will consume *verified* records from this repository.
Do not wire the cockpit to `documented`/`unknown` entries — verify first.
