# NADI Phase 2 Bundle B — umbrella evidence

Baseline: latest verified main `02e887c56057611f112b7b652ba9a9aee8b382ea`,
PR29 MERGED on 8 October 2026; corrected head `67dcb4d` included.
Phase 1 remains CURRENT/PARTIAL; Phase 2 candidate, operational activation OFF.

Original workspace and existing worktrees preserved, including an unrelated
untracked spreadsheet. A fresh isolated worktree is used. PRs are a dependency
stack: review/merge in checkpoint order, never automatically. No concurrent branch
or private runtime evidence is overwritten. Historical Phase-1 GOV03 monitoring
expiry/review remains the accountable operator's duty; this bundle changes no
policy, service, credential, journal, lock, cursor, mapping or measurement.

## Checkpoints

| Checkpoint | Candidate scope | Verdict |
|---|---|---|
| B1 | ADR007, source-boundary policy, local coverage/dependency/threat review | PASS — source-free architecture evidence |
| B2 | Trusted identity/session/RBAC adapter | PASS — isolated foundation; enterprise activation BLOCKED |
| B3 | Local factual intelligence improvements / collection proposal | PASS — no source acquisition |
| B4 | Manual inspection envelope / methods / isolated lifecycle | PASS — candidate model; engineer field approval PENDING |
| B5 | Recommendations / existing WO references / audit | PASS — local proposal semantics, no maintenance authorization |
| B6 | Existing Engineering + four context-preserving lab screens | PASS — production blocked; operational integration PENDING |
| B7 | Integrated regression/security/handoff | PASS — isolated acceptance; deployment NOT AUTHORIZED |

Baseline test: Cockpit `python -m unittest discover -s tests -q`: 396 run,
276 pass, 120 skip. PostgreSQL fixtures not configured; no new operational DB.
Existing SQLite ResourceWarnings are visible, not hidden as a clean leak audit.
Final fixture/test evidence and review PRs are recorded below.

## Dependency and threat review

Accepted contracts use Pydantic, SQLAlchemy, FastAPI; web is Next15/React19/TS.
Reuse existing dependencies; no invented enterprise IdP SDK, new collector or
source credential path. Browser actor/roles/assets remain untrusted. Protect
session fixation, revocation, CSRF/origin, IDOR, self-review, audit tampering,
lost updates, unsafe attachments and interpretation-as-fact. Production bootstrap,
provider validation, identity directory, retention/quota and restricted writer
provisioning are activation blockers. This is a scoped design assessment, not a
claim of dependency-CVE clearance or operational penetration testing.

Safety target: source writes0, unapproved production GET0, operational DB/DDL0,
deployment/restart0, Engineering activation0, Phase-1 evidence mutation0.

## Overall verdict and exact branch dependencies

**PARTIAL — candidate implementation complete; operational activation remains BLOCKED.**
Main was fetched again before publication and remained `02e887c56057611f112b7b652ba9a9aee8b382ea`. PR29 is MERGED at that SHA; its corrected `67dcb4d88c142e6e21293b387d57c8b87de41b5b` is included. No existing PR29 branch is changed.

