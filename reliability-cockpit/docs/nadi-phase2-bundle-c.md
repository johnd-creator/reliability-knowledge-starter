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


## C0–C7 checkpoint verdicts

Overall **PARTIAL**: development/test candidate delivered; operational product
activation BLOCKED. Phase1 remains CURRENT/PARTIAL, not re-certified or closed.

| Checkpoint | Candidate verdict | Delivered evidence |
|---|---|---|
| C0 baseline/dependencies | PASS | Exact main7a846ef, BundleB PR30–36 included, original workspace/concurrent work preserved, ADR/security/knowledge/concept review |
| C1 unified context | PASS | Typed same-asset bounded asset/maintenance/condition/human-record query, disabled GET-only factory, neutral freshness |
| C2 Maximo local intelligence | PASS | Deterministic maintenance chronology/pagination, original dates/status/failure code, proposal-only source manifest |
| C3 manual inspection | PASS | Explicit submission/review/return/revise lifecycle, immutable reviewed-human snapshot and unit/time/null preservation |
| C4 recommendations | PASS | Reviewed case/evidence pins, local review/follow-up, independent completion evidence; never WO mutation |
| C5 concept UI | PASS | Integrated five-screen DEMO, shared branding/components, responsive and accessible input, unsaved protection |
| C6 integrated acceptance | PASS |532 Cockpit tests, isolated PostgreSQL transaction/concurrency, source/authorization negatives, browser and contract compatibility |
| C7 documentation/UAT/handoff | PASS | Coverage, dependencies, activation blockers, engineer packet, rollback proposal and truthful roadmaps |
| Production readiness | BLOCKED | Enterprise identity/bootstrap, writer/migration provisioning, engineer fields and operational UAT; no activation authorized |

## Exact review stack and release provenance

Authoritative main remains `7a846ef2c7e25306f23da99dd011e1d54aa8f4a4`.
Final tested application checkpoint: `b42c1da84bb3ba5e9ed8cb14e873bb5f11c25636`.
C7 adds documentation and a nonfunctional trailing-blank fixture cleanup; its exact delivery HEAD is reported after
publication and can be resolved from the final PR head. None of these PRs is merged.

| PR | Checkpoint / branch | Exact head | Depends on |
|---|---|---|---|
| [#37](https://github.com/johnd-creator/reliability-knowledge-starter/pull/37) | `codex/nadi-ph2-c1-asset-context` | `27f3f5ffb0f850f3e5a108b28bdeab914f0597bd` | `main` |
| [#38](https://github.com/johnd-creator/reliability-knowledge-starter/pull/38) | `codex/nadi-ph2-c2-local-maximo` | `c4991f27e6f2d656ea59de6d5ffe920d47aaeff2` | `codex/nadi-ph2-c1-asset-context` |
| [#39](https://github.com/johnd-creator/reliability-knowledge-starter/pull/39) | `codex/nadi-ph2-c3-inspection-workflow` | `f1c8fab768b2c058d1bb83150a659d21d6283fa3` | `codex/nadi-ph2-c2-local-maximo` |
| [#40](https://github.com/johnd-creator/reliability-knowledge-starter/pull/40) | `codex/nadi-ph2-c4-recommendation-workflow` | `248b49639429e187670df3ce77db79022c29e043` | `codex/nadi-ph2-c3-inspection-workflow` |
| [#41](https://github.com/johnd-creator/reliability-knowledge-starter/pull/41) | `codex/nadi-ph2-c5-concept-workflow` | `b5da9a513ad5f5ea9c459a5dc3ad2d8065c6d762` | `codex/nadi-ph2-c4-recommendation-workflow` |
| [#42](https://github.com/johnd-creator/reliability-knowledge-starter/pull/42) | `codex/nadi-ph2-c6-integrated-acceptance` | `b42c1da84bb3ba5e9ed8cb14e873bb5f11c25636` | `codex/nadi-ph2-c5-concept-workflow` |


C7 branch: `codex/nadi-ph2-c7-handoff`, based on C6. Its PR is the umbrella
documentation handoff, not a separate implementation or operational release.
Review dependency order C1→C2→C3→C4→C5→C6→C7. C6 contains acceptance repairs;
do not activate an intermediate checkpoint. All PRs stay OPEN/UNMERGED.

## Local evidence coverage and gaps

| Domain | Current bounded candidate coverage | Gap / source status |
|---|---|---|
| Asset master/hierarchy | Existing registered Mart identity, description/location/parent/type/unit and original timestamps | Classification/specification not inferred; UNKNOWN when not projected |
| Existing WO / maintenance | Existing MXWODETAIL projection, asset relationship, status/type, actual start/finish/source-change chronology and failure code | Problem/cause/remedy and PM/job-plan fields not silently drawn from raw payloads |
| Approved PI condition | Existing selected accepted ConditionQueryService evidence with lineage/type/unit/source/collection/projection time/quality/freshness | No technical registry auto-promotion; unmapped/no-approved-signal remains unavailable/unknown |
| Engineering cases | Existing application service scope/revisions/review plus frozen approved inspection evidence | Trusted enterprise provider/bootstrap and mounting pending |
| Manual PdM | Generic original-value envelope, method registry and independent human review | Method-specific engineering fields/limits and attachments not approved/activated |
| Recommendations | Exact reviewed same-asset case/evidence, PIC/team/date, local follow-up and completion verification | No Maximo mutation; operational directories/UAT pending |

[Source manifest](maximo-bundle-c-collection-manifest.json) contains exact known
object structures only; unknown endpoints stay null/unverified, budgets unapproved,
execution disabled. New classification/specification/PM/job-plan/operator-logsheet
collection requires a separate owner-approved task. No new source endpoint was tested.

Read models are implemented against existing accepted local Mart schemas, not copied
source databases. Backend complete-chain acceptance uses synthetic disposable Mart
and application rows; PI handoff is a hermetic Collector fixture, never a live GET.
Frontend screens use labeled browser-memory fixtures; no operational backend wiring,
fake authentication, approved production field claims or browser role authority.
No new operational database. Production populations/runtime were not queried or
re-certified here; preservation is supported by zero operational access/mutation.

## Acceptance and next handoff

[Integrated acceptance](bundle-c-integrated-acceptance.md) records exact commands,
532/181/180+11SKIP/14 test counts,35 schemas,100 frontend assertions,40 browser
checks and typing/build evidence. All38 new workflow assertions and17 trusted HTTP
integration tests are included in their respective totals, not double-counted.
GitHub CI rollups are empty for this review stack; local results are not falsely
reported as GitHub CI PASS. Required repository/owner reviews remain pending.

[UAT and activation plan](bundle-c-uat-and-activation.md) records owner gates,
engineer input, reviewed migration/provisioning and rollback proposals.
[Five-image coverage](../../docs/design/NADI-BUNDLE-C-CONCEPT-COVERAGE.md) records
original-image inspection and concept-to-screen coverage without invented visual facts.

Task-attributable Maximo/PI source GET/write, WO create/update/status changes,
production DB write/DDL, deployment/restart, Engineering activation, source registry,
mapping/signal/projection and Phase1 journal/cursor/evidence mutation counts: **0**.
CEMS/NK unchanged. All temporary previews and disposable fixture services are stopped
after validation. Original workspace, source runtime and private acceptance artifacts
remain preserved. No source credentials or private runtime infrastructure published.
