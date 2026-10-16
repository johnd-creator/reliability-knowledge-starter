# NADI-AUD-02B-B4 — Projection Coverage Status & Reconciliation

## 1. Executive summary

Disabled, internal read-only candidate. B4 distinguishes latest activity from
last complete population coverage, current deferred families, immutable receipt
proof, replay stages and unknown legacy history. It cannot authorize collection,
replay, migration, engineering methods or rollout. **Astra F-03 remains OPEN.**

The candidate is not wired into existing API routes, startup or environment
activation. Legacy operational behavior and public DTO/schema remain unchanged.
Only source-free synthetic databases were used; operational/Persistent-QA stores,
services, sessions, sources, localhost:3000 and freshness policy were not accessed.

## 2. Exact dependency chain and baseline

| Layer | Exact SHA | Preflight |
| --- | --- | --- |
| main | `4914a73fc7b640b6dd0667d0450fdb12aa04c452` | Verified remote |
| B1 / PR95 | `ce6a29a29fb55a5c72612bc981e32b220768b27e` | OPEN / DRAFT |
| B2 / PR96 | `86d760c7f3cf8638ef2099f4e545ec315f82916e` | OPEN / DRAFT |
| B3 / PR97 | `662ce7b47c930b3ab312f3ce02223d49544b7094` | OPEN / DRAFT |
| B4 | `codex/nadi-aud02b-b4-coverage-status` | New isolated worktree from exact B3 |

Chain: main → B1 → B2 → B3 → B4. B3 exact-head
[CI 38866288595](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38866288595)
was verified PASS. No dependency PR/branch is rewritten, merged or updated by B4.

The graph generation predates the candidate and Integration code; coverage checks
reported missing paths. Relevant source, migrations, tests and CI were inspected
directly in the pinned worktree. Graph absence is not completeness evidence.

## 3. Incremental and cumulative changed files

Incremental B3 → B4:

- `reliability-cockpit/src/domain/projection_coverage.py`: internal v1 evidence,
  run activity, manifest/debt/replay aggregates and explicit proof completeness.
- `reliability-cockpit/src/repositories/projection_coverage.py`: bounded SELECT
  queries, identity/grant/schema preflight and receipt reconciliation.
- `reliability-cockpit/src/repositories/mart_database.py`: opt-in repeatable-read
  snapshot using the existing read-only engine/facade; existing reads unchanged.
- `reliability-cockpit/src/services/projection_coverage.py`: explicit opt-in
  conservative adapter for a caller-supplied existing IntegrationStatus.
- `reliability-cockpit/tests/test_projection_coverage.py` and `tests_coverage_pg/`:
  synthetic contract, role, status, bounded-query and cross-component tests.
- `maximo-collector/tests_postgres/coverage_writer.py`: disposable-only genuine
  B1–B3 fixture generation in its own interpreter. Never operational wiring.
- `.github/scripts/coverage_ci/`: isolated component runners, private Unix-only
  PostgreSQL lifecycle and negative qualification tests.
- `.github/workflows/nadi-maximo-collector.yml` and its existing qualification
  tests: required B4 matrix lane and failure gate; pinned/read-only model retained.
- This report and append-only DEV-LOG checkpoint.

Cumulative main → B4 also includes the unmerged B1/B2/B3 capture, MartWriter,
ledger/replay candidates, migrations and tests. The PR lists both diff inventories.
Migrations **004/005/006 are unchanged by B4**. No operational schema or grants
are installed. No public schema, API, PI integration implementation or policy
file changes are included.

## 4. Current assumptions and candidate read model

The existing IntegrationMartReader records legacy `last_status` and
`last_success_at` for both factual projections. IntegrationStatusService derives
Mart freshness from those timestamps. This is accepted legacy activity semantics,
not proof of B1 capture membership, B2 reconciliation or B3 replay completion.
Those defaults remain intact; B4 is an additional opt-in evaluation only.

Internal `projection-coverage-internal-v1` independently records:

- Latest fenced run UUID, recorded state/start/completion, FULL or RECOVERY_BY_ID,
  sealed flag and continuation. Failure or unfinished activity is never hidden by
  a previous success.
- Recorded last complete pointer/time and independently revalidated proof. A
  historical complete run and current complete coverage are different facts.
- Per-domain captured/acknowledged/projected/unchanged/approved-exclusion/deferred/
  failed/unprocessed counts for the latest manifest.
