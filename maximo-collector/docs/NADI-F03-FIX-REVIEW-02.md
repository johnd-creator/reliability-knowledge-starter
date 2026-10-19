# F03 safe local fixes — review 02, 19 October 2026

**Local software verdict:** the demonstrated PostgreSQL16.14 restore blocker is
fixed and qualified in the isolated candidate. Identity substitution is mitigated
by refusing unapproved case changes. Full identity reconciliation and repeat
recovery enrollment still need explicit contract decisions below. **F03 remains
operational NO-GO; FAU-11 remains In Progress.** No publication or activation.

This is the follow-up to [review01](NADI-F03-NIGHT-REVIEW-01.md). Its original
exact-PR100 RED evidence is retained. PR94–100 and their heads are unchanged;
the dependency/CI table there remains the fetched historical evidence, not new CI.
The candidate is main `35f3c101129241745e1795edd78a34c3617dccd7` plus an uncommitted
integration of PR100 `952160cca72724e456b5a4e092301f5e475143e3` and local fixes.
The only integration conflict was DEV-LOG, reconciled without losing either log.
No new commit, push, PR, merge, remote-stack edit, deploy or active access change.

## P1 restore — locally fixed with finite exact pins

Affected paths: `src/repositories/deferred_store.py`, `replay_store.py`, and
`reliability-cockpit/src/repositories/projection_coverage.py`. All existing full
catalog hash functions, fresh-install pins, function-body/type/trigger/ACL/owner
checks remain. The change admits only the independently reproduced **whole-catalog**
restore signatures, gated by server-reported `server_version_num=160014`.
No broad text normalization or dynamic acceptance of an observed DB hash occurs.
No migration is rewritten and no installer/DDL runs at application startup.

The reviewer checked the exact fresh/restored catalog differences: varchar-array
casts deparse differently after logical restore, with reviewed values, operators,
predicates, columns and uniqueness preserved. Role, ACL, owner, helper007 body,
search_path/security flags and trigger metadata also match. B4 has separate exact
ORM and SQL restored pins. Other restored PostgreSQL versions remain unqualified
and fail closed; this is not a general PostgreSQL16 restore guarantee.

Original writer RED and separate B4 SQL/ORM RED probes are retained. New independent
clusters on PostgreSQL16.14 restore globals/schema/data with owner/ACL retained.
Both SQL001→007 and ORM fixtures complete restricted replay to DONE. Their actual
separate Cockpit readers report capability VERIFIED, resolved debt and DONE queue;
targeted latest run stays PARTIAL/RECOVERY_BY_ID, without invented last-complete or
full-population proof. Real enum, partial predicate, index uniqueness/columns,
trigger body/enablement, helper ACL and owner mutations are refused. Wrong-version
tests alter only test query results after an actual SELECT160014; no server
configuration is changed. Unknown/modified hashes stay refused.

Final rehearsal also changes actual Equipment source siteid and orgid separately
after a restored claim is sealed and reserved. Restricted processing refuses both,
with no new target/receipt/resolution, no raw-input change and unchanged cursor.
After restoring only the synthetic original fields, every target table hash equals
its pre-drift value. Nine metadata/version negative-control groups cover distinct
B2 and B3 wrong-version query paths plus the reader; two additional real provenance
cases establish the post-restore refusal boundary.

The final exact commands, source hashes, negative-control outcomes, archive hashes,
and cleanup are in `review-evidence/f03-night-restore-qualification-v2.json`.
The original failing report `f03-night-restore-qualification.json` is untouched.

## P2 source identity — safe refusal implemented; semantic decision remains

Further review corrects the earlier description of a simple normalization defect:
**legacy matching is not proof of correct canonical linkage**. `canonical_id()`
strips whitespace but preserves case of the source natural key. Mapper outputs
`asset:MAXIMO:MXASSET:BSR:IP:a` and `...:A` for two distinct raw assets. Legacy WO
reconstruction uppercases its reference, so raw `a` becomes canonical reference
`...:A`. Two pure witnesses demonstrate this existing inconsistency.

The minimal mitigation in `projection_store.map_input()` acts after the approved
WO-prefix exclusion and before dependency evaluation. A reference whose case
would change becomes FAILED/INVALID_MAPPING using existing schema vocabulary.
Raw captured input and fingerprints are preserved; B1 remains PARTIAL and B2
records BLOCKED_NEEDS_REVIEW, with no canonical target write. Whitespace-only
` A ` still maps to exact `A`. No alias lookup, fuzzy match, source mutation,
helper007 change or migration/counter/epoch reset is introduced.

