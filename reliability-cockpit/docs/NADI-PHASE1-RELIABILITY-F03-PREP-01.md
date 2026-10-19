# NADI-PHASE1-RELIABILITY-F03-PREP-01

Prepared 19 October 2026 against main `8bb1bcb2c485feeb792235c64b5aef6bbce5e3cc`. Initial review checkpoint was local-only. The user subsequently authorized commit/push, a draft PR to main and exact-head CI. Merge, auto-merge, deployment, active runtime changes and F03 activation remain unauthorized.

| Priority | Concrete scope | Acceptance criteria | Boundary / blocker |
|---|---|---|---|
| 1 — Status | Reconcile roadmap, repository status and append-only DEV-LOG with verified PR105 source and CI | Correct main/PR statuses, immutable CI links, runtime/source/acceptance separated; historical entries preserved | Linear handled elsewhere; no new domain acceptance |
| 2 — Phase1 reliability | Audit exact identity bindings and provenance on read paths; reproduce misleading CURRENT/missing states, fix only demonstrated software defects | Invalid/missing identity/provenance cannot become accepted evidence or PASS; real zero and unknown/stale remain distinct; valid evidence and factual data unchanged; hermetic regression tests | Wider Maximo↔AF mapping and condition freshness thresholds require attributable owner/engineer evidence; no seeding/verification, policy or active DB edits |
| 3 — F-03 preparation | Trace actual collector→Mart recovery dependencies and test safe recovery/backup/rollback boundaries on temporary fixtures | Fault injection preserves source/cursors and evidence; restore targets a separate disposable destination; rollback fails closed; report precisely which PostgreSQL/role/global-metadata/operational gates remain unproved | Astra F-03 is OPEN; PR94–100 recovery stack is unmerged. No active-system grants/security/credential changes, migrations/restore, deployment or collector restarts; isolated synthetic fixtures only |

## Verified starting facts and exclusions

PR105 source integration and exact-head candidate/main CI passed. The laptop control checkout and active preview are separate from main; all 35 containers and existing dirty files remain protected. Single-pilot identity acceptance does not approve all Registry assets. Source facts, quality, collection/projection time, review, operational readiness and device condition remain independent.

PdM engineer validation is explicitly deferred by the user. Do not create measurements, threshold approvals, human signoff, factual mapping matches or new production SLAs to obtain PASS. Monitoring approval expiry must be reconciled with accountable evidence rather than inferred from old CURRENT headings. Reads and tests must not contact production sources or extract user sessions.

Astra F-03 concerns recoverable Mart projection and is not AUTH-F03's configuration approval gate. Existing draft PR100 (`952160cca72724e456b5a4e092301f5e475143e3`) reports technical synthetic qualification but operational NO-GO, including unresolved full metadata/global-role restore and source-lock grant approval. Its historical fixture privilege exception is retained. This batch does not run the unmerged F03 source-lock/helper fixture. Isolated Phase1 tests use a new disposable cluster and a synthetic SELECT-only reader role; this is separate from active-system security changes.

Earlier PR100 counts are historical evidence, not tests rerun by this batch.

## Observed local API — not candidate deployment

At 2026-10-19 12:35:58 UTC, one credential-free read of the existing local
`/v1/reliability/integration-status` returned 845 registered assets, one verified
mapping, one approved/projected pilot signal, no ambiguous mapping; technical PI
490 total /433 active /433 snapshots. MAXIMO was DEGRADED with COLLECTOR_ERRORS
and NO_SUCCESSFUL_ACTIVITY; its bounded observation supplied no successful time.
This does not prove no historical successful collection outside the observation
window. PI collection was CURRENT independently of BAD source quality. Factual
Mart projection was CURRENT; condition source/projection remained UNKNOWN with
original 8 October timestamps and unset condition thresholds. No fresh condition
measurement, mapping or policy was created to change that result.

Effective monitoring limits in that DTO remain660/660/1800. The recorded GOV03
hard expiry is **2026-10-13T00:00:00+07:00**; post-expiry disposition is **NOT ESTABLISHED**. Search covered committed main plans/, reliability-cockpit/docs/ (including JSON), DEV-LOG and related main history since12 October. GOV03 lines101–121 name Fauzi, require explicit renewal/manual rollback and do not record execution; the72h review records PARTIAL/UNKNOWN with no policy action; later UX-ID-01 lines119–121 retain UNKNOWN absent separate accepted evidence. Older GOV02 calendar15Oct is superseded by GOV03 exact13Oct. No attributable later renewal or completed rollback was found in that scope; external evidence may exist. An accountable owner must reconcile current approval/expiry
before monitoring can be represented as currently approved. This task neither
disables nor extends settings. Condition use-age policy and wider asset identity
remain evidence/owner decisions, not software defaults or deferred PdM signoff.