- Current outstanding/OPEN/ELIGIBLE/BLOCKED/RESOLVED family counts, historical
  superseded versions and unique unlinked B1 identities.
- Replay phase counts, expired/stale claims and policy mismatch.
- Explicit domain, fixed BSR/IP scope, mapper/deferred/replay epochs,
  reconciliation result and proof-complete flag. Source freshness is deliberately
  NOT_EVALUATED; source collection needs independent accepted observations.

No Registry count is inferred from technical Asset inventory, and no Work Order
count is interpreted as failures or equipment condition.

## 5. Debt and replay aggregation

Current debt is counted once per exact B2 family through its current version.
Historical superseded versions are separate lineage facts, never added to current
outstanding debt. An inconsistent active noncurrent version refuses proof.
Unlinked B1 receipts are deduplicated by exact source identity within the bounded
domain history; repeated attempts do not create independent source records.
No old debt is enrolled, deleted, forgiven or replayed by a status read.

Replay has one row per family. PENDING, CLAIMED, CAPTURED, WRITING, FAILED,
PROJECTED, DONE and BLOCKED remain internal workflow facts, not public trust enums.
Their counts must not be summed with debt as a new population. A stale queue pointer
is explicitly unreconciled, including a historical DONE row followed by newer debt.
A queue phase alone never proves readiness or resolution. DONE requires the exact
current B2 resolved event/receipt; PROJECTED remains unfinished reconciliation.

Incompatible debt epochs cannot be filtered out and disguised as zero debt.
Missing capability, failed proof or exceeded limits returns UNKNOWN/unavailable
counts; invalid capability/policy/privilege evidence remains safely non-CURRENT.

## 6. Reconciliation invariants

One REPEATABLE READ, database-enforced read-only snapshot covers both domains and
all metadata/proofs. Each sealed manifest's ordered ordinal/source/fingerprint
hash and item count are reconciled. Continuation must have its acknowledged prefix.
Only the existing reviewed non-BSR WO-prefix exclusion predicate is accepted;
unknown scope cannot become a proven exclusion.

Resolved current debt requires its immutable resolved event, exact occurrence,
matching family/source/fingerprint, sealed run and terminal committed receipt.
Canonical target values are read privately in byte-capped SQL and hashed using
the existing B1 encoding. Actual values and target sidecar digests must match the
receipt. These values, including canonical provenance, are never returned.

A recorded full COMPLETE run must be sealed, fully acknowledged, terminal and
match the domain's recorded complete pointer/time. The two writer clock_timestamp
calls may differ slightly; completion must precede its recorded domain timestamp,
not be incorrectly required to equal it byte-for-byte.

Current unresolved/unlinked debt, unfinished replay, stale claims, failed/latest
partial activity or incomplete proof prevents current complete coverage. Targeted
recovery is never FULL. A successful recovery does not rewrite an old PARTIAL run.
A last complete pointer can remain a historical fact while current proof is stale,
partial, invalid or unknown. Source cursors/business timestamps are not queried as
projection progress or completeness evidence.

## 7. Read-only role and explicit database boundary

The caller must explicitly supply the existing `MartDatabase` and expected
owning database identity. There is no legacy Cockpit fallback or environment DSN
lookup in the candidate reader. Disabled/default and missing database paths do
not connect. PostgreSQL read-only transaction state and expected database name
are checked in the snapshot.

The synthetic role `nadi_b4_reader` has SELECT/column-SELECT and schema USAGE only;
no superuser, createdb, createrole, replication, inheritance or administrative
ownership. Database CREATE/TEMP privileges are revoked in the disposable fixture.
The reader verifies administrative flags, schema/database creation capability,
and table **and column-level** DML/REFERENCES/TRIGGER privileges. Fixture owner or
an INSERT(column) grant fails preflight even if a facade looks read-only.

The role cannot select capture payloads, source Work Orders or source cursors.
It can read only reviewed candidate evidence and canonical target proof. Tests
turn transaction READ WRITE on deliberately to prove actual SQL grants still
reject DML/DDL; facade restrictions alone are not called role qualification.
No production grants are inspected or changed.

## 8. Conservative trust-state compatibility

A caller supplies an existing IntegrationStatus plus its independently governed
FreshnessPolicy. B4 never instantiates a collector observation/source client.
Default-disabled reconciliation returns the exact same DTO object/serialization.

For enabled evaluation:

