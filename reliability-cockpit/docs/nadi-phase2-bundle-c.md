# Bundle C — non-operational integrated candidate

Baseline: main `7a846ef2c7e25306f23da99dd011e1d54aa8f4a4`, containing merged
Bundle B PR30–36 and the method-extension parity correction. Phase1 CURRENT/PARTIAL.
No deployment, source collection or operational application write is authorized.

## C0 dependency audit

Read ADR006/007, Engineering threat model, Bundle B acceptance/coverage,
manual PdM engineer-input packet and authoritative roadmap. All five root
konsep PNGs inspected directly at original resolution on9 October2026;
hashes match `docs/design/NADI-CONCEPT-ALIGNMENT.md`. Existing navy/teal logo,
shared UI and development-only workspace are reused. Graph generation predates
these modules; coverage checked and exact current source used as fallback.
Original workspace and other branch work preserved in a separate candidate worktree.

Fresh Bundle B baseline evidence: Cockpit463 PASS, Maximo181 PASS, PI180 PASS/
11 Timescale SKIP, contracts14 PASS; TypeScript/build and62 frontend assertions
PASS. Baseline six final-main contract/route/security checks PASS. These are
local source-free results from the immediately preceding integration, not live
production health or a new source acquisition.

Dependency map: collector-owned Mart SELECT facade → registered asset / local
maintenance / ConditionQueryService → application-facing AssetContextService;
separate application store → existing CaseService / InspectionService /
RecommendationService → authorized context pages. SessionAuthority remains the
required trusted transport adapter. Writer router factories remain isolated,
default-off and unmounted. No second source client, collector or database.

## C1 — unified asset context

Typed bounded context combines canonical asset facts, informational WO references,
accepted selected condition evidence, scoped cases/inspections/recommendations.
Each original DTO retains its source/revision/time/quality/provenance; no raw
payload or source URL. Classification is UNKNOWN unless a canonical contract
exists; asset_type is not mislabeled as classification. Mart ingestion,
projection and source timestamps are separate; neutral policy means UNKNOWN.
Only APPROVED inspections enter reviewed_inspections; this is human record
review, never source verification or equipment health. Missing/unconfigured and
unavailable/invalid pages differ; unknown totals are null. Partial pages are
explicit, not full coverage. Cross-store reads are not an atomic historical
snapshot (`BOUNDED_LOCAL_READS`). Exact actor scope precedes all queries.

Capabilities use existing accepted local schemas without production DB access
in this task. Operational populations and runtime readiness are not re-certified.
Field, identity, provisioning, migration and UAT blockers remain in force.
