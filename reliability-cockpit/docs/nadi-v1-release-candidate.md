# NADI V1 Release Candidate

## Product Identity

NADI — Navigasi Analitik Data dan Informasi
Platform Analitik Keandalan Aset Pembangkit

NADI is an evidence-led product layer over local Reliability Mart evidence. It
is not a replacement for Maximo.

## Release Scope

The V1 factual release-candidate boundary contains:

- Executive Overview (`/`)
- Asset Reliability (`/assets`)
- Maintenance (`/maintenance`)
- Maintenance Investigation (`/maintenance/investigation`)
- FMEA (`/fmea`)
- RCFA (`/rcfa`)
- Asset Health (`/asset-health`)
- Overhaul (`/overhauls`)
- Data Trust (`/data-quality`, retained for route compatibility)

No PdM Center, Recommendations, or Action Board is exposed as an unfinished
product surface.

## Architecture Boundary

```text
MAXIMO → local Collector → Reliability Mart → NADI
```

Current V1 production evidence is primarily Maximo evidence projected through
the local Collector and Mart. PI, DCS, and CEMS are not live NADI integrations
in this release candidate and are not contacted by release QA.

## Data Population Boundary

- `BUSINESS_REGISTRY` — `reliability_asset_registry`, the Registered Reliability
  Asset product boundary.
- `LOCAL_COLLECTOR_PROJECTION` — broad local Asset and Maintenance evidence
  projected from Collector into the Mart.
- `CONTROLLED_MART_POPULATION` — bounded evidence for FMEA, Asset Health, RCFA,
  and Overhaul; it is not asserted to be complete history.
- `TECHNICAL_CONTEXT` — broader technical Equipment context outside the normal
  Registered Reliability Asset population.

Representation is not completion, and a latest record date is not ingestion
freshness.

## Available Analytics

The release candidate exposes only factual or transparent derived surfaces:

- Executive Overview with Registry-scoped Maintenance Activity, bounded trend,
  activity concentration, raw Source Status and Work Type distributions,
  controlled-record availability, and relationship evidence.
- Asset Reliability using Registered Reliability Assets as the business scope.
- Maintenance Activity and Repeat Activity investigation. Repeat Activity is
  not Repeat Failure.
- FMEA header records, source number, raw status, source Failure Code, and
  record recency. Item-level failure-mode details remain deferred.
- Asset Health assessment records, raw lifecycle status, source text, and
  assessment record recency. No numerical Health Score is inferred.
- Global RCFA records, raw status/category, and record recency. Asset,
  Work Order, and Failure Event relationships remain unresolved.
- Overhaul records with factual Work Order relationship evidence, Asset
  resolution only through the verified Work Order path, planned/actual dates,
  and raw Source Progress.
- Data Trust Center with population maturity, domain evidence, relationship
  readiness, and semantic readiness.

## Intentionally Blocked Analytics

The following are intentionally withheld because required source evidence or
business semantics are not verified:

- Repeat Failure
- MTBF, MTTR, and Availability
- Health Score, Wellness Score, Risk Score, and Reliability Score
- FMEA Failure Mode analytics and RPN
- RCFA Asset/work-order relationship, root-cause taxonomy, and completion KPI
- Overhaul schedule variance, completion, and performance KPIs
- PdM alerts and Recommendations

## Known Limitations

- IPFMEAITEM semantics are not verified.
- RCFA Asset, Work Order, and Failure Event relationships are unresolved.
- Asset Health numerical Wellness/Health source semantics are unavailable.
- Repeat Failure identity and failure-code business semantics are unavailable.
- Overhaul KPI semantics, including progress scale and schedule meaning, are
  incomplete.
- PI/DCS PdM is not implemented in the NADI decision model.
- Sync freshness is not available in the current Cockpit evidence model;
  business-record dates are shown with domain-specific date bases instead.
- Controlled domain populations must not be described as complete history.

## Version Convention

The backend package, frontend package, lockfile root, and FastAPI application
currently align on application version `0.1.0`. No separate NADI version source
is necessary for this release freeze. The recommended future Git release
convention is `v0.1.0-rc.1`; no Git tag is created by this task.

## Security / Safety

- NADI product reads local Reliability Mart evidence; no release QA source
  discovery or source-system write is permitted.
- Maximo, Collector, Mart, Registry, FMEA, RCFA, Asset Health, and Overhaul
  populations are not mutated by this release task.
- No production report or raw production payload is committed.
- NADI normal pages do not surface PII fields such as reporter, lead, or
  supervisor information.
- Canonical/internal identifiers remain secondary technical evidence.
- Raw statuses and unresolved relationships are not fabricated into business
  conclusions.

## Release Acceptance

The checklist below is the evidence gate for this factual V1 release candidate
and is updated by the release-freeze task:

- [PASS] Active branch is `task/nadi-002-asset-reliability-workspace`.
- [PASS] Upstream tracking ref matches the local release-freeze HEAD.
- [PASS] Only the explicitly allowed local production report remains untracked.
- [PASS] No source-system requests or writes are used by release QA.
- [PASS] No new reliability analytics or semantic widening is introduced.
- [PASS] Product vocabulary and hardcoded-live-count checks pass.
- [PASS] Backend hermetic suite passes.
- [PASS] Frontend typecheck and production build pass.
- [PASS] Development and production route smoke pass for all nine routes.
- [PASS] Reliability Contract schemas validate without changes.
- [PASS] Secret/privacy audit and `git diff --check` pass.
- [PENDING] Separate release PR, mainline integration, and release tagging task.

This document certifies a tested factual release boundary, not a claim that
the future reliability platform is complete.