| Evidence | Existing supported public state |
| --- | --- |
| Missing schema, legacy-only or unverifiable/limited proof | UNKNOWN |
| Invalid policy/capability/privileged reader or blocked queue | BLOCKED or safely UNKNOWN when the evidence cannot be classified |
| Partial/deferred/failed/latest incomplete activity | DEGRADED |
| Fully verified coverage but old complete timestamp | STALE |
| Fully verified and recent, independent availability/source collection gates pass | May remain CURRENT |

Existing BLOCKED, NOT_CONFIGURED, unavailable or other non-CURRENT gates cannot
be waived/upgraded by the candidate. Source collection is reevaluated separately
using its original policy and observed timestamp. PI and mapping components and
Registry coverage are byte-identical. The Mart projection clock uses only the
verified complete time, never the latest partial attempt or source changedate.
No freshness threshold, approval window, review checkpoint or expiry is changed.

## 9. Public-contract compatibility

No public routes, DTO fields, enum values, schemas, login or RBAC behavior change.
The adapter uses only existing reasons/states and keeps richer evidence inside
its internal result, including separate legacy activity time. Existing Integration
UI fixtures, DTO schema validation and PI/source/mapping preservation tests run.

A future detailed endpoint needs a separately versioned contract and trusted-actor
review. Fixed BSR/IP filtering is not caller authorization. Do not publish run
identifiers or diagnostics automatically, and never expose obligation IDs, source
identities, payloads, owner/fence identities, SQL errors or credentials publicly.

## 10. AUD-11 vocabulary alignment

| Term | Recorded fact / derived result / policy evaluation |
| --- | --- |
| Started activity | Run started_at and recorded state; not success |
| Successful complete coverage | Full sealed terminal manifest plus current debt/receipt proof |
| Partial coverage | Recorded PARTIAL, unresolved or unfinished evidence; non-CURRENT |
| Deferred debt | Current B2 family/version facts; not another source record |
| Failed attempt | Recorded FAILED; preserves older complete fact separately |
| Aborted/unknown attempt | Unfinished/expired claim or missing evidence; do not invent an abort event |
| Last complete time | Recorded full-run completion, independently validated |
| Evidence validity | Bounded snapshot, schema/grant/manifest/receipt checks |
| Run identity | Internal UUID; not a source identity or public actor |
| Source freshness | Independent acquisition evidence/policy |
| Projection freshness | Verified complete timestamp evaluated with existing policy |
| Legacy history | UNKNOWN coverage even when SUCCEEDED activity exists |

No standalone AUD-11 implementation/proposal was available in the pinned repository;
repository-scoped PR/issue search found only cross-references in existing audit
work. This map aligns the supplied B4 brief and B3 handoff. Astra endorsement is
PENDING, not manufactured. Full AUD-11 monitoring and policy approval are outside B4.

## 11. Test matrix and executed results

Collector and Cockpit both use a Python package named `src`. Separate interpreters
select the exact component source root. Genuine B1/B2/B3 writers generate synthetic
scenarios; a different Cockpit interpreter evaluates them with the SELECT-only role.
The read implementation never imports the writer or its admin capabilities.

The disposable runner verifies on-disk cluster identity, data directory, Unix-only
listener, database/role and private context location before fixture preparation and
reads. Only its own cluster is stopped; all evidence is retained. Connection guards
reject other addresses/databases/users/options and unapproved processes. The only
client-side psycopg context allowed is its typed SQLAlchemy AdaptersMap; it cannot
redirect the verified connection. This is accidental-I/O protection, not a hostile
Python/native-code sandbox.

Executed local suites are recorded separately in delivery evidence: full Collector
offline/AUD-01, full B1/B2/B3 private PG, affected Cockpit integration/observation/UI
contract + B4 service tests, the complete canonical contract suite, B4 writer-reader
PG tests, existing qualification security tests and new negative CI cases.
| Local suite | Executed result |
| --- | --- |
| Full Collector offline / AUD-01 | 240 PASS |
| Existing B1/B2/B3 disposable PG | 133 PASS |
| Cockpit integration/observations/UI/B4 | 43 PASS (18 new B4) |
| Complete canonical contracts | 14 PASS |
| New B4 writer-reader PG | 38 PASS |
| Existing CI security regressions | 23 PASS |
| New B4 CI negatives | 10 PASS |

There are 66 new B4 cases: 18 service/policy, 38 actual PG and 10 CI negatives.
Intermediate capability-pin runs are derivation, not acceptance. All final suites
must execute without skips or forbidden I/O. Supported Python 3.11/3.12 qualification is required on the delivered exact HEAD;
local Python 3.14.3 / PG18.6 alone does not establish that gate.