## Reproduced defects and local fixes

| Finding | Reproduction on baseline | Local candidate behavior | Evidence path |
|---|---|---|---|
| P2: missing/wrong-mapping projection attestation can leave a false complete pilot PASS | Delete or change the synthetic state row after valid evidence; both cases returned PASS | Retain original evidence/counts/source times; projection UNKNOWN with PROJECTION_ERROR, no PASS; malformed statuses also fail closed | `tests/test_phase1_read_integrity.py`; `repositories/condition_integrity.py`; `repositories/integration_reader.py` |
| P2: detail read did not bind every stored JSON identity to its row | Swap evidence signal JSON or alter selection JSON ID; detail could accept a duplicate or silently return a partial set | Shared row/asset/mapping/signal/approval/provenance/collection-instant validation on both read paths; inconsistent records become existing safe PROJECTION_ERROR, no fabricated zero | `services/condition_query.py`; `repositories/condition_integrity.py` |
| P2: crash could retain factual projection SUCCEEDED | Fail the third persist after an earlier success and partial new writes | Record FAILED using existing state columns; preserve last successful watermark/time, source cursor/floor and original exception; first failure has no invented success/checkpoint | `maximo-collector/src/services/local_mart_projector.py`; `test_f03_local_rehearsal.py` |
| P2: aggregate accepted duplicate attributes/semantics rejected by detail | Corrupt two matching selection/evidence documents with distinct IDs but the same attribute or semantic; aggregate still passed | Validate the complete ProjectionPlan per mapping before coverage, matching detail | `repositories/integration_reader.py`; paired regressions |
| P2: same-mapping old state could attest newer evidence | Keep fresh evidence while restoring attempted_at one second older; aggregate still passed | Inconsistent attestation becomes PROJECTION_ERROR/UNKNOWN; original evidence retained, invalid latest-attempt not asserted | `repositories/condition_integrity.py`; both read paths |
| P3: UNKNOWN could have no reason | Unset policy or configured policy with missing timestamp | Existing UNKNOWN_FRESHNESS_POLICY / UNKNOWN_TIMESTAMP reasons explain applicable dimensions without inventing thresholds | `services/integration_status.py` |

Original six Phase1 reproductions failed before repair; two collector failure
reproductions also failed before repair. Additional positive/negative tests cover
original evidence preservation, collected-column mismatch, malformed state,
recent-success versus failed attempt, and non-UTC time/replay. Technical database
clocks normalize to UTC; original source/collection representation stays in JSON.
No product migration, permission contract, public schema, factual mapping or condition-unit change. An independent source reviewer found the latter two P2 gaps; three new failing reproductions confirmed them, then passed after fixes. Follow-up independent review found both closed and no new blocking source finding; reviewer did not execute tests.

## Executed validation

- Initial focused run151 =140 pass/11 skips. Correction: **10 PostgreSQL skips +1 UI dependency skip**, not11 PostgreSQL skips.
- Final focused suite on a private **PostgreSQL18.6** cluster: **169/169 pass, zero skips**. Includes15 new integrity cases on SQLite and the same15 on PostgreSQL, plus10 existing PostgreSQL acceptance cases; actual UI render uses already-copied workspace dependencies and Node22. No dependency install or active frontend write. Private Unix-socket cluster stopped and deleted after the run.
- Same final focused suite on an existing immutable **PostgreSQL16.14** image: **169/169 pass, zero skips**. New owned fixture had network=none, no published ports, private socket path and tmpfs data only. Synthetic reader-role/schema changes stayed inside this fixture; its exact container ID was stopped/removed and socket directory deleted. Initial fixture startup failures were diagnosed and cleaned up before the successful run; no active service was restarted.
- PostgreSQL acceptance mapping: typed values/BAD quality, model/schema rejection, full/oversized attribute references, source/proxy boundary, ASGI detail+aggregate contracts, replay/conflict/older/governance, source-unavailable retention, canonical migration idempotency and SELECT-only reader separation. New PG cases directly cover changed selection/evidence binding, missing/wrong/old attestation, duplicate sets, offset/replay, UNKNOWN reasons and unchanged valid reads. These are Phase1 schema/data/read checks, **not** F03 global-role/helper/backup recovery qualification.
- Direct local Maximo suite originally **208/208 pass, zero skips**. Prepublication use of the actual CI runner exposed six file-rehearsal failures: standard CI deliberately allows memory-only SQLite. Its guard remains unchanged. Rehearsals now live in `maximo-collector/rehearsals/` with a dedicated guarded runner and mandatory CI step: **202/202 standard +6/6 rehearsal PASS**, zero skips/blocked I/O. **29/29 qualification/safety tests PASS**, including outside path/URI/traversal/symlink, ATTACH, unwrapped connections, environment, socket/subprocess/non-SQLite and caught-violation negatives. The private-file runner allows only its own new0700 root; it does not allow external database paths. Both suites are required in each existing Python3.11/3.12 matrix job and retain selected-SHA/source-cleanliness and final PR-head recheck gates.
- Canonical contract suite: **14/14 pass**. Existing typed contract vocabulary
  supports the added reasons; no schema or API version was changed.
