# NADI-AUD-02B-B5-FIX-01 — Least-privilege recovery lock candidate

Date: 2026-10-16. Branch: `codex/nadi-aud02b-b5-fix01-source-lock`.
Scope: synthetic PostgreSQL qualification only. Candidate DISABLED by default.
Operational readiness: **NO-GO**. Legacy writer compatibility: **RESTRICTED**.
Astra F-03: **OPEN**. No merge, migration, source request or runtime activation.

## 1. Exact dependency chain

| Dependency | Pinned HEAD |
| --- | --- |
| main | `4914a73fc7b640b6dd0667d0450fdb12aa04c452` |
| B1 / PR #95 | `ce6a29a29fb55a5c72612bc981e32b220768b27e` |
| B2 / PR #96 | `86d760c7f3cf8638ef2099f4e545ec315f82916e` |
| B3 / PR #97 | `662ce7b47c930b3ab312f3ce02223d49544b7094` |
| B4 / PR #98 | `bee49a345a63bb6083b6dd79650569febd227ba9` |
| B5 / PR #99; FIX branch base | `ef0dc37f0e294897b79a58e681c5e87c5a646d40` |

Remote main and all five OPEN/DRAFT dependency heads were rechecked before delivery.
The new DRAFT is logically stacked on #99, targeting main to use the existing
exact-source CI qualifier. No dependency PR is rebased, edited, pushed or merged.
The final containing commit, PR URL and immutable CI links are recorded in the
delivery PR; this file cannot embed its own Git hash.

The [original B5 PARTIAL checkpoint](NADI-AUD-02B-B5-INTEGRATED-QUALIFICATION.md)
and its DEV-LOG entry remain unchanged. That historical result is not upgraded.

## 2. Reproduced B5-GRANT-01 failure

With actual non-owner credentials, source SELECT and B1 full capture work, but
direct `SELECT ... FOR SHARE` on either source table is denied. The original
B3 direct-lock recovery fails with no canonical target, false RESOLVED debt or
DONE queue entry. The identical reserved recovery succeeds with the reviewed
helper. The test records the actual server version and both outcomes.