Cases cover full/partial/legacy/unlinked history, repeated families/supersession,
resolved targeted recovery, expired and stale claims, retry/poison/absence,
latest-failed versus old complete, mixed domains, schema/index/guard drift,
explicit limits and timeouts, target digest drift, grants, unchanged public shape,
PI independence and original policy thresholds. Missing suites, skips, external
I/O and an incomplete cross-component lane must fail qualification.

Development failures were retained: initial capability-pin derivation; a SELECT
facade correctly refusing a test's SHOW statement (test changed to current_setting);
a missing-component runner failing before writing structured FAIL (fixed); and a
strict fixture guard initially rejecting SQLAlchemy's typed client-only adapter
context. No source/runtime guard was disabled to make these cases pass.

## 12. Cross-component exact-head CI

The existing immutable Maximo qualifier now has a required B4 lane on Python
3.11/3.12. Explicit triggers include affected Cockpit reader/service/domain/tests,
contracts, Collector and CI tooling. Candidate execution receives no GitHub token
or production secret. All checkouts and action versions remain SHA-pinned, and the
final fresh-runner gate requires Collector, B1–B3 PG and B4 qualification success
before rechecking the PR HEAD. Failed/skipped/cancelled/missing B4 lanes fail closed.

The B4 lane separately executes Cockpit tests, all contracts, source-free actual
writer/SELECT-only-reader PG and negative infrastructure regressions. Existing
Maximo suites remain required. Existing Engineering/UI CI is independent and is
not substituted for cross-component proof. Workflow triggers do not add general
root-document paths; GitHub PR path filtering still considers the cumulative PR
diff, so a docs-only follow-up within a code PR may requalify its exact HEAD.

The DRAFT PR body/final report provides actual run URL, SHA and read-back JSON test
counts for each matrix job. Earlier B3 green results or dirty-worktree runs labelled
against the B3 base cannot qualify the final B4 HEAD. A containing report cannot
embed its own final Git hash; use the exact-head check/artifact metadata.

## 13. Security and failure-mode review

- No new public entrypoint, trusted-actor bypass, source acquisition or scheduler.
- No writer/admin imports or mutation/commit method in the reader facade.
- Read queries have finite rows/runs/bytes/queries/time, preserve the existing
  per-statement timeout ceiling and use one consistent snapshot.
- Missing/drifted/expired/limited evidence produces sanitized reason codes and
  unknown counts, not exception text or fabricated zero.
- Canonical row JSON is capped in SQL; captured payloads are never selected.
- Unknown/incompatible epochs and active noncurrent versions cannot be omitted
  to certify CURRENT. Unready workflow states never become readiness evidence.
- Actual SELECT-role tests supplement transaction/facade controls. They do not
  authorize operational migrations or prove operational grants currently match.
- Independent source/PI/Registry/policy and engineering meanings remain intact.

## 14. Remaining operational blockers

F-03 remains OPEN. No operational candidate migration/grants, reader activation,
legacy writer exclusion, historical backfill, replay permission, policy renewal or
runtime acceptance is granted. Production cardinality/performance/retention remain
unqualified; a bounded UNKNOWN is intentional rather than an unlimited history scan.
Current operational freshness-policy state was not read or modified; historical
expiry/checkpoint obligations remain separately governed, never extended by B4.

## 15. B5 integrated qualification handoff

Senior Review must still qualify combined B1–B4 semantics, schema packaging and
checksums for unchanged 004→005→006, owner/admin versus least-privilege reader grants,
concurrent legacy-writer exclusion and exact-main integration/merge ordering.
Rollback must preserve manifests, debt, receipts, sessions and backups. Operational
unknown-history reconciliation, source absence, stale/abandoned-claim decisions,
resource/performance/retention budgets and Phase 1 acceptance need separate approval.
A public detailed status contract/actor review and Astra AUD-11 vocabulary endorsement
remain independent. No operational rollout is implemented here.

## 16. Senior Review recommendation

Review incremental B3→B4 and cumulative main→B4 together. Accept only the disabled
synthetic candidate if all final exact-head cross-component checks pass. Keep
PR95/96/97 independent and DRAFT; no automatic merge or deployment. Next gate is
Senior Review → NADI-AUD-02B-B5. This task stops after its DRAFT PR and report.