Six real PG regressions moved **RED:6 tests/3 failures → GREEN:6/6**. They cover
raw provenance retention, distinct `a/A` assets, uppercase whitespace, no invented
lowercase alias, a case-only source change after capture, and an old accepted
resolved fingerprint. That old corpus produces an explicit incompatibility
refusal under the mitigation; target, receipt and ledger are not rewritten and
no new COMPLETE claim appears. This is fail-closed requalification, not transparent
backward compatibility. The earlier test that accepted case-folding was explicitly
replaced with whitespace-only acceptance and new refusal regressions.

**Exact owner/source decision still needed:** preserve case-sensitive source natural
keys throughout WO relationships, or authorize an explicit scoped alias contract.
An alias option needs verified source evidence, collision handling, retained raw-ID
provenance and exact source-lock/fingerprint binding. `upper(trim(Equipment.id))`
alone would collapse distinct canonical assets and is not a safe fix. Until that
decision, Equipment `a`/WO `A` remains deferred; lowercase references are not
automatically recovered. Existing acknowledged corpus needs governed requalification.

## P2 next-generation enrollment — policy deliberately unchanged

SQL006 makes DONE/BLOCKED queue rows immutable and the primary key is lifetime
family_id. A current new OPEN obligation cannot be enrolled over that row. A new
real PG witness proves registration refusal preserves queue, stage history and
budgets and does not silently re-enroll or report successful recovery.

**Exact decision needed:** authorize a new explicit recovery episode after DONE,
then choose lifetime versus per-generation attempts/probes/history budgets,
immutable predecessor links and B4 interpretation of current debt versus completed
episodes. BLOCKED recovery needs a separate decision. A safe proposed direction is
append-only episodes after DONE with existing lifetime caps retained, but this is
not approved policy. It requires additive versioned schema/guard/reader contracts
and concurrent enrollment/fencing tests. Resetting/deleting terminal history,
raising caps or rotating an epoch to evade the refusal is not authorized here.

## Executed combined-candidate checks

All local runs use Python3.14.3 and PostgreSQL16.14. Runner `tested_sha=35f3c101...`
is the base SHA, not a new exact-head CI claim. The final content manifest captures
runtime code, tests and controllers including `projection_store.py`; no changes
are published and the original detached PR100 source is still clean.

| Combined candidate check | Actual result |
|---|---|
| B1/B2/B3 PostgreSQL |139/139 PASS, including six new identity regressions |
| B4 PostgreSQL reader |38/38 PASS |
| B5 writer/reader |18+8 PASS; legacy limited data-only restore also PASS |
| FIX01 restricted writer/reader |39+2 PASS; actual source/dependency fingerprint negatives retained |
| Real two-process claim/fence |1 PASS; one owner, stale fence refused, current owner DONE |
| Explicit next-generation policy witness |1 PASS; refusal/history preservation, not successful enrollment |
| Maximo offline |248/248 PASS, including new identity and restore-pin tests |
| Cockpit integration/coverage offline |43/43 PASS |
| Private SQLite main rehearsals |6/6 PASS |
| CI safety and cleanup |72/72 PASS |
| Additional restore gate unit tests |4 Maximo+4 Cockpit PASS; Maximo four included in248 above |
| Independent-cluster restore v2 |PASS for SQL and ORM restricted replay plus actual B4 readers |

No skipped/expected-failure tests or forbidden I/O were accepted in guarded runs.
The independent reviewer approved the design before edits and the combined diff
afterward. Original RED tests remain evidence; they are not turned into expected
failures or counted as successful functional acceptance. Cleanup remains the
independently reviewed pidfd-only fix; every owned cluster stops with verified
identity, and no raw PID/pg_ctl-stop fallback exists.

## Preservation and remaining limits

Final evidence `f03-fix-runtime-preservation.json` checks the original35 container
identities/states/ports, dirty files, main working-tree branch/HEAD, original runtime
PIDs, controller bytes, live preview SHA and tracked bytes. No fixture PG16 process
remains. No operational role/grant, data/auth/session, collector, runtime, expiry,
rollback disposition or owner/engineer acceptance is altered or invented.

No operational restore, live backup, PITR/WAL/physical restore, RPO/RTO/retention
endorsement, active legacy-writer coexistence, migration promotion or deployment
is qualified. GOV03 expiry remains 2026-10-13T00:00:00+07:00. Fresh immutable
candidate CI, the two contract decisions above, and separately authorized
operational acceptance remain prerequisites for promotion. FAU-7 Done is separate.