- `git diff --check` and local documentation references checked. At the local review checkpoint, no remote CI/publication or active service lifecycle operation had run. Owned disposable test services were cleaned up. The publication authorization below supersedes only that publication boundary.
- Current codebase graph/checkout skills cannot certify these new paths. The
  runtime root `.agents` is empty and `.agents/skills` is absent in both source
  and scratch; relevant catalog instructions and direct source review were used.

The new integrity module and PostgreSQL acceptance class are added to the existing Engineering CI test list. A separate ephemeral `nadi_mart_test` database keeps destructive fixture schema recreation away from application fixtures; a synthetic SELECT-only reader exists only there. Existing exact-head assertions and all prior tests/guards are retained. Workflow YAML and embedded fixture-creation Python parse/compile locally.
The user has now authorized draft publication and exact-head remote CI; terminal results belong to the draft PR handoff. Earlier PR105 CI is not evidence for this new candidate.

## F-03 recovery and backup/rollback preparation

The test controller creates only its own private temporary directory and SQLite
source/Mart files. It accepts no DSN or operational target, creates no roles or
grants, and never instantiates a production source client. Recovery uses a fresh
projector object after injected failure; it is not a host service restart test.

| Rehearsal | What passed | Explicit limit |
|---|---|---|
| Mid-batch interruption and retry | Partial target writes remain visible as FAILED; successful checkpoint unchanged; fresh object drains remaining rows; replay does not duplicate; source/cursor/floor table hashes unchanged | No PostgreSQL locking, process crash, moving source or distributed atomicity proof |
| First-run failure | FAILED with null success/watermark; retry correctly reports full scan | No fabricated incremental checkpoint |
| Backup and separate restore | Real SQLite backup API,0600 archives, separate new destinations; all fixture-table logical row counts/hashes roundtrip; source remains unchanged | Not pg_dump/pg_restore, cluster/global roles, helper ownership/ACL or active database acceptance |
| Restore refusal | Existing destination retained; corrupt digest refused before destination creation | No active restore attempted |
| Error during failure journaling | Original exception propagates, no raw exception/source text logged | Unavailable target cannot persist its FAILED marker; F-03 durable failure/ownership work remains separate |
| Deferred dependency witness | Legacy incremental scan misses a WO older than overlap when its equipment arrives later; explicit full scan recovers this static fixture without cursor reset | This known counterexample keeps F-03 OPEN; full scan is not a general recovery/coverage guarantee |

The late-dependency witness was also executed using the exact projector source from main `8bb1bcb` (1/1 pass asserting the omission). It is an **existing main limitation**, not introduced by failure journaling, and not a validation failure in the unmerged PR94–100 stack: that stack was inspected but not integrated or executed. Full reconciliation recovers this static fixture only; no general guarantee is inferred.

The full mainline suite passes; **F-03 is not closed**. It still lacks the durable
capture/debt/receipt/fencing and restricted-writer qualification in the unmerged
B1–B5 stack. Do not replace that work with a freshness timestamp or call a static
SQLite retry an operational recovery proof.

## Existing F-03 dependency stack and required decisions

