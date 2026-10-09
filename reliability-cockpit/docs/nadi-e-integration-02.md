# NADI-E-INTEGRATION-02 — final audit and local authentication acceptance

Date: 2026-10-09. Development/disposable acceptance **PASS**. Overall delivery
**PARTIAL**: real QA **NO_GO**, operational Engineering activation OFF.
Merge candidate **READY pending explicit operator authorization and exact-head CI**.
No merge or deployment is authorized by this document.

## Baseline and dependency stack

Verified main: `eda3595a9b8d86726dd0d89192ebf4657b66d27e` (Bundle D merged).
Original Bundle E candidate: `fe7f958ce071b3b22e30b484ee9805c8c76c0237`.
Tested final implementation: `1ec149de2d1acd4113987364e1f96c790bfaf63e`.
PR61 final documentation HEAD is resolved from GitHub before authorization; this
report deliberately does not claim a self-referencing documentation commit SHA.
The original workspace, concurrent branch and untracked spreadsheet were preserved.

| PR | Head at review | Base dependency |
|---|---|---|
| 51 | 727f11554303fcf4ce988dfbca5d72a973c6449f | main |
| 52 | b2f91ddb372fd0db16270f2649b17e63d2aba66e | 51 |
| 53 | 2b4a03920e7493ffc2f75821fe1354c69e3da9bd | 52 |
| 54 | 7493e68a0bbfff3759046d88e1155f4b0862c94c | 53 |
| 55 | e1dec11a42b5c4fd543980bf13876d836bc47143 | 54 |
| 56 | fa5405a12c2cc00d2ee52cda466a26b6d1d61c5c | 55 |
| 57 | f3674192fb06b6c0d8f7538defdd5d6079fd4fe4 | 56 |
| 58 | d3a7d43f55a619440f758ec6ef21ae6c2156422d | 57 |
| 59 | fe7f958ce071b3b22e30b484ee9805c8c76c0237 | 58 |
| [60](https://github.com/johnd-creator/reliability-knowledge-starter/pull/60) — E9 | 00d307731ab006fc942ffc4c7c5dae9801f86526 | 59 |
| [61](https://github.com/johnd-creator/reliability-knowledge-starter/pull/61) — E10 | final reviewed PR head; includes 1ec149d | 60 |

PR51–59 were preserved; E9/E10 extend the existing stack. All remain OPEN/UNMERGED.
Each initial checkpoint51–59 has one intended incremental commit. E9 has an
implementation and explicit migration-registration repair commit. E10 records
UI acceptance, preflight correction, session-isolation correction and this handoff.
No rebasing/force push or main change was performed.

## Authentication and application boundary

**Local username/password is selected for initial QA.** Enterprise SSO/Entra/OIDC
registration is optional future work, not an initial-QA gate. Existing enterprise
identity interfaces remain reusable; server-side grants and SessionAuthority were
extended rather than replaced.

Application-only additive migration006 adds unique normalized usernames, immutable
account IDs, Argon2id hashes, status/password-change flags, versioned revocation,
bounded shared login budget and immutable security events. No plaintext credentials,
public default account, automatic bootstrap or public privilege assignment exists.
The private operator CLI uses explicit application admin credentials, expected DB,
accountable operator, acknowledgement and hidden interactive password input. It
requires reviewed migrations already applied and never runs DDL/grants itself.

Scoped ADMIN checks old and new scopes; last-admin removal is serialized/denied.
Directory changes and command execution share identity locks; disable, reset, scope
or role change and revoke invalidate old sessions. HTTPS Origin/JSON and session
CSRF protect writes; cookies are Secure/HttpOnly/SameSite=Strict. Login input and
validation errors are bounded/sanitized. Argon2id defaults and session/ingress
capacity remain subject to operator review before real activation.

The actual local login UI talks through the bounded Next proxy to the trusted backend.
Browser storage contains no credentials or session authority. `/login` and
`/engineering/local` require explicit development opt-in; production builds deny
these entrypoints. The operational FastAPI factory mounts no Engineering/local-auth
writers. The injected QA factory accepts development/loopback disposable PostgreSQL
only. A reviewed real-QA startup/transport path is still required; enabling flags
alone cannot turn this fixture into a supported real-QA deployment.

Application migrations002→003→004→005→006 and writer grants were exercised only in
disposable PostgreSQL. Runtime writer differs from migration owner; immutable audit/
revisions/receipts have append-only grants. Wrong DB, Mart anchors, ownership,
PUBLIC/default/inherited privilege and cross-asset tests fail closed. Existing
Reliability Mart is SELECT-only at the application read boundary. No new operational
DB was created or canonical Mart writes introduced.

See [local authentication contract](local-authentication-v1.md),
[database boundary](bundle-e-database.md), [QA runbook](../../deploy/qa/RUNBOOK.md).

## Final security audit and corrections

Immutable audit range: main `eda3595` → initial E10 `142791d34fb2d765d55ddd8b40fd7f0ffab21d87`.
All63 changed files were accounted for:35 authoritative source/config files and28
supplemental documentation/tests. Authentication/ADMIN/session, cross-asset and
independent review, DB privileges, attachments/recovery, HTTP bounds, source safety,
release integrity and default-off gates were traced. Independent bounded reviews
covered authentication, storage and UI/proxy; parent reviewed release/preflight.
Graph generation was stale/missing candidate paths; exact committed-source fallback
was used. This is complete changed-file coverage, not certification of unchanged
collectors or actual unprovisioned QA/production infrastructure.

| Severity | Finding / exact original location | Resolution |
|---|---|---|
| MINOR / security LOW | Prior subject response retained after401 and local re-login: `web/components/EngineeringQa.tsx:14,19,23` at142791d | 1ec149d clears response, drafts, IDs and CSRF on expiry/logout/re-login; identity epoch discards late prior-session responses. Real browser regression and independent repair review PASS. |
| MINOR / functional | Duplicate interpreter/module in `deploy/qa/compose.preflight.yaml:6` versus Docker ENTRYPOINT | bc01da8 passes flags only; actual CLI argument regression PASS. |
| MINOR / documentation | `docs/bundle-e-database.md:31` omitted migration006 | bc01da8 reconciles002–006 sequence. |
| ACCEPTED LIMITATION | Actual QA TLS, DB ACLs, storage/scanner, onboarding and startup not provisioned/approved | Activation remains NO_GO; no claimed real-host validation. |
| ACCEPTED LIMITATION | Shared authentication budget can reduce availability under attack; receipt/transport bounds are not a full downstream handler deadline | Reviewed ingress/capacity/timeout policy remains mandatory before activation. |

No confirmed BLOCKER/MAJOR survived the reviewed changed paths. The sealed audit
retains the LOW finding against its immutable earlier target; the subsequent repair
and actual browser regression are separate evidence and do not rewrite that audit.
Scan ID: `722c58b8-3a9b-4c5a-abbe-aaa4f2dca8c5`. Detailed scan/PoC artifacts remain local,
not committed. Token use for the security review was not available as a measured
scan metric; no invented usage total is reported.

Attachments preserve private opaque file identity, checksum/size/quarantine and
fail-closed scanner results; recovery never silently deletes evidence. An actual
scanner integration, custody, encryption, retention, resource bounds and reviewed
upload/delivery activation still need approval. No frontend attachment upload or
operational storage activation was introduced.

## Actual development acceptance

Disposable fixture administrator provisioned Engineer and independent Reviewer
through server-owned local authentication administration. Random test credentials
remained in restricted private temporary files, never Git or report output.
Real HTTPS browser→Next→HTTP→disposable PostgreSQL exercised:

1. Invalid login and generic feedback; Engineer login and scoped local asset context.
2. Expiry401 and clearing prior-subject response/draft; different-subject login.
3. Inspection draft/submission and independent Reviewer approval.
4. Reviewed immutable inspection evidence linked to an Engineering Case.
5. Independently reviewed case linked to a NADI-native recommendation.
6. Recommendation review, follow-up and Action Board record access.
7. Page reload/session resume, durable records, logout/revocation, responsive layouts.

Current local-auth browser:40 assertions PASS,0FAIL,0SKIP. Legacy source-free trusted
proof browser:25 PASS,0FAIL,0SKIP. Neither is real plant UAT. Browser sources use fixtures;
no PI/Maximo source HTTP was issued. Quality remains separate from freshness and
health; unknown/manual observations never become factual health scores or Maximo WO.

Backend negative tests cover disabled/locked users, login budget, enumeration
resistance, scoped ADMIN denial, forged sessions, missing/invalid Origin/CSRF, expiry,
password reset revocation, concurrency, self-review, cross-asset evidence, wrong DB,
immutable grants and Maximo mutation guards. They do not prove real infrastructure
approval or perfectly constant authentication timing.

## Final test evidence

Commands run from the relevant subproject with isolated fixtures/configuration:

```sh
# Cockpit: loopback disposable application, engineering and Mart PostgreSQL fixtures
# NADI_APPLICATION_TEST_DSN, NADI_ENGINEERING_TEST_DSN, NADI_MART_TEST_DSN
# COCKPIT_CONFIG_MODE=managed DATABASE_URL=sqlite:// NADI_COMPOSE_TESTS=1
PYTHONPATH=.:tests python -m unittest discover -s tests -q
# Maximo: managed configuration, sqlite unit default, fixture-only source adapters
PYTHONPATH=.:/tmp/nadi-phase2-testdeps python -m unittest discover -s tests -q
# PI: managed configuration and disposable Timescale PI_MIGRATION_TEST_DSN
PYTHONPATH=.:/tmp/nadi-phase2-testdeps python -m unittest discover -s tests -q
# Contracts
python -m unittest discover -s tests -q
# Web
npm run check:engineering
npm run check:phase2
npm run check:workflow
npm run check:http-qa
npm run check:bounded-http
npm run check:bounded-proxy
npm run check:local-auth
npm run check:product-safety
npx tsc --noEmit
npm run build
# Actual disposable HTTP/browser fixture, private random accounts supplied by path
python tests/qa/local_browser.py
python tests/qa/browser.py
# Exact-code source-free release/preflight; unresolved approval gates are expected
python -m src.qa.release --output <new-private-manifest>
python -m src.qa.preflight --config <private-config> --release-manifest <private-manifest>
git diff --check
```

| Suite | PASS | FAIL | SKIP |
|---|---:|---:|---:|
| Cockpit full (687 tests,110.042s) | 687 | 0 | 0 |
| Maximo Collector | 181 | 0 | 0 |
| PI Collector, including11 isolated Timescale tests | 191 | 0 | 0 |
| Data contracts / schema parity | 14 | 0 | 0 |
| Targeted preflight/release/identity config after reconciliation | 15 | 0 | 0 |
| Frontend assertions (37+25+38+10+8+9+16) | 143 | 0 | 0 |
| Local-auth browser workflow + expiry/different-subject regression | 40 | 0 | 0 |
| Legacy browser workflow | 25 | 0 | 0 |

TypeScript, Next production build,32-file product-safety inspection and diff-check
PASS. Targeted backend tests are subsets of687, not additional unique test totals.
Initial disposable-fixture setup failures were corrected; a prior incorrectly wired
run skipped112 tests and was superseded by the explicit final687/0/0 run. Resource
warnings from existing SQLite/Psycopg test cleanup were visible; no false claim of
warning-free execution. Real QA UAT/on-host TLS/storage/scanner tests were not run
and remain acceptance gaps, not counted as passing disposable tests.

Clean implementation1ec149d produced98 exact-code artifact entries. Actual source-free
preflight exit2,3 PASS/4 BLOCKED gates, `real_qa_readiness=NO_GO`, source_gets=0/writes=0.
Blocked: local-auth/on-host Origin policy, session/pool policy, storage policy and
accountable approval references. Entra/OIDC is not a missing prerequisite.
The image/Compose argv path was tested without building or deploying an image.

GitHub backend/frontend jobs were successful on preserved PR51–60 heads. PR61 final
HEAD must have backend/frontend SUCCESS before merge authorization is acted upon;
CI conclusion and exact final HEAD are captured in the operator delivery report.
Main currently has no branch protection/rulesets; absence is not authorization to
merge or bypass future requirements. Recheck reviews/checks/protection at each step.

## Controlled merge and rollback proposal

Recommended merge commits:51→52→53→54→55→56→57→58→59→60→61.
**STOP before51; request explicit operator merge authorization.**
For each authorized step: refresh main and expected PR HEAD, verify existing-parent
ancestry and intended incremental diff, inspect current reviews/required checks,
merge using merge commit, verify both parents/new main and final tree. Retarget the
next dependency to main, re-evaluate its diff/checks/mergeability and stop on movement,
conflict or failed gate. Do not force push, squash or bypass protection. Exact final
tree must equal the approved final candidate tree; duplicated commits must not occur.

Repository rollback is a separately reviewed revert of merge commits, preserving
history. No deployment accompanies integration. Future QA migration002–006 requires
private application backup, explicit DB/owner/ACL preflight, deliberate runner,
idempotency and writer audit. On future activation failure, disable approved QA
access/authority while preserving application evidence/files; do not reset Mart,
source DB, journal or collector cursor. No destructive down-migration is proposed.

## Activation blockers and roadmap

Real QA requires: host/DNS/TLS/network; reviewed real-QA startup and frontend secure
transport; exact image provenance; separately provisioned application DB/owner/writer
and audited privilege separation; private admin custody and accountable account
onboarding; password/session/ingress/resource policy approval; actual private
storage/scanner/retention/backup; PdM engineer field sign-off; engineer/reviewer UAT;
explicit per-action provisioning/deployment authorization. Proposed names are not
provisioned resources. Enterprise SSO remains optional future work.

Phase1 remains **CURRENT/PARTIAL**; operational policy/evidence acceptance was not
re-certified. Phase2 local foundation is **CANDIDATE/PARTIAL**, real QA **NO_GO**.
Next after approved merge: separately authorized real-QA activation design and
operator prerequisites, followed by provisioning review; never automatic deployment.

## Safety accounting

Task-attributable production PI/Maximo/CEMS GET=0; Maximo/PI source writes=0;
Maximo WO create/update/status=0; real QA/production DB writes/DDL=0;
deployment/restart=0; operational Engineering activation=0;
Phase1 evidence/journal/cursor/policy mutation=0; real user provisioning=0.
Only disposable PostgreSQL/Timescale migrations, synthetic application records and
local preview processes were used. CEMS/NK unchanged. Existing private artifacts and
operational services were preserved.
