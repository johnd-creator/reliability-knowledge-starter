# NADI Product Foundation

## Identity

**NADI** means **Navigasi Analitik Data dan Informasi**. Its positioning is
**Platform Analitik Keandalan Aset Pembangkit**.

NADI reads the Reliability Mart to make factual asset-reliability information
understandable. It is not a Maximo replacement, a generic enterprise
dashboard, or a source-system discovery tool.

## Product boundary

The Maximo Collector remains the engineering surface for collection status,
allowlisted source projections, canonical mapping, provenance, and Mart
inspection. NADI is the reliability-user surface for assets, maintenance,
FMEA, RCFA, asset health, overhaul, and relationship integrity.

NADI does not start collection, call Maximo, expose raw OSLC, or expose raw
Mart SQL. Its frontend uses the existing read-only `/v1/reliability` API.

The supplied NADI logo is used by the application shell. Light theme is the
default presentation; users can switch to the dark technical theme from the
top bar, and the preference is retained locally in the browser.

## Navigation architecture

| Route | Purpose |
| --- | --- |
| `/` | Overview of factual Reliability Mart counts and integrity |
| `/assets` | Canonical asset list with server-side filters and pagination |
| `/maintenance` | Maintenance event list |
| `/fmea` | FMEA assessment list |
| `/rcfa` | RCFA list with an explicit unresolved asset relationship |
| `/asset-health` | Factual Asset Health assessment workspace without a numerical health score |
| `/overhauls` | Overhaul list, including unresolved asset references |
| `/data-quality` | Canonical reference resolution summary |

The current operating scope is BSR / IP. NADI does not provide a site
switcher; the backend contract authorizes this scope only.

## Data and controlled-load language

NADI has **mixed data maturity**. Asset and Maintenance data are the current
local Collector projection, while FMEA, RCFA, Asset Health, and Overhaul are
current controlled Mart populations. NADI presents factual counts as records
available in those populations; it does not call them complete history or full
plant population.

The Executive Overview and Asset Health workspace use bounded read aggregates
and explicitly label metric evidence. Asset Health record age means record
recency only. NADI intentionally does not fabricate MTBF, MTTR, availability,
risk, health, wellness, or reliability scores.

## Relationship semantics

RCFA-to-asset remains unresolved in Contract v1. NADI does not add an Asset
column to RCFA through inference and does not allow an asset filter for RCFA.
The UI uses neutral language: **Asset relationship not mapped**.

Overhaul rows can also have no `asset_ref`. They remain visible and display
**Asset unresolved** rather than inventing a link.

Data Quality reports resolved and unresolved asset/work-order references. An
unresolved reference may point outside the bounded initial sample; it is not
automatically a source-data defect.

## Future boundaries

Asset context, timeline, KPI design, PI/DCS/CEMS views, authentication/RBAC,
ML, anomaly detection, and predictive recommendations are intentionally
outside NADI-001. The next product increment is NADI-002: Asset Reliability
Workspace & Asset Detail.
