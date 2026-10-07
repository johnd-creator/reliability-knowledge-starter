# NADI-INTEGRATION-STATUS-001 — candidate local evidence status

GET `/v1/reliability/integration-status` and GET
`/v1/reliability/assets/{canonical_id}/integration-status` report five independent
components. Data Trust Center and Asset Overview display the same read model.

Availability, collection freshness, source freshness, projection freshness,
identity readiness, quality and coverage are separate fields. CURRENT means the
named evidence dimension meets an explicit policy; it never means healthy
physical equipment. No policy/timestamp means UNKNOWN. Source epoch timestamps
can be STALE while collector/projection timestamps are CURRENT.

The canonical contract is `src/domain/integration_status.py`, exported as
`reliability-data-contracts/schemas/integration-status.schema.json`. Counts are
null when their schema/query is unavailable; real zero remains zero.

## Evidence boundaries

- Maximo: fixed local Collector GET `/sync/status` and `/collect-runs?limit=100`;
  successful completed WO incremental runs, excluding recovery-floor records.
  Unchanged/overlap skips are not errors; the run error count and partial mode
  determine acquisition failure. Missing WO observations within that bounded window remain UNKNOWN. No business
  changedate is treated as collector freshness; source freshness remains UNKNOWN.
- PI: fixed local GET `/integration-observation`, aggregating active local
  registry, stored snapshots and successful snapshot runs. Minimum source time
  detects stale members; future timestamps also have an explicit unknown count. Partial/unknown source coverage prevents CURRENT.
  The new endpoint needs reviewed collector deployment; older APIs report UNKNOWN.
- Mart: registered BSR/IP Asset scope, explicit SELECT-only Mart DSN, factual
  projection state, existing mappings and selected evidence tables. No legacy DSN
  fallback. Schema readiness means read-model compatibility, not migration ledger
  or constraint attestation; controlled migration preflight remains authoritative.
- Mapping coverage counts unique VERIFIED PRIMARY_EQUIPMENT CENTRAL_PI identities.
  Ambiguity cannot win; proposed/retired/other-source mappings cannot contribute.
- Condition coverage includes only currently approved selection/current mapping
  evidence with matching provenance. Retired or ambiguous identities are excluded.
  Stored process values and source payloads never enter this status response.

The API receives the two non-secret collector API bases and three optional
`NADI_*_MAX_AGE_SECONDS` values in both Compose modes. Local observation HTTP
uses fixed paths, bounded bytes/timeouts, no redirects, .netrc or source auth.
No arbitrary plan, attribute proxy or status mutation endpoint exists.

## Acceptance scope

Hermetic tests prove neutral policies, explicit stale/current policies, no
mapping, ambiguity, missing schema/Mart, partial coverage and degraded quality.
This candidate does not deploy condition migration 004, change production
mappings, approve production signals or project production condition evidence.
Phase 1 product acceptance remains blocked, including human crosswalk and
reviewed runtime deployment prerequisites.
