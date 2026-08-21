# NADI Asset Reliability Workspace

## Information architecture

The Asset Reliability page (`/assets`) is the entry point for the first
asset-centered NADI workflow. A business-readable asset number opens
`/assets/{canonical_id}`. The detail page can be refreshed or opened directly
and keeps the canonical identity available as secondary technical context.

The workspace tabs are:

- **Overview** — current asset facts, asset-scoped Mart totals, bounded recent
  context, latest Asset Health, and a neutral relationship note.
- **Timeline** — newest-first evidence from Maintenance, FMEA, Asset Health,
  and Overhaul.
- **Maintenance** — paginated asset-filtered maintenance events.
- **FMEA** — paginated asset-filtered assessments. IPFMEAITEM detail remains
  deferred.
- **Asset Health** — paginated asset-filtered health assessments.
- **Overhaul** — paginated overhaul records with a proven Asset relationship.

## API usage

The frontend uses the existing read-only `/v1/reliability` API. Overview uses
the bounded asset context endpoint and `limit=1` asset-filtered requests for
Maintenance, FMEA, Asset Health, and Overhaul totals. Totals always come from
`meta.total`; bounded recent context list lengths are not treated as totals.

Full tabs use server-side pagination with a default page size of 50. Timeline
events use the backend event types `MAINTENANCE`, `FMEA`, `ASSET_HEALTH`, and
`OVERHAUL`. Events with a null timestamp remain visible as **Date
unavailable**.

## Relationship boundaries

RCFA is intentionally absent from the Asset workspace. Contract v1 still
marks the RCFA-to-Asset relationship as unresolved, so NADI does not create a
tab, count, timeline event, or inferred link for it.

Overhaul rows with `asset_ref = null` remain visible on the global Overhaul
page but are not attached to any Asset detail page.

The context endpoint's relationship health is a **Dataset Reference Health**
aggregate. It is never presented as an Asset health, reliability, risk, or
criticality score.

## Mixed data maturity limitation

The current Reliability Mart has mixed data maturity. Asset-specific tabs show
only relationships resolved to the selected Asset in the current Mart. Empty
Maintenance, FMEA, Asset Health, or Overhaul states are factual and do not
imply that the source system has no corresponding history.

## MX-012R local projection

NADI Asset Reliability is scoped to the current `reliability_asset_registry`
projection. The technical `asset_master` table remains available to the Mart
as relationship context, but its larger count is not presented as the NADI
business Asset population.

Maintenance is likewise Registry-scoped in normal NADI views. Its date query
uses the actual start when available and falls back to `source_changed_at` for
local Collector history whose optional actual timestamps were not retained.

MX-012R does not alter FMEA, RCFA, Asset Health, or Overhaul source semantics.
RCFA remains independent because its Asset relationship is unresolved. An
Overhaul with no resolved Asset remains visible globally but is not attached to
an Asset workspace.

The current Mart is mixed maturity: Asset and Maintenance are local Collector
projections, while other reliability domains remain within their controlled
Mart population. This is disclosed in the Overview and is not a claim of
complete plant history.

## Future extension points

The workspace can later add verified PI/DCS condition trends and other
read-side evidence without changing the Asset identity or tab model. KPI,
risk, health-score, authentication, and source-collection work remain outside
this product increment.
