# NADI V1 Product Readiness

## Purpose

This note records the product-hardening boundary for the factual NADI V1
workspaces. It does not add reliability analytics or change Mart, Collector,
Registry, Contract, or source semantics.

## Current product routes

The current navigation remains:

- Executive Overview (`/`)
- Asset Reliability (`/assets`)
- Maintenance (`/maintenance`)
- Maintenance Investigation (`/maintenance/investigation`)
- FMEA (`/fmea`)
- RCFA (`/rcfa`)
- Asset Health (`/asset-health`)
- Overhaul (`/overhauls`)
- Data Trust (`/data-quality`, retained for route compatibility)

No empty PdM Center, Recommendations, or Action Board entry is exposed.

## Product vocabulary

Normal workspaces use NADI product terms: Asset, Registered Reliability Asset,
Work Order, Maintenance Activity, FMEA, RCFA, Asset Health, Overhaul, and Data
Trust Center. Internal identifiers remain secondary evidence where they are
needed for traceability; they are not the primary management labels.

Maturity labels retain their meaning:

- `BUSINESS REGISTRY` — the Reliability Asset product boundary.
- `LOCAL COLLECTOR PROJECTION` — broad local Asset/Maintenance projection.
- `CONTROLLED MART POPULATION` — bounded domain evidence, not asserted as full history.
- `TECHNICAL CONTEXT` — broader technical Equipment context.

## Semantic safety rules

Counts shown in live UI are read from API responses. The UI does not embed the
current Asset, FMEA, RCFA, Asset Health, or Overhaul populations.

Maintenance Activity and Repeat Activity remain factual activity measures.
They are not failure, risk, health, or recommendation scores. The existing
domain evidence boundaries remain in the domain semantics documents.

Raw source statuses are not automatically interpreted as good, bad, complete,
healthy, or risky. The UI uses a `raw-neutral` status mode for current NADI
source statuses. A separate `semantic` mode exists for a future status whose
business meaning is explicitly verified; it is not used to reinterpret the
current domain statuses.

Error states identify the Reliability Mart in user language and preserve the
AppShell/navigation when a page API is unavailable.

## Responsive and accessibility acceptance

The route smoke covers all nine routes with direct HTTP responses and sidebar
href checks. Tables remain inside horizontal overflow frames, filters collapse
at mobile widths, and the sidebar becomes a compact two-column navigation at
small widths. The accepted review widths are approximately 390px, 768px, and
1440px.

Interactive links, buttons, inputs, and selects have visible `:focus-visible`
outlines. Pagination controls have accessible labels. Charts expose a textual
summary/label and visible values; color is not the only signal.

## Known evidence gaps

The following remain intentionally unavailable or semantically gated:

- Repeat Failure, MTBF, MTTR, Availability, Health Score, Wellness Score, Risk Score, and Reliability Score.
- FMEA item-level Failure Mode analytics and RPN.
- RCFA Asset, Work Order, and Failure Event relationships, root-cause taxonomy, and completion KPI.
- Overhaul schedule variance, completion, and progress KPIs.
- PI/DCS-based PdM alerts and recommendation logic.

The Data Trust Center explains that blocked analytics are intentionally withheld
because source evidence or business semantics are not verified; blocked does
not mean that the source system is defective.

## Office-network discovery backlog

Future source/business verification should follow the existing domain notes:
FMEA item semantics; RCFA relationships and action objects; Asset Health
Wellness/ACR/MPI source semantics; Overhaul status, progress, inspection, and
date boundaries; Maintenance failure identity; and the future PI/DCS PdM
model. NADI V1 does not guess these semantics from labels or coincidence.
