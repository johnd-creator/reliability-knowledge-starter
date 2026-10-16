# NADI-AUD-02B-B5 — Integrated Qualification & Promotion Readiness

## Decision and scope

This is disabled-candidate qualification and a proposed promotion plan. It is not
an operational acceptance, deployment, migration/grant approval or F-03 closure.
**Feature default DISABLED; legacy-writer compatibility RESTRICTED; operational
readiness NO-GO.** Technical outcome and final exact-head CI are recorded in the
DRAFT PR delivery, alongside remaining findings below. A green negative test
proves a refusal works; it does not resolve the limitation being tested.

## Pinned chain and preservation

| Layer | PR | SHA |
| --- | --- | --- |
| main | — | `4914a73fc7b640b6dd0667d0450fdb12aa04c452` |
| B1 | 95 | `ce6a29a29fb55a5c72612bc981e32b220768b27e` |
| B2 | 96 | `86d760c7f3cf8638ef2099f4e545ec315f82916e` |
| B3 | 97 | `662ce7b47c930b3ab312f3ce02223d49544b7094` |
| B4 | 98 | `bee49a345a63bb6083b6dd79650569febd227ba9` |

All four dependency PRs were OPEN/DRAFT and their heads were checked against this
chain. B4 CI [38910099646](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38910099646)
and Engineering CI [38910099867](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38910099867)
were PASS. New branch: `codex/nadi-aud02b-b5-integrated-qualification`, from exact B4.
No dependency branch is rewritten, rebased, merged or pushed by B5.

A private before/after inventory covers 62 existing worktrees (HEAD/status/tracked
diff hashes), original workbook and five PNG hashes. Only the new B5 worktree is
edited. Read-only service/listener inventory found `nadi-primary-web.service` and
`nadi-live-api.service` active; HTTPS3000 listener PID 1844261. No service HTTP,
operational/Persistent-QA database or session was accessed. No collector command,
source request, restart, policy mutation or localhost change was performed.

Graph generation `2026-08-24T09:24:57Z` lacks B1–B4 source. Direct pinned-source
reads supplement the graph; the writer inventory below is bounded to checked-in
Maximo/Cockpit code and does not certify the deployment's actual writer inventory.

## Qualification package

- [F-03 mechanisms, implementation, executed checks and limitations](b5/traceability.md).
- [Immutable migration manifest](NADI-AUD-02B-B5-MIGRATIONS.json).
- [Migration packaging, privileges and writer compatibility](b5/migrations-grants.md).
- [Historical exceptions, governance and operating envelope](b5/policy-capacity.md).
- [Evidence-preserving rollback and proposed merge sequence](b5/rollback-promotion.md).

## Integrated scenario and evidence

The private Unix-only PostgreSQL runner creates synthetic source/canonical/candidate
tables and distinct reader/projector/source-reader/migration-owner roles. It checks
its data directory, on-disk system identifier, fixed DB/role and disabled TCP before
source/test imports. Child environment excludes private DSNs, credentials and
source settings. Python network, unapproved database connections and subprocesses
are blocked during tests. This accidental-I/O guard is not a hostile-code sandbox.

The pipeline runs eligible Equipment and a ready WO plus a year-2000 WO with missing
Equipment. It captures/seals an immutable full manifest, projects the ready row,
records one B2 family and explicitly enrolls B3. Two later full generations leave
the unchanged old WO unresolved. Repairing only local Equipment permits indexed
due selection and exact-source-ID capture; recovery supersedes the old version,
produces matching target/receipt/audit evidence and resolves the current version.
The old run and its original receipt stay unchanged/PARTIAL. Targeted recovery
remains PARTIAL. Only a later full generation can establish full coverage.

Three independently repeated checkpoints are retained in separate fixture schemas:
partial, targeted recovery and final full completion. One collector interpreter
asserts each transition; a separate Cockpit interpreter reads those exact persisted
schemas with a SELECT-only role and evaluates B4. No writer is imported by B4.

Settled local qualification:18 writer/migration/grant/capacity cases +8 reader
cases,0 skips/errors/failures, selected-schema restore84 tables/143 rows PASS, and
6 new negative CI cases PASS. There are32 new B5 unittest cases; the separate
backup/restore workflow is not double-counted as a unittest. Exact-head CI still
qualifies these on supported Python versions. Candidate child processes have120s
CPU/1GiB address-space caps and300s wall timeout; PostgreSQL uses32MiB shared buffers,
12 connections and no TCP. No operational resource settings are changed.
Synthetic source cursors are compared before/after every writer test. No external
Maximo source or acquisition cursor is touched.

