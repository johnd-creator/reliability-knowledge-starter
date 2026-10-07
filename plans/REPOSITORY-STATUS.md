# Repository status and debt — PLATFORM-ROADMAP-001

Audit date: **2026-10-07**. This is the Git-backed repository snapshot, not a
fresh production-runtime audit. Read [roadmap index](README.md) for priorities.

## Current NADI-PI-RUNTIME-001 checkpoint — 2026-10-07

Latest verified baseline `origin/main`: `3e981a3c5e20e148feba5b01ec0b1c134ca89205`.
PR #12 is **MERGED** at 10:27:39 UTC, after PR #13/#14. Its final pre-merge
head was `10f9e4a`; old IMPLEMENTED/MERGE-CANDIDATE statements below are dated
historical checkpoints. Phase 0 factual acceptance stays CURRENT; Phase 1 stays
CURRENT / PARTIAL. See [PI runtime evidence](../pi-collector/docs/nadi-pi-runtime-001.md).

Runtime control remains the original feature checkout `0c800da`, not the fresh
`codex/nadi-pi-runtime-001` review branch. PI API/source code was built from exact
merged `3e981a3`; private operator/lease modules are the runtime PR's new scope.
Migration 004 is applied to the same existing PI DB. One known source GET passed
and one snapshot owner is enabled; no governed NADI signal/projection is claimed.
Actual Mart owner is existing Maximo DB; `asset_af_mapping` is absent there.
[NADI-RUNTIME-002](NADI-RUNTIME-002.md) owns broader Mart runtime/governance schema
reconciliation before the NADI-IDN-002 pilot. Managed Mart DSN and PI opt-in
wiring corrections are proposed here; external-mode/full-platform acceptance is
not certified. NK and the mixed historical feature commit remain outside scope.

## Historical NADI-PI-001-FIX-01 reconciliation — 2026-10-07

Latest fetched `origin/main`: `52c67d41115b324e57c93bf82264a38951a6c275`.
PR #14 merged at 2026-10-07T10:09:16Z, after PR #13. Existing PR #12 previous
HEAD: `417dbc8316e1bfbd9ffba0c8bd4777bd186cf8ff`; a normal merge incorporates
main with no conflicts or published-history rewrite. Maximo implementation and
[WO acceptance evidence](../maximo-collector/docs/maximo-wo-recency-002.md) are
preserved unchanged. Maximo WO and NADI registered BSR/IP are CURRENT within
the accepted population; Phase 1 and MXR-004 remain CURRENT/PARTIAL and PARTIAL.
NADI-PI-001 stays IMPLEMENTED / MERGE-CANDIDATE on open, unmerged PR #12.