| Checkpoint / branch | Checkpoint commit | Review PR / base |
|---|---|---|
| B1 `codex/nadi-ph2-b1-boundaries` | `03ab551` | [PR30](https://github.com/johnd-creator/reliability-knowledge-starter/pull/30), main |
| B2 `codex/nadi-ph2-b2-identity` | `9936b5b` | [PR31](https://github.com/johnd-creator/reliability-knowledge-starter/pull/31), B1 |
| B3 `codex/nadi-ph2-b3-maximo-intelligence` | `d55d1d1` | [PR32](https://github.com/johnd-creator/reliability-knowledge-starter/pull/32), B2 |
| B4 `codex/nadi-ph2-b4-manual-pdm` | `7c594c6` | [PR33](https://github.com/johnd-creator/reliability-knowledge-starter/pull/33), B3 |
| B5 `codex/nadi-ph2-b5-recommendations` | `ed1f7f8` + compatibility repair `87e4b93` | [PR34](https://github.com/johnd-creator/reliability-knowledge-starter/pull/34), B4 |
| B6 `codex/nadi-ph2-b6-concept-ui` | `4eeea80` | [PR35](https://github.com/johnd-creator/reliability-knowledge-starter/pull/35), B5 |
| B7 `codex/nadi-ph2-b7-integrated-quality` | code/test checkpoint `6dda97f`; documentation at current PR HEAD | [PR36](https://github.com/johnd-creator/reliability-knowledge-starter/pull/36), B6 |

All PRs stay OPEN/UNMERGED. Review in dependency order; retarget a dependent PR to main only after its predecessor is reviewed/merged. B7 supplies final formatting, exact-subject session hardening, bounded scopes, unsaved-form discard correction, shared nonblank/schema alignment, acceptance and truthful roadmap reconciliation. Earlier checkpoints are not independent deployment releases. No merge, rebase/force push or runtime promotion is performed.

## Implemented contracts and isolation

- Trusted provider assertions produce a stable server principal; shared opaque hashed sessions support idle/absolute expiry, revocation, exact HTTPS origin, session-bound CSRF and JSON mutation requests. Browser actor/roles/assets are ignored. Missing/forged/revoked identity and wrong provider subject are denied.
- AUTHOR owns draft mutation; REVIEWER must be asset-scoped and independent from creator/contributors/inspector/PIC. ADMIN can perform narrow scoped session administration and is not an implicit author or reviewer. Activity exposure is bounded to authorized own-subject audit; broader security-custodian reporting is deferred.
- Manual PdM is an extensible human envelope with original typed value/unit/time, separate observation/interpretation, candidate method fields, metadata-only attachments and NOT ASSESSED. The inspector is the trusted recording principal; delegated transcription requires a later explicit policy.
- Recommendations resolve case and supporting evidence through local authorized catalogs, optionally reference an exact existing local WO, and require validated PIC/team scope. Review is NADI_RECORD_REVIEW_ONLY. Local follow-up never changes source WO status and does not authorize maintenance.
- Exact registered canonical assets are required. Manual inspection identity does not require inventing an AF mapping. Referenced PI condition evidence still requires the existing governed mapping/signal boundary. Unknown/null is never manufactured as zero or healthy.
- Application CAS, immutable revision snapshots and actor-scoped receipts commit atomically. Same request replays without duplicate record/audit or fabricated timestamps. One concurrent edit wins; the other receives a conflict. Source and canonical Mart access remain read-only.
- Five concepts, original logo and existing shared components were inspected. `/engineering/lab` contains four new context-preserving synthetic views, linked to the existing case workspace. Production demo remains blocked even with both candidate flags true.

## Test evidence

Commands below ran from the indicated subproject with existing dependency environments. `NADI_TEST_PYTHON` denotes the existing Cockpit Python interpreter; no new runtime dependency is added. Temporary HTTP/JSON-schema test dependencies were supplied on PYTHONPATH. Disposable PostgreSQL DSNs were localhost-only `*_test` databases on an isolated temporary cluster, not operational DATABASE_URL or Mart credentials.

```sh
# reliability-cockpit; all three isolated test DSNs configured, NADI_COMPOSE_TESTS=1
PYTHONPATH=.:tests:/tmp/nadi-phase2-testdeps:/tmp/nadi-phase1-host-testdeps \
COCKPIT_CONFIG_MODE=managed DATABASE_URL=sqlite:// \
"$NADI_TEST_PYTHON" -m unittest discover -s tests -q
# 462 run / 462 pass / 0 skip, 47.759 seconds

# targeted bundle acceptance (part of full suite)
"$NADI_TEST_PYTHON" -m unittest test_phase2_bundle -q
# 10 pass: schema/model parity, strict contracts, disabled routes, trusted-session E2E,
# PG additive migration compatibility, concurrent CAS, duplicate receipt rollback,
# reader/writer grants, in-flight session revocation serialization.

# reliability-data-contracts
python -m unittest discover -s tests -q
# 14 pass

# maximo-collector: existing interpreter, hermetic adapters/fixtures
python -m unittest discover -s tests -q
# 181 pass

# pi-collector: existing interpreter, hermetic adapters/fixtures
python -m unittest discover -s tests -q
# 191 run / 180 pass / 11 skip

# reliability-cockpit/web
npm run check:phase2                 # 25 assertions pass
npm run check:engineering            # 37 assertions pass
npm run check:product-safety         # 25 UI source files pass
npx --no-install tsc --noEmit        # pass
COCKPIT_API_BASE=http://127.0.0.1:9 NEXT_TELEMETRY_DISABLED=1 npm run build
# pass; isolated source copy, no operational API/config

git diff --check                     # pass
# Markdown relative links: pass; all 34 JSON Schemas validate
```

The isolated test cluster needed UTF-8 initialization for psycopg/SQLAlchemy; the initial SQL_ASCII fixture was retained locally and replaced only as a disposable test fixture. No operational database was reset. Existing SQLite/psycopg ResourceWarnings remain visible; no claim of a completed resource-leak audit. PI's 11 skipped PostgreSQL/Timescale integration tests require a dedicated PI/Timescale fixture unavailable in this test setup; no operational PI DB was substituted.

Browser acceptance: **24 pass**, network restricted to two disposable loopback previews. Manual numeric blank rejection; true numeric zero/original unit; review remains IN_REVIEW; synthetic queue counts; no browser approval authority; proposal validation; UNKNOWN/NOT ASSESSED; four screens at 390/768/1365 px without horizontal overflow; no JS exceptions; production lab blocked/no form controls. Desktop/mobile screenshots were visually inspected. Operational UI/API smoke is intentionally not performed.

GitHub checks: repository has no `.github/workflows` and checkpoint PR check rollups are empty. Local results above are evidence, not a claim that GitHub CI passed.

## Security/activation blockers and migration proposal

| Gap | Class | Required before activation |
|---|---|---|
| Enterprise assertion verification and directory grant guard | SECURITY / IDENTITY | Trusted production provider integration; stable subject, asset scope and atomic revocation/grant-change contract |
| Browser session bootstrap/logout/recovery | SOFTWARE / SECURITY | Reviewed login/CSRF lifecycle, logout revocation, rate/quota and retention policy; no anonymous/browser identity fallback |
| Application migration ownership/ledger/preflight | PROVISIONING | Prove existing application DB identity, backup and reviewed additive 002→003→004; wrong-DB guard; explicit checksums/ledger and fail-closed status/apply tooling |
| Least-privilege session/application writer | PROVISIONING | Separate owned DB roles; only approved row writes, revision/security audit INSERT/SELECT; no audit UPDATE/DELETE, schema ownership or source privileges |
| Manual method fields / interpretations | HUMAN / DATA | PdM engineers approve field definitions, measurement context, units, reviewer/PIC/team semantics; no limits fabricated |
| Attachments | OPTIONAL / SECURITY | Authenticated scoped storage, MIME/content scanning, quota/retention before actual upload; currently metadata only |
| Operational frontend/API integration and UAT | SOFTWARE / HUMAN | Trusted server identity wiring, conflict recovery, engineer workflow/accessibility validation; current UI is synthetic local only |
| New Maximo domains | SOURCE CONTRACT / AUTHORIZATION | Separate bounded read-only plan and authorization, confirmed fields/keys/provenance/cursor; no new collection executed |

Application migration namespace is separate from canonical Mart. 002 case tables, 003 session/security tables and 004 human-record tables were exercised only on disposable PostgreSQL. Files intentionally fail if rerun without a reviewed ledger; do not execute them manually in production. Future preflight must reject wrong database, unknown schema/checksum, incomplete relations and unexpected role ownership. Back up the owning existing application store before approved DDL. Rollback first disables application endpoints/session issuance, revokes candidate writer privileges and preserves all record/audit history; never drop canonical Mart, reset collector state or recreate volumes.

Scoped threat and negative-test review covered CSRF, impersonation, IDOR, independent review, CAS/replay, audit privileges, attachment metadata, source-boundary imports and production mounting. No production penetration test, enterprise provider validation or dependency-CVE clearance is claimed. Graph discovery was attempted first; generation `2026-08-24T09:24:57Z` points to the original older checkout, so new Phase-2 paths were missing/stale. All relied-on changed paths and relevant API/migration scopes received coverage checks, then exact current source and executable fixtures were used. Graph absence was not treated as proof of completeness.

## Safety and readiness

Task-attributable production operations, all **0**: Maximo source writes; WO create/update/status/approval/closure; PI source writes; unapproved production source GET; production DB writes/DDL; production deployment/restart; Engineering activation; Phase-1 evidence/journal/lock/cursor/approval mutation. CEMS/NK changes, registry reload, mapping changes, source discovery/history/backfill and new operational databases are also zero. Only synthetic SQLite/PostgreSQL fixture writes and temporary preview services occurred. Existing operational health is not newly certified; accepted historical evidence is preserved, not rewritten as a fresh observation.

**Phase 1 CURRENT/PARTIAL. Phase 2 candidate foundation implemented; overall PARTIAL.**
Recommended next bundle: trusted enterprise identity/session/directory integration, engineer field/PIC/review sign-off, reviewed application migration runner/least-privilege provisioning and authorized backend/frontend UAT. Operational activation remains a separate reviewed authorization. Do not introduce Maximo WO writes as a shortcut.