Fault coverage includes missing source, unknown scope, invalid mapping, exhausted
poison attempts, expired claim, unfenced legacy target drift, bounded lock contention,
concurrent source change, pre-commit crash, post-commit lost reply, real SQL migration
order/repeat, proof-budget refusal, and historical B1–B4 regression suites.

## Findings requiring separate decisions

**B5-GRANT-01 — source row-lock privilege gap.** PostgreSQL `SELECT ... FOR SHARE`
requires UPDATE privilege on at least one selected table column. B3 `_source(...,
lock=True)` uses this lock for Work Order and exact Equipment verification. A
projector with SELECT-only source grants can full-capture and write canonical
receipts, but cannot execute that replay lock. The synthetic negative test proves
permission refusal; it is not a successful least-privilege replay qualification.
B5 does not silently grant source UPDATE or remove the lock. Required follow-up:
review a constrained locking boundary/role design, source-mutation implications,
trusted function ownership/search_path if proposed, then requalify actual replay
under non-owner credentials. This is outside minimal test/CI changes.

Administrative fixture-owner replay proves transaction behavior, not this missing
permission boundary. Source-reader, non-owner full-capture projector, migration-owner
and SELECT-only B4 permissions are tested separately. Do not report the entire
least-privilege recovery lane as SYNTHETIC_PASS while this gap remains.

**B5-CATALOG-02 — verified narrow candidate correction.** Real 001→006 SQL creates
canonical indexes different from SQLAlchemy create_all. Catalog comparison confirmed
that only the index group differs; columns/types/nullability, constraints, triggers
and function bodies match. B4 previously pinned only the ORM catalog. B5 adds the
complete SQL catalog SHA256 `45e77c7cc8b51de1d10d5e77d29a84607b0f5fbcbc657361e94559d65e25d6a2`
alongside the unchanged ORM pin. No category is omitted or broadly allowed; a removed
SQL canonical index still fails closed. No migration/index is changed. This is the
only runtime-source edit, to the disabled candidate reader, justified by an executed
migration-compatibility failure. Exact-head CI must requalify both schemas.

Technical qualification remains PARTIAL while B5-GRANT-01 is unresolved even when
the narrow catalog correction and all regression tests pass. Operational readiness
remains NO-GO.

## CI and result interpretation

The required B5 integrated matrix on Python 3.11/3.12 supplements existing Collector,
B1–B3 PostgreSQL, B4 PostgreSQL, Cockpit, contracts, CI safety and Engineering/UI
lanes. Failed/skipped/cancelled/missing integrated lanes fail the fresh-runner gate.
Candidate execution has no GitHub token or operational credentials. SHA-pinned
workflow/source checkouts and source-integrity checks remain enabled.

The final PR body records exact candidate/workflow SHA, job/run URLs, executed
counts, failure/skip/I/O counters, private-cluster cleanup and capacity metrics.
Local runs labelled against the B4 base plus an uncommitted B5 diff are development
evidence only. Existing Engineering CI may check a PR merge commit; source/tree
identity must be verified before using that result as candidate regression evidence.

The first local harness failures are retained: schema search_path escaped into the
fixture pool (fixed with a separate engine); a shared checkpoint count assumed no
previous empty scenario (fixed with named membership); and reader tests changed
while an earlier writer phase was already loaded, causing missing `sql_install`
evidence. That run is FAIL, not acceptance; the settled files are requalified together.

## Senior Review handoff

Technical PASS requires integrated behavior, actual migration reader/writer
compatibility, least-privilege recovery and restore evidence to be coherent with no
unresolved technical release blocker. Otherwise report PARTIAL/BLOCKED explicitly.
Operational NO-GO remains regardless of synthetic success until owner/co-location,
backup/restore, migration/grant, legacy writer exclusion, history/absence/stale claim,
resource/retention, Phase 1, AUD-11 and rollout/rollback approvals exist.

Astra F-03 operational status remains OPEN. Stop after the DRAFT PR and report.
Next: Senior Review → separately authorized remediation/merge/operational preparation.