Final PI sequence: 001_init, 002_collect_runs, 003_backfill_progress,
004_signal_quality_fields. Duplicate numeric-prefix regression is added.
Migration 004 remains nullable/additive/guarded, prepared but not applied;
production PI access, pilot mappings and NADI PI projection are outside FIX-01.
See [offline evidence](../pi-collector/docs/nadi-pi-001-implementation.md#fix-01-reconciliation-and-migration-sequence).

## Historical NADI-PI-001 update — 2026-10-07

Verified new implementation baseline: `origin/main`
`a8393ba7d8dfddcae67b14b6153a8056c2f01d34`, which includes PLATFORM-ROADMAP-001.
`codex/nadi-pi-001-governed-source-adapter` selectively adapts `d23f848` with
additional lineage checks, streaming limits, typed JSON value evidence and
hermetic persistence/API tests. **IMPLEMENTED / MERGE-CANDIDATE**, not merged
or deployed. The quality migration is now numbered 004 after FIX-01, prepared
but not applied. Production PI requests: 0.
NK/deployment/CEMS are untouched; Phase 1 remains CURRENT / PARTIAL.
See [implementation evidence](../pi-collector/docs/nadi-pi-001-implementation.md).
Next: runtime/Mart reconciliation if needed, then NADI-IDN-002 pilot.

The remaining baseline/branch tables below preserve the PLATFORM-ROADMAP-001
dated audit; their ahead/behind counts are historical, not recomputed here.

## Baseline and method

| Fact | Verified result |
|---|---|
| Repository | `johnd-creator/reliability-knowledge-starter`, public, not archived |
| Default branch | `main` |
| Starting main SHA | `ef07a263b122d30e7dbec451e6094f9016b603c3` |
| Main commit date | `2026-08-24T18:45:41+07:00` |
| Audit branch | `codex/platform-roadmap-realignment`, created directly from fetched `origin/main` in a clean, separate worktree |
| Factual RC tag | `v0.1.0-rc.1` → `af1d9bde22dd37c96ec8156496d209532c0f601a`, reachable from main |
| PRs before this audit PR | #1–#10 MERGED; no OPEN PR returned by complete listing (10 total) |
| Main protection | `protected: false` from GitHub branches API; settings unchanged |
| Tracked GitHub workflow config | No `.github/` files in audited main tree; this is not evidence about every external CI service |
| Feature branch | `feature/pi-governed-source-adapter`: ahead 2, behind 0 |

Evidence method: fetch remote refs; inspect first-parent and reachability history;
use `rev-list --left-right --count` and `git cherry` to distinguish ancestry from
patch equivalence; read relevant main/branch documents, patches and source;
query GitHub PR/branch metadata. Documentation/status is evaluated against the
main SHA above; branch artifacts remain explicitly UNMERGED.

Codebase-memory Tier 2 and the existing graphify graph supplied structural
pointers. The code graph generation was `2026-08-24T09:24:57Z`, rooted in the
original checkout, not this main worktree. Coverage reported stale/untracked
NK, PI boundary and some governance files; deployment docs are excluded. Exact
Git blobs/main source were used for these claims, rather than assuming graph
completeness. This is a bounded roadmap audit, not an exhaustive code/security
or live source audit.

The original feature checkout retains a local production export; it was not
copied into this clean worktree or published. No historical branch, feature
code, binary or dataset was merged/copied in this task.

## Merged evidence catalog

| Scope | Integration evidence | Authoritative detailed evidence |
|---|---|---|
| Factual NADI V1 / Phase 0 | [PR #1](https://github.com/johnd-creator/reliability-knowledge-starter/pull/1), `af1d9bd`, tag `v0.1.0-rc.1` | [Release Candidate](../reliability-cockpit/docs/nadi-v1-release-candidate.md), [readiness](../reliability-cockpit/docs/nadi-v1-product-readiness.md) |
| Asset Health bounded discovery | [PR #2](https://github.com/johnd-creator/reliability-knowledge-starter/pull/2), `6687f07` | [MX-013A/B](../maximo-knowledge/docs/mx-013a-asset-health-source-discovery.md): technical Wellness metadata is partial, report/business meaning unresolved |
| FMEA item bounded discovery | [PR #3](https://github.com/johnd-creator/reliability-knowledge-starter/pull/3), `596d799` | [MX-014A](../maximo-knowledge/docs/mx-014a-fmeaitem-semantics.md): verified item→header; governed RPN/product use pending |
| Maintenance failure discovery | [PR #4](https://github.com/johnd-creator/reliability-knowledge-starter/pull/4), `44868d8` | [MX-015A](../maximo-knowledge/docs/mx-015a-maintenance-failure-semantics.md): source fields are not a governed failure event |
| RCFA relationship discovery | [PR #5](https://github.com/johnd-creator/reliability-knowledge-starter/pull/5), `2c73b03` | [MX-016A](../maximo-knowledge/docs/mx-016a-rcfa-relationships.md): direct source Asset field/FDT verified; canonical projection still pending |
| DOMINION Overhaul discovery | [PR #6](https://github.com/johnd-creator/reliability-knowledge-starter/pull/6), `2163be2` | [MX-017A](../maximo-knowledge/docs/mx-017a-dominion-overhaul-semantics.md): additional inspection/Scope-PM/WO paths, incomplete KPI semantics |
| Central PI + identity probe | [PR #7](https://github.com/johnd-creator/reliability-knowledge-starter/pull/7), `74e5dc3` | [PI-001A/002A](../pi-knowledge/docs/pi-001a-source-topology.md): native key not found in bounded evidence; governed registry required |
| Asset↔AF registry | [PR #8](https://github.com/johnd-creator/reliability-knowledge-starter/pull/8), `1c24a78` | [Mart query/mapping boundary](../reliability-cockpit/docs/reliability-mart-query-api.md) |
| Controlled mapping administration | [PR #9](https://github.com/johnd-creator/reliability-knowledge-starter/pull/9), `883534c` | [Administration workflow](../reliability-cockpit/docs/asset-af-mapping-admin.md): PROPOSED import, human verify/retire, no production seeds |
| SQLite mapping timestamp correction | [PR #10](https://github.com/johnd-creator/reliability-knowledge-starter/pull/10), `ef07a26` | Main baseline includes the correction; test artifact does not certify active DB migration |

PR merge SHAs differ from branch heads because integration used merge commits.
Every listed integration SHA and tag is reachable from audited main. Source
knowledge can be newer than the accepted canonical/product projection; keep
both boundaries explicit until a reviewed implementation changes them.

## Documentation reconciliation

| Artifact | Classification / decision |
|---|---|
| Root README | Old “templates only” claim and missing CEMS were STALE; rewritten as CURRENT platform entry point |
| Root AGENTS | Old seven-project/no-root-runtime/only-application framing was PARTIAL; rewritten for platform ownership, evidence and no-new-DB rules, with NK marked UNMERGED |
| `plans/README.md` and new vision/product/status docs | CURRENT entry point; one owner document per status dimension |
| `plans/reliability-cockpit-platform/05-roadmap-implementasi.md` | CURRENT engineering backlog with reconciled M0–M8 status; 20-Aug execution table retained as HISTORICAL |
| Older planning docs 01–04/06 and plan-folder introduction | PARTIAL / HISTORICAL assumptions; preserved with a supersession notice, not execution authority for current product status |
| “Cockpit never reads collector SQL” in old plan | SUPERSEDED for the explicit SELECT-only canonical Mart path; legacy API ingestion remains correct |
| Domain semantics, contract, Mart and source discovery docs | CURRENT within their dated/accepted scope; semantic unknowns remain binding, not globally solved by a discovery PR |
| Factual V1 RC/readiness notes | HISTORICAL QA plus CURRENT factual product boundary; stale PR/tag pending state reconciled to PR #1/tag |
| `summary.md` | HISTORICAL; its “collector-only cockpit refactor not started” statement is superseded by main |
| `CODEX_BOOTSTRAP_PROMPT.md` | Old discovery-first task was STALE as a general onboarding default; replaced with roadmap-aware instructions |
| `USERGUIDE.md` | HISTORICAL standalone setup guide; preserved with a deployment/ownership notice |
| `deploy/compose/README.md` | PARTIAL runtime runbook; corrected API-only statement and warns that main lacks Mart DSN wiring and managed PI worker |
| Feature-only AGENTS / NK / governed PI docs | UNMERGED evidence only; not used to claim main has those services or files |

## Debt inventory and dispositions

| Debt | State | Recommended action |
|---|---|---|
| D01 Governed PI adapter | MERGED / runtime checkpoint above | NADI-PI-001 selectively adapts `d23f848` from `main a8393ba`, reconciled with `main 52c67d4` via FIX-01; PR #12 merged, migration 004 applied by NADI-PI-RUNTIME-001; governed pilot/projection remain pending |
| D02 Mixed platform/NK feature commit | UNMERGED / NEEDS_REVIEW | Split/review NK, deployment, documentation and data/model publication from `0c800da`; do not bulk merge for PI integration |
| D03 Mart runtime DSN | UNMERGED / PARTIAL | Review `7149455`: main Compose lacks `RELIABILITY_MART_DATABASE_URL`; retain external-mode wiring, init dependency and regression intent after reconciling managed-mode overlap in `0c800da` |
| D04 Home Asset Health access note | UNMERGED / HISTORICAL | Compare `94721eb` with merged MX-013A/B. It records TLS-blocked access, not verified Wellness/ACR/MPI; preserve useful network evidence later without reopening this audit's source access |
| D05 Source→product semantic adoption | PARTIAL | FMEA item fields/RCFA source Asset relationships/Overhaul additions are discovery findings, not already accepted canonical UI joins or KPI semantics |
| D06 Pilot identity and runtime migration | NEEDS_REVIEW | Mapping administration is merged, but no production mapping seed or migration execution is certified by Git; approve scoped pilot and read-only-role/runtime readiness separately |
| D07 Collection/integration acceptance | PARTIAL | Validate capacity, single-worker ownership, freshness/coverage/degraded states and 24–72h/backup restore acceptance in authorized later tasks |
| D08 Governance / CI | NEEDS_REVIEW | Main is unprotected and tracked GitHub workflow config absent; adopt lightweight PR and relevant checks, protection separately if authorized |
| D09 Runtime vs Git handoff | NEEDS_REVIEW | Feature deployment reports restored local data and PI HTTP 401; these are dated operational handoffs, not main runtime guarantees. User deferred credential checking; do not retry here |

### Required branch details

Counts are **ahead / behind audited main**, not “number of changes to merge”.
A diverged branch has both counts > 0. `git cherry` found no patch-equivalent
unique commits for the three branches below with positive ahead counts.

| Branch | Head SHA | Ahead / behind | Unique work | Disposition |
|---|---|---:|---|---|
| `feature/pi-governed-source-adapter` | `0c800dac1da6ef863afdb193021176fe7feac073` | 2 / 0 | `d23f84851716cec88e43237654a1c58fa79e63d4` governed PI source boundary; `0c800da` adds NK and managed runtime/docs | KEEP TEMPORARILY / UNMERGED; review and split by concern |
| `fix/nadi-mart-runtime-wiring` | `71494550714f77af8f9cb68c90722732e18b5ca8` | 1 / 20, diverged | Mart DSN template, managed/external Compose wiring, init dependency and regression tests | CHERRY-PICK CANDIDATE after adaptation; not safe to assume superseded completely |
| `discovery/mx-013h-home-asset-health-source` | `94721eb0b54c70bef21e5604e0a9f41168943544` | 1 / 20, diverged | One documentation commit: home TLS blocked before auth/business discovery; no new source meaning | NEEDS_REVIEW; retain historically useful bounded access evidence |
| `fix/unblock-local-collector-access` | `88f573e781bf4ea0a1cc3ee14cce2bb8d5c58f31` | 0 / 78 | None outside main; ancestor | MERGED/HISTORICAL; deletion candidate only after owner review |
| `task/nadi-002-asset-reliability-workspace` | `449ca5cfcf4c41525bd3a958e28b3f2fa54312ca` | 0 / 21 | None outside main; factual RC integrated via PR #1 | MERGED/HISTORICAL; preserve PR/tag before any later cleanup |

`7149455` adds external Mart configuration that `0c800da` does not include;
the latter hardcodes a managed DSN and adds other services. Review both targets
and tests rather than declaring the old fix obsolete. No cherry-pick, merge,
branch deletion, or protection change was performed by this task.

### Remaining remote branch inventory

All remote branch heads were examined, not only the five required names.
Main is the baseline; the current audit branch is omitted from this pre-PR
inventory. Rows with ahead 0 are reachable from main and have no unique commits;
“historical” does not automatically authorize deleting them.

| Branch | Full head SHA | Ahead | Behind | Disposition |
|---|---|---:|---:|---|
| `discovery/maximo-asset-health-wellness-acr-mpi` | `62ba505b333af8770d3d4606777875ce77f448cd` | 0 | 18 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `discovery/maximo-dominion-overhaul-semantics` | `e2751c3993baf1e769dd67658c3193b84e23a953` | 0 | 19 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `discovery/maximo-fmeaitem-semantics` | `20c56efc741dd13a07ab9be5540e8ee02033ec3b` | 0 | 19 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `discovery/maximo-maintenance-failure-semantics` | `5aeab33636325b73dd03821ae7b5c08d19c3b9a8` | 0 | 19 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `discovery/maximo-rcfa-relationships` | `94da5977feba9c9c804f850c8c971fcc83c93406` | 0 | 19 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `discovery/pi-web-api-topology` | `e8c19a7a37a897e2f3dba507cc2bee816f89dd7e` | 0 | 18 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `feature/governed-asset-af-mapping-admin` | `a976c21e6f71eb32323cab9fe3f693ddc6a93b90` | 0 | 3 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `feature/governed-asset-af-mapping-registry` | `7e85fd7180fe3fa00688bbdbabe2ff71fc655f04` | 0 | 5 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `fix/mapping-sqlite-timezone-test` | `8201930ba369ca6e39773facce15480b2d2bde54` | 0 | 1 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-005r-extended-app-discovery` | `3da15d564bcc4f3eb8a7140069f3d861d2974d5e` | 0 | 73 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-006a-knowledge-auth-parity` | `21ced437f8f5e67aa71138e8c845d52f2d0057e6` | 0 | 70 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-006b-safe-detail-dereference` | `224384b1b162647f73926ae4eb48e7f6690606af` | 0 | 67 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-006c-contract-integrity-query-shaping` | `c0907c1f3ce2c3ca5af76e4e2bf0ad002b1aee9b` | 0 | 65 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-007r-nadi-canonical-contract` | `0213402348e23233a53f41593eaa6e17c34f9cc4` | 0 | 62 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-008r-maximo-canonical-collector` | `d269e6e9eeec727d1448119198cde80157a1441a` | 0 | 59 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-008s-live-canonical-smoke` | `92984b7d7973d949d485e790bbc502637565ea8b` | 0 | 57 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-009r-reliability-mart-persistence` | `66b75b874b17470150b815e77184ad4c42bdbfbb` | 0 | 53 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-010d-maximo-data-explorer` | `07a9023ba313f74b5ccc84519bda488fea2e76c9` | 0 | 49 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/mx-011r-controlled-initial-mart-load` | `8b60186a15a47d2a70a3a4973e91097d3e87e912` | 0 | 48 | MERGED/HISTORICAL; owner-reviewed cleanup later |
| `task/nadi-001-product-foundation` | `54b3a8115f1076823283b09dd2abb1cf3d3e6556` | 0 | 44 | MERGED/HISTORICAL; owner-reviewed cleanup later |

Two additional local-only historical branches were checked:

| Local-only branch | Full head SHA | Ahead / behind | Result |
|---|---|---:|---|
| `task/mx-006r-targeted-live-verification` | `49651cc2b9223e85da1e7f489ff9fbe7a3dc72e5` | 0 / 72 | Ancestor of main; no unique work |
| `task/mx-010r-reliability-mart-query-service` | `7576214ed74204eb2951a5e2c52098dc8d8879b7` | 0 / 52 | Ancestor of main; no unique work |

Two local heads differ from remote, but are also ancestors of main with no
unique work:

| Local branch | Local head SHA | Ahead / behind main | Remote distinction |
|---|---|---:|---|
| `fix/unblock-local-collector-access` | `f85dfa6c07f4d278424ac7d9e16b72682332f6c6` | 0 / 74 | Remote head is `88f573e`; local advanced further in already-integrated history |
| `task/mx-008s-live-canonical-smoke` | `6ec2b228fc96b012965570690fbc910989b42ad3` | 0 / 56 | Remote head is `92984b7`; local includes the already-integrated Mart schema commit |

All remaining pre-existing local heads with remote counterparts matched them
at audit. The audit worktree was clean before edits. The original feature
checkout's untracked report is not a reason to reset that checkout or copy it
into documentation.

## Lightweight repository governance

```text
main ← reviewed Pull Request ← one task branch
```

Prefer `codex/<task>` for agent-created branches; existing `task/*`, `feature/*`,
`fix/*` and `discovery/*` remain valid historical conventions. One concern per
PR, task ID and scope in the body, acceptance evidence, migration/rollback
notes only where relevant. For a solo maintainer, self-review plus relevant
checks is sufficient to keep velocity; request a second review for identity,
source safety, scoring, production migration or write-back decisions.

Recommended later protection: require PRs, block force-push/deletion of main,
and require the relevant automated checks after those checks exist. One review
can be required when a reviewer is available; avoid permanently blocking a
solo maintainer on an unavailable reviewer. `protected: false` is an observation,
not an authorization to change settings in this task.

Use documentation/link/diff checks for docs PRs and each owning component's
hermetic/contract tests for code changes. No workflow files are added here.
After integration, update the owning roadmap status with accepted evidence;
Git reachability and PR state outrank dated proposal checklists.

## Documentation validation

PLATFORM-ROADMAP-001 checks before PR creation:

- `git diff --cached --check`: PASS.
- Staged diff gate: 19 changed files, all `.md`; no application code, Compose,
  migration, data, image, model, or other binary changes.
- Local Markdown targets/heading anchors: 94 checked, zero errors; branch-only
  GitHub blob references validated against local Git objects. General external
  web links were not crawled; PR/commit/tag evidence came from GitHub/Git.
- 56 commit references resolved; mainline evidence ancestry and the five
  required remote branch refs verified.
- All 78 detailed engineering backlog IDs and the old historical status table
  preserved; current M0–M8 status is separately reconciled.
- Added-line secret-pattern scan: no private keys, credential URLs, GitHub
  tokens or AWS keys found. No environment file or raw report copied.
- `git ls-remote --tags` confirms the RC tag on GitHub and its peeled mainline
  commit. PR listing and branch-protection reads were read-only.

The temporary local documentation validator was used because no tracked
Markdown validator/workflow was identified in the audited baseline. Application
suites and production smoke were not rerun for this Markdown-only change.

## Review notes and audit limits

- Phase 0 COMPLETE refers to the accepted factual RC boundary, not all M0–M8
  exit criteria or continuously healthy source integrations.
- All M0–M8 remain PARTIAL at full-milestone scope where wider acceptance is
  unproven; detailed completed artifacts remain credited.
- NK manual baseline is implemented only on feature; automatic acceptance is
  not inferred from tests/model files, and UI accuracy/uncertainty claims need
  separate validation. No artifact is moved out of the monorepo.
- Source credentials and live pilot readiness were not checked. PI HTTP 401 is
  a previous handoff and remains deferred; no new source requests were made.
- Branch cleanup and runtime fixes are recommendations for later PRs. This PR
  changes only Markdown and leaves application/runtime files identical to main.