PostgreSQL requires UPDATE privilege on at least one column for a locking SELECT
in addition to SELECT on the columns read. This is a permission boundary, not
missing fixture data. See [PostgreSQL 16 SELECT](https://www.postgresql.org/docs/16/sql-select.html).
Local evidence uses PostgreSQL 18.6 / Python 3.14.3 and is explicitly supplemental;
PostgreSQL 16 and supported Python 3.11/3.12 results must come from exact-head CI.

## 3. Evaluated locking alternatives

| Option | Decision / guarantee |
| --- | --- |
| Restricted SECURITY DEFINER lock helper | Selected candidate; effective owner has only necessary source-column privileges, application has EXECUTE without source UPDATE. |
| Direct application FOR SHARE | Rejected: incompatible with SELECT-only source privilege. |
| FOR KEY SHARE | Rejected: does not block ordinary non-key source UPDATE; also does not solve the locking permission boundary. |
| Advisory lock alone | Rejected: uncooperative legitimate source writers do not take the advisory lock. |
| Fingerprints before/after without a source lock | Rejected: writer may change source after final read and before target commit. |
| Broader isolation without enforced writer coordination | Not qualified as a substitute; no demonstrated common source/target serialization protocol. |

SHARE blocks concurrent UPDATE/DELETE of the locked rows until transaction end.
It is not a permanent freshness guarantee; later legitimate changes remain legal.
See [PostgreSQL row locks](https://www.postgresql.org/docs/16/explicit-locking.html#LOCKING-ROWS).

## 4. Selected design and rationale

`ReplayStore(..., source_lock_schema=<explicit reviewed schema>)` opts in only
after existing B1–B3 candidate flags and schema checks. Omission retains the
historical path for prior regression coverage; an actual restricted role still
cannot use that direct-lock path. A missing/drifted configured helper never
falls back. No operational CLI, scheduler, DSN or startup installation is added.

On the existing target transaction, the boundary validates the helper capability,
calls the schema-qualified typed function, locks exact WO then exact Equipment,
and re-reads the allowlisted source payload to compare its sealed fingerprint.
The existing mapper epoch, scope/manifest, B2 audit/receipt, fence and deadline
checks still govern canonical commit. An event-based test observes the same
physical backend PID and transaction object across helper and receipt writes.

## 5. Role / owner / ACL matrix

| Actor | Source tables | Candidate tables | Authority |
| --- | --- | --- | --- |
| Reviewed application projector | SELECT on approved columns; no INSERT/UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER | Existing B1–B3 required reads/writes | EXECUTE on this exact helper only; non-owner, no admin/membership, no schema CREATE or DB CREATE/TEMP |
| `nadi_capture_lock_owner` | WO SELECT(id,equipment_id), Equipment SELECT(id,sources); UPDATE(id) only on each | None added | NOLOGIN, NOINHERIT, no admin/BYPASSRLS/membership, no schema/DB ownership or CREATE/TEMP |
| Separate fixture source writer | Legitimate synthetic source SELECT/INSERT/UPDATE/DELETE | No recovery authority | Used on separate connections for contention tests |
| Separate trusted installer / source owner | Owner DDL solely inside private fixture | Installs unchanged 001–006 and additive 007 | Remains a privileged, explicitly trusted actor |
| Cockpit reader | No source mutation | Existing allowlisted SELECT-only coverage evidence | Read-only default transaction |
| PUBLIC / unrelated role | No helper capability | None added | Helper EXECUTE denied |

Runtime verifies exact helper owner column grants, rejects any application
source UPDATE (including column grants), other table-level mutations and
column INSERT/REFERENCES. Both owner and app must have no inbound/outbound role
membership. Final fixture-wide privilege checks span every source schema.

## 6. Helper function security analysis

Installed signature: `<trusted schema>.nadi_lock_source_exact(text,text,text)`
returns void. Static qualified SQL; no dynamic execution or data-modifying SQL
in the privileged function. Dynamic identifiers occur only in owner-run migration
DDL. `search_path=pg_catalog,pg_temp`, explicit PUBLIC revocation, no grant option,
EXECUTE ACL exactly owner plus reviewed app. Builtins and relations are qualified.
See [PostgreSQL SECURITY DEFINER guidance](https://www.postgresql.org/docs/16/sql-createfunction.html).

Exact IDs are bounded to 60 ASCII bytes with reviewed character classes. WO IDs
require BSR prefix; normalized Equipment dependency must exactly match the
captured ID. Equipment source scope must be site BSR / org IP. Missing,
mismatched, cross-scope and oversized input fails with a generic refusal.
No source payload is returned. Ordinary tables without RLS/forced RLS are
required; RLS-enabled stores are unsupported and rejected, not bypassed.

The runtime validates function body SHA256, exact signature/language/return,
owner, security/volatility/parallel flags, search_path and ACL. It rejects
overloads, missing EXECUTE, source ownership, role/schema privilege drift and
untrusted session schemas/temp namespaces. The installed body hash after schema
normalization is `d084e770f5b95a0770f90feb75061a67f17c21b5730e1f89b234cde450b874d0`.
The trusted DB administrator remains outside this boundary; malicious admin
DDL racing catalog checks is not defended as an unprivileged threat.

## 7. Source-mutation concurrency guarantees

All cases use private PostgreSQL and separate real connections:

| Required case | Test / expected result |
| --- | --- |
| WO changed before acquisition | `changed_source_before_lock_refused`: fingerprint refusal, no target |
| WO changed during held lock | `work_order_writer_waits_until_atomic_commit`: actual Lock wait, resumes after commit |
| Equipment changed during held lock | `equipment_writer_waits_until_atomic_commit`: actual Lock wait, resumes after commit |
| Dependency removed before lock | `dependency_deleted_before_lock_refused`: refusal |
| Dependency identity changed | `dependency_identity_changed_after_capture_refused`: exact identity refusal |
| Source write after commit | `source_update_after_commit_detected_by_next_capture`: new version OPEN/PARTIAL |
| Bounded timeout | `lock_timeout_refuses_without_target`: no false resolution |
| Opposite-order contention | `opposite_order_contention_bounded`: bounded lock refusal; no false DONE |
| Connection lost before commit | `connection_loss_before_commit_rolls_back`: rollback target/receipt |
| Reply lost after committed receipt | `lost_ack_after_commit_resumes_exact_receipt`: same receipt, no duplicate attempt |
| Fence expires while waiting | `lease_expires_while_waiting`: fenced out after lock acquisition |
| Post-lock fingerprint differs | `reread_fingerprint_after_helper_lock_refuses_tamper`: refusal |

The helper locks at most one exact WO and one exact Equipment per invocation.
WO→Equipment ordering is deterministic; an opposite-order writer can still
contend, so lock timeout/fencing provide bounded failure rather than retries.
Direct authorized SQL misuse can consume locks; application policy/DB resource
controls and trusted credential handling remain necessary.

## 8. Additive migration 007 candidate and rollback

[007 SQL](../migrations/007_restricted_source_lock_candidate.sql) SHA256:
`0d89507cd84c4a79c5fad645b5bebc3b443956cf9ede0e8421cf936f5034e5c0`.
[FIX manifest](NADI-AUD-02B-B5-FIX-01-MIGRATIONS.json) binds the unchanged
[001–006 manifest](NADI-AUD-02B-B5-MIGRATIONS.json), whose SHA256 remains
`74f9ac1c77e65346e62364c33afdbda14423d0f64ed19cf1a8c9ccac81d719fe`.

007 is deliberate transactional installation after 006; requires a precreated
reviewed owner and explicit installer `nadi.lock_projector_role`. No role is
created by this migration. Duplicate function installation, missing 006 and
incompatible roles/grants are rejected. No startup hook applies it.

Rollback planning: stop only a separately authorized candidate invocation,
disable its opt-in and leave B1/B2/B3 manifests, receipts, obligations and audits
intact. The old restricted path cannot safely resume recovery and must remain
disabled. Preserve helper/function grants until separately reviewed rollback;
do not drop source or evidence tables. A future operational backup must include
role/ACL/function definitions and evidence plus verified restore to another
store. Existing B5 synthetic selected-schema restore is not operational backup
acceptance and does not establish restore of all new helper/global role metadata.

## 9. Exact SQL / ORM catalog qualification

Both actual 001→007 SQL and independent ORM fixture variants run restricted
recovery end to end. The unchanged B4 reader accepts only the same exact reviewed
catalog fingerprints: ORM `c36d02ad2f137456ee38d247c23c0d0ad0519a676f3098359c70e96c70a40afa`,
SQL `45e77c7cc8b51de1d10d5e77d29a84607b0f5fbcbc657361e94559d65e25d6a2`.
No index/constraint checks or public coverage DTOs are relaxed for 007.
The separate helper does not alter the canonical table catalog fingerprints.

## 10. Restricted-role recovery evidence

The app creates original missing-Equipment debt, releases it, advances two
synthetic WO generations, repairs Equipment without changing the historic WO
timestamp, and selects the exact due obligation. Helper-backed RECOVERY_BY_ID
produces one canonical target and its atomic receipt, supersedes the old debt
version and resolves the exact selected version. Original PARTIAL evidence is
unchanged. A later full capture proves COMPLETE. The SELECT-only Cockpit reader
reconciles both SQL/ORM variants to outstanding=0/resolved=1/superseded=1.
Every test compares synthetic source cursor snapshots; no cursor changes.

## 11. Existing B1–B5 regression results

Required exact-head lanes, each on Python3.11 and Python3.12:

| Lane | Expected executed tests / additional evidence |
| --- | --- |
| Collector offline | 240 |
| B1/B2/B3 PostgreSQL | 133 |
| B4 Cockpit offline | 43 |
| Canonical contracts | 14 |
| B4 PostgreSQL reader | 38 |
| B5 integrated writer / reader | 18 / 8; capacity and different-DB selected-schema restore |
| Existing CI negatives | 23 + 10 + 6 |

B5's original direct-lock denial is retained; its updated synthetic recipe
then installs 007 and must complete as the restricted role without UPDATE grants.
Local B5 regression passed 18+8 plus restore of 84 tables / 143 rows.
Prior B5 report remains immutable. Full supported-version results are reported
only after CI completes; expected counts above are not a claim of execution.

## 12. New FIX-01 regression counts and execution exception

New suite: **39 restricted PostgreSQL tests + 2 Cockpit reader tests + 8 CI
negative/artifact tests = 49 distinct new tests** (each supported Python lane).
Local reviewed suite passed 39+2 on PostgreSQL18.6; CI is required for PG16.
Initial local failures involved >63-byte schema truncation, failed setup leaking
fixture connections and one CREATE OR REPLACE parameter-name mismatch. Fixes:
short hashed schema names, cleanup registered before fixture initialization and
matching declared parameter names. Failed logs/clusters are retained, stopped.

**Execution exception — overall task process status PARTIAL:** early disposable
negative tests actually granted synthetic projector UPDATE(id) on a synthetic
work_order and temporarily helper-owner membership. This violated the explicit
no-projector-UPDATE boundary even in a fixture. No operational database or
service was involved. It was disclosed to the Product Owner during execution.
Those tests were removed; they are not part of the delivered source or final CI.
Replacement tests attempt GRANT/SET ROLE as the unprivileged app and require
denial, plus actor-global source privilege zero assertions. Retained private
`/tmp/nadi-fix01-pg-hardened.*` evidence is not reclassified as compliant
acceptance. The stopped early clusters/logs remain available for audit.

Final delivered fixtures do not grant source UPDATE or helper-owner membership
to the app. Final actor-global checks require **zero** source write privilege
tables across all schemas. A technical PASS does not erase the early execution
exception; report it independently of the final candidate qualification.

## 13. Exact-head CI evidence

At report commit: **PENDING**. Delivery PR must pin containing source HEAD,
workflow SHA, run URLs and the actual executed counts/results for both versions.
Local tests from a dirty base-labelled worktree are not exact-head proof.

Required new `source_lock` lane is included in the existing fail-closed Maximo
gate; failure/skipped/cancelled/missing lane must prevent gate success. Immutable
tools checkout, exact selected source checkout and fresh PR-head recheck remain.
The runner uses private mode0700 `/tmp`, its own Unix socket, no TCP listener,
independently verified PostgreSQL system ID/datadir, exact DB/role allowlists,
credential-free environment, denied external I/O, separate component interpreters
and bounded CPU/address space/wall time. It stops only its own disposable cluster
and retains evidence. Tests must report no skips/blocked external I/O.
Engineering backend/contracts and frontend lint/type/assertions/build/browser
checks must also pass for the final source tree; merge-ref tree equivalence is
checked if that workflow uses the synthetic PR merge commit.

## 14. Remaining technical limitations

- Trusted installer/admin and trusted source schema remain assumptions; no
  RLS/partitioned-table or cross-database source-lock support is claimed.
- Supported exact IDs intentionally narrower than arbitrary vendor text;
  unreviewed IDs/scope fail closed rather than guessed normalization.
- Runtime capability checks add catalog reads per replay item; synthetic bounded
  evidence is not operational throughput qualification.
- Locks establish source consistency through target commit, not permanent
  freshness, source absence proof or unrestricted legacy-writer compatibility.
- Operational role/function metadata backup/restore and grant approval remain
  separate gates; this task never inspects the operational database.
- Codebase graph generation2026-08-24 lacks these candidate paths; direct source
  review was used after coverage reported missing freshness. No graph
  completeness claim is made.

## 15. Remaining operational blockers and preservation

Actual owner/co-location, approved grants/migration/rollback, legacy writer
exclusion, historical exceptions, absence policy, stale claims, resource/retention
limits, Phase1 expiry/acceptance, AUD11 endorsement and independent Senior Review
remain outstanding. This work does not change them. Astra F-03 remains OPEN;
legacy writer compatibility RESTRICTED; operational readiness NO-GO.

No source requests, operational/Persistent-QA database/session access, collectors,
controllers, localhost3000, freshness settings, public API/DTO/login/RBAC or 26
pending engineer decisions were changed. Before/after local preservation records
compare existing worktree HEAD/status/diff hashes and workbook/five PNG hashes.
This is filesystem preservation evidence, not a broad operational/DB audit.

## 16. Final Senior Review recommendation

Evaluate B5-GRANT-01 as FIXED_AND_VERIFIED only after the exact-head PG16 matrix
and all prior invariants pass. Technical qualification is independently PASS,
PARTIAL or BLOCKED based on actual results; overall process status remains
PARTIAL because of the disclosed early fixture exception. No unqualified claim
that source UPDATE was never granted during execution is permitted.

Recommend Senior Review of this DRAFT and the final CI evidence. Separate
technical acceptance / merge authorization is required. No operational readiness,
F-03 closure, merge or rollout is implied. **STOP after delivery.**
