# F03 night review 01 — local evidence, 19 October 2026

**Verdict: NO-GO to promote the stack as F03 recovery-ready.** Development
integration is CONDITIONAL on the tasks below and new exact-candidate CI.
This batch makes no commit, push, PR, merge, deployment, operational restore,
source acquisition, persistent access change or acceptance decision.

## Reviewed provenance and dependency graph

Current GitHub main at the 15:37 UTC metadata check:
`35f3c101129241745e1795edd78a34c3617dccd7`, after merged PR106. All PRs below
remain OPEN/DRAFT, with no submitted reviews/comments in the fetched snapshot.
All target `main`; GitHub's PR base snapshot/common merge-base is
`4914a73fc7b640b6dd0667d0450fdb12aa04c452`, **not current main**.

| PR | Exact head | Historical exact-head CI | GitHub mergeability |
|---|---|---|---|
| [94](https://github.com/johnd-creator/reliability-knowledge-starter/pull/94) | `71d2f3802b325e1cf36563db556364444305ec7f` | [SUCCESS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38845574783) | clean |
| [95](https://github.com/johnd-creator/reliability-knowledge-starter/pull/95) | `ce6a29a29fb55a5c72612bc981e32b220768b27e` | [SUCCESS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38857614073) | clean |
| [96](https://github.com/johnd-creator/reliability-knowledge-starter/pull/96) | `86d760c7f3cf8638ef2099f4e545ec315f82916e` | [SUCCESS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38861970132) | clean |
| [97](https://github.com/johnd-creator/reliability-knowledge-starter/pull/97) | `662ce7b47c930b3ab312f3ce02223d49544b7094` | [SUCCESS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38866288595) | clean |
| [98](https://github.com/johnd-creator/reliability-knowledge-starter/pull/98) | `bee49a345a63bb6083b6dd79650569febd227ba9` | [SUCCESS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38910099646) | dirty/conflicting |
| [99](https://github.com/johnd-creator/reliability-knowledge-starter/pull/99) | `ef0dc37f0e294897b79a58e681c5e87c5a646d40` | [SUCCESS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38915140502) | dirty/conflicting |
| [100](https://github.com/johnd-creator/reliability-knowledge-starter/pull/100) | `952160cca72724e456b5a4e092301f5e475143e3` | [SUCCESS](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38923341988) | dirty/conflicting |

Run API `head_sha` matches each displayed head. PR98/99/100 also have successful
Engineering runs 38910099867/38915140757/38923342051 at those same heads. These
16 October runs do not validate this uncommitted combination with current main.

Ancestry proves **95 → 96 → 97 → 98 → 99 → 100**. PR94 is an independent
discovery document and is not an ancestor of PR95. No listed head is in current
main. A future integration can preserve that order or consolidate the cumulative
PR100 history while retaining requirements; do not merge all independently as
if they were disjoint patches. PR94 needs separate documentation reconciliation.

Isolated `merge --no-commit --no-ff` of PR100 onto current main conflicts only in
DEV-LOG. Resolution preserves all current-main text then appends the exact stack
additions from the common base. No runtime source conflict was found. Integration
index tree: `234c68d17f7660c11c79b7de680e00c35936bd1f`.

## Findings and concrete tasks

### P1 — logical restore cannot reopen recovery

[deferred_store.py:165](https://github.com/johnd-creator/reliability-knowledge-starter/blob/952160cca72724e456b5a4e092301f5e475143e3/maximo-collector/src/repositories/deferred_store.py#L165)
and [replay_store.py:128](https://github.com/johnd-creator/reliability-knowledge-starter/blob/952160cca72724e456b5a4e092301f5e475143e3/maximo-collector/src/repositories/replay_store.py#L128)
pin SHA256 of textual `pg_get_constraintdef`/`pg_indexes` output. A real logical
roundtrip between two new independent PostgreSQL16.14 clusters changes equivalent
varchar-array deparse forms. For example `ANY ((ARRAY['x'::varchar,...])::text[])`
becomes `ANY (ARRAY[('x'::varchar)::text,...])`.

All 56 table hashes/19 synthetic rows, six source roles, memberships,
database/schema/table/column ACLs, 17 functions including007 ownership/body/
search_path/security/ACL, and 36 triggers match. Nevertheless restricted
ReplayStore initialization raises `deferred constraint/index definition drift`;
the restored queue remains PENDING. Direct SourceLockBoundary passes and eight
source mutation/admin attempts are denied. B2 source/restored signatures are
`faca19addbe32d3e024ca83c8421c3f5cb6f60e0e7a738f67760d38daf7af92a` /
`9b2bbd375dee865741e1f24d5089a27090e1c2179f0ed1083170eb304c6b45d4`;
B3 signatures differ too. This is an availability failure with data retained,
not demonstrated data corruption or access escalation.

**Task:** specify versioned, reviewed structural capability checks or a reviewed
set of restore-equivalent signatures. Preserve rejection of changed predicate,
columns, uniqueness, constraints, trigger attachment/body and privilege drift;
do not broadly strip casts, disable checks or change constants to whatever a DB
returns. Add independent-cluster logical restore to CI and require restricted
replay through DONE plus read-side coverage after restore. Current data-only B5
backup test at `.github/scripts/qualification_ci/backup.py:37–49` intentionally
omits owners/ACLs, uses the same cluster and compares rows only; its PASS is
insufficient for this gate. Existing scope disclosures are accurate.

### P2 — dependency normalization differs from accepted legacy behavior

[projection_store.py:116](https://github.com/johnd-creator/reliability-knowledge-starter/blob/952160cca72724e456b5a4e092301f5e475143e3/maximo-collector/src/repositories/projection_store.py#L116)
normalizes only WorkOrder.equipment_id; Equipment.id is compared raw. The accepted
source model allows raw lowercase IDs. Equipment `a` and WO reference `A` are
accepted by legacy normalized membership, but the candidate captures DEFERRED /
MISSING_LOCAL_EQUIPMENT. The acceptance repro fails on exact unmodified PR100.
The restricted helper's raw lookup at migration007:60 has the same assumption.

**Task:** establish a consistent exact raw-to-normalized identity contract across
capture, source fingerprint and restricted source locking. Require a unique
normalized match; explicitly reject collisions. Add lowercase, whitespace and
ambiguous-normalization regressions. Use an additive reviewed migration for a
changed helper contract; do not silently edit immutable007/body pins or alter
source records to make tests pass.

### P2 — no explicit enrollment path for a later recovery generation

[replay_store.py:205–207](https://github.com/johnd-creator/reliability-knowledge-starter/blob/952160cca72724e456b5a4e092301f5e475143e3/maximo-collector/src/repositories/replay_store.py#L205)
keeps one lifetime queue row per family. After first recovery DONE, a later full
capture creates a new OPEN obligation for changed source input. Registering that
current obligation raises `existing queue requires explicit policy reconciliation`.
The old terminal row is excluded from due selection. This is reproducible after
successful first recovery and a repaired second dependency.

Terminal immutability is intentional (B3 implementation:198); the finding is the
missing **audited explicit next-generation enrollment** capability. No automatic
reset/unblock is recommended. **Task:** either specify append-only generation
enrollment with policy/attempt/history/fencing isolation and regressions, or
explicitly scope acceptance to one enrollment per family and document the manual
governed path. Never delete/reset the terminal queue or raise caps silently.

### P2 harness — uncertain startup could leave its own cluster running; fixed locally

The four original PG controllers set `started=True` only after `pg_ctl -w start`
returned successfully. A server can be live despite timeout/nonzero wait result.
Local patch adds `.github/scripts/maximo_ci/owned_cluster.py` and seventeen tests,
and changes the four controllers. It records the attempted start beforehand,
pins private directory inodes/system identifier, opens pidfd before verifying
executable/-D/owner/pidfile, signals only that descriptor, then confirms stopped.
There is no raw-PID/pg_ctl-stop fallback. Cleanup and original failure are reported
separately; malformed prepare evidence cannot remove the cleanup report.

Independent source review approved the final patch. All four real qualification
fixtures stopped. Real post-start nonzero and timeout fault injections both keep
their expected FAIL/original error and report OWN_CLUSTER_STOPPED. No recovery
logic, migration, policy or access-control relaxation is included in this patch.

## Executed verification

Local interpreter is Python3.14.3, PostgreSQL16.14. These are local runs, not new
GitHub CI. Exact-source tests use unmodified detached PR100 plus the locally fixed
controller only; source remains clean. Integration tests use current main plus
uncommitted PR100 and cleanup. Their runner `tested_sha` field is the base main
SHA, **not an immutable candidate SHA**; `f03-night-integrated-source-manifest.json`
records tested content (aggregate `691cbbed7f2caced409ea5517c720793f4c707a0395f0733f732a7fa0017f4eb`).

| Run | Actual result |
|---|---|
| Exact PR100 B1/B2/B3 PG | 133/133 PASS |
| Exact PR100 B4 reader PG | 38/38 PASS |
| Exact PR100 B5 writer/reader | 18+8 PASS; old limited data-only restore PASS,84 tables/143 rows |
| Exact PR100 FIX01 restricted writer/reader | 39+2 PASS; source direct-share denied; helper-backed replay PASS |
| Extra actual OS-process claim/fence test | 1/1 PASS: two forked processes, exactly one claim; expired fence3 refused, fence4 reaches DONE |
| Two extra recovery acceptance repros | RED: one assertion FAIL, one CaptureError; zero skips/I/O violations |
| New independent-cluster full logical restore | FAIL as above;3 negative controls detect ACL/owner/trigger drift with unchanged row hashes |
| Integrated Maximo offline suite | 240/240 PASS; no skips/expected failures/forbidden I/O |
| Integrated Cockpit integration/coverage suite | 43/43 PASS; no skips/forbidden I/O |
| Main's private SQLite rehearsals retained in combination | 6/6 PASS |
| CI safety/unit regressions including cleanup | 48+10+6+8 =72/72 PASS, including17 cleanup regressions |
| Two real uncertain-start cleanup rehearsals | expected nonzero/timeout FAIL reports; both OWN_CLUSTER_STOPPED |

Old-WO/later-Equipment repair, supersession, receipts, no source-cursor advancement,
fencing, source/dependency changes, lost acknowledgements and restricted helper
behavior have concrete passing coverage. Existing thread tests use independent
DB connections; the extra process test establishes actual separate OS processes.
It does not prove coexistence with active legacy writers.

Initial tooling initdb failure occurred before any server start (missing extracted
sample file); tooling only was corrected. The first process diagnostic's sandbox
Unix socket EPERM ran zero tests, stopped/not-running confirmed, and is retained
as attempt1 evidence; the same own-fixture run with socket permission passed.
One intermediate restore-harness import error was corrected before the final
clean rerun; the final restore result remains FAIL, not hidden as a harness issue.

## Boundaries and next decision

All DBs are synthetic, new, Unix-only, private0700, and have distinct verified
system identifiers; all tested servers stopped via verified pidfd cleanup.
Synthetic roles/grants exist only in those stopped fixtures, with no password
creation. No operational DB/source/auth/session was accessed for these tests.
No production-shaped backup, PITR/WAL, physical restore, live concurrent backup,
retention/RPO/RTO endorsement, migration promotion or runtime co-location test
was performed. Graph coverage was UNKNOWN; exact source was read directly.

F03 remains OPEN/NO-GO. GOV03 expiry remains 2026-10-13T00:00:00+07:00; no extension,
rollback disposition or owner/engineer acceptance is invented. An expiry review
and operational endorsement are separate gates. FAU-7's Done status does not
close FAU-11 or F03. The next reviewable work is the three concrete recovery tasks,
then fresh candidate CI/rehearsal and explicit human promotion approval.

Machine evidence and standalone repros are retained in the task workspace's
`review-evidence/f03-night-*` files; this document and cleanup patches are local
and unpublished. Final runtime preservation is recorded separately in
`f03-night-runtime-preservation.json`.