Read-only GitHub recheck confirms PR94–100 OPEN/DRAFT, no merge. Exact heads:
PR94 `71d2f3802b325e1cf36563db556364444305ec7f`;
PR95 `ce6a29a29fb55a5c72612bc981e32b220768b27e`;
PR96 `86d760c7f3cf8638ef2099f4e545ec315f82916e`;
PR97 `662ce7b47c930b3ab312f3ce02223d49544b7094`;
PR98 `bee49a345a63bb6083b6dd79650569febd227ba9`;
PR99 `ef0dc37f0e294897b79a58e681c5e87c5a646d40`;
PR100 `952160cca72724e456b5a4e092301f5e475143e3`.
Their existing exact-head runs are successful, but were not rerun or integrated by
this batch. [PR100](https://github.com/johnd-creator/reliability-knowledge-starter/pull/100)
and its immutable B5 FIX report retain the historical privilege-test exception,
restricted writer compatibility and operational NO-GO. No acceptance is inferred
from that historical PASS or from tracker status.

Before F-03 closure, require the following reviewed evidence; operational writes/activation remain separately authorized:

1. Cumulative B1–B5/source-lock design, actual owner/co-location, exact migrations
   and role/helper privileges, writer exclusion/shared fencing and legacy limits.
2. Disposable PostgreSQL16 qualification of this candidate and any integrated
   recovery stack, including all role/global metadata/helper ownership/ACL, source
   concurrency and restore elsewhere. **F03 qualification not executed here**: current main does not contain that stack and this Phase1 run does not install its helpers, grant source UPDATE, or qualify global metadata restore. Isolated synthetic testing is permitted; it is not blanket-blocked by the prohibition on active security changes.
3. Complete operational backup inventory, approved RPO/RTO/capacity/retention,
   verified separate restore and reconciliation of changes since backup. No
   operational backup was read or restored by this task.
4. Poison/absent/stale claims, historical unresolved debt, least-privilege reader
   downgrade and non-destructive application rollback. Retain tables, audit,
   captures/receipts, obligations and source cursors; no down migration/reset.
5. Current Phase1 monitoring expiry/policy and AUD11/accountable operational review.
   Deferred PdM engineer validation stays deferred; it is not invented to satisfy
   these distinct gates.

Source-only local fixes have passed Phase1 PostgreSQL qualification and are ready for review. The runtime observation above describes unchanged deployed code; these fixes are not live. Minimal next tasks: publish the authorized reviewed diff as a draft and require its exact-head CI; obtain attributable expiry disposition from Fauzi; independently review/qualify the cumulative F03 stack against explicit recovery acceptance. No merge or operational activation is authorized by this document.


## Final local preservation checkpoint

Final read-only verification at2026-10-19 **13:06:16 UTC**: main remains `8bb1bcb2c485feeb792235c64b5aef6bbce5e3cc`; runtime control HEAD/branch/status and dirty-file hashes unchanged;35 container identities/states/ports unchanged; original runtime PIDs/listeners and serving tracked bytes unchanged; controller manifest files still match PR103. Preview remains PR104 with its existing generated next-env.d.ts modification. Background collection may advance naturally; this is not a frozen database-byte claim. No user session or active database backup was read. Final evidence confirms both owned test clusters and failed-start remnants removed; original35 containers unchanged. Workspace-only dependency symlink was removed after render verification.

Local candidate verdict: **READY FOR REVIEW / CONDITIONAL qualification**. Documentation reconciliation and isolated software fixes are prepared; F-03 remains **OPEN / NO-GO**. At the initial review checkpoint this batch had created no commit/push/PR. Subsequent authorization permits draft publication and CI only; no merge, deploy, runtime or Linear update. Phase1 PostgreSQL fixtures are tested; F03 role/helper/global-metadata restore, operational policy disposition and active runtime tasks remain unexecuted and require the separately scoped decisions above. No automatic approval rejection occurred in this batch.


## Publication authorization and CI runner follow-up

The user explicitly approved commit/push of this batch, draft PR to main, and CI through terminal status. No merge/auto-merge/deploy/runtime activation is included. Prepublication review reproduced the standard CI/file-rehearsal incompatibility and separated the suites without changing `run_offline.py`. The new private-file guard requires exact six test IDs, reports caught forbidden I/O as FAIL, rejects SQLite ATTACH and removes its owned temporary root. Workflow tools retain `github.workflow_sha` provenance; dispatch from older main cannot substitute for the candidate PR workflow. Independent high source follow-up found and closed URI/PathLike semantic and NUL validation gaps; final source follow-up found no remaining blocker. Reviewer executed no tests/services. Actual test execution and final SHA/checks are reported separately at PR handoff. F03 remains OPEN/NO-GO and PdM engineer validation deferred.
