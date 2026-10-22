# Complete historical demo path — local preparation, not activation approval

22 October 2026. PR111 reviewed head `5123b9b042f7bf9ea26f68149f200a0c199d6496`
merged as `85e6bb61eb5cb724e436846b9bdeee31709dffd4`, with identical source tree.
This adapter/proposal is a separate unpublished worktree, based on the reviewed
head. It is not part of PR111 and has not been applied to the demo.

## Verified target and source scope

Read-only inventory verified `127.0.0.1:15443 / nadi_local_dev_01_test`, application
role `nadi_local_dev_01`, with migrations002–006 intact and007 PENDING. Existing
business counts:35 inspections/46 revisions/46 receipts/4 Cases/12 Case events/
12 Case receipts. No live migration, import, privilege change or runtime change.

The adapter pins exact plan
`e87f84abf7a32a223ff5c3568cd41b1748ac8f05c55f4524b393e46688f17b88`:
7 workbooks/200 sheets/173,147 populated physical cell proofs/25,278 source groups.
It verifies actual workbook hashes and parser/stream identities before writes.
Boiler/Turbine differ from the older catalog fingerprint: the approved plan binds
the actual supplied bytes and all their groups must remain RAW_UNRESOLVED. These
mismatches are explicit; no hash equivalence, source identity or date/unit is guessed.

Default qualification importer guards remain unchanged. The separate adapter has
an exact demo profile and a disjoint disposable test profile; arbitrary database,
role, port or DSN-query overrides fail before connection. It requires the reviewed
column/PK/FK schema and an existing non-owner, non-super import role with exactly
SELECT+INSERT on the seven history tables, plus UPDATE only on history_batch.
It performs no DDL, credential provisioning, GRANT or automatic recovery.

Default calls are read-only. Explicit apply requires the current exact preflight
ID, a separate approval reference and1–250 new chunks per invocation. Preflight
binds target/database identity, exact manifest/sources, migration checksums,
backup, existing business/history/grants, author grant-version and implementation
hashes. They are rechecked before the first write; actor grant-version is checked
per chunk. Chunks remain1 source/profile,500 cells or25 groups, within existing
240,000-row/96MiB source-store bounds. No human-record guard is increased.

## Isolated qualification

Full public adapter qualification used a normal restricted SQL role in two new
owned disposable PostgreSQL databases, never the demo target. Read-only preflight
made zero history writes; invalid approval/preflight/chunk bounds were refused.
Lost-response resume completed in8 apply calls, each at most250 new chunks.
All173,147 proofs/25,278 groups read back exactly;32 old samples were linked
(7 partial/25 complete), not duplicated. Completed replay inserts nothing.

A13-table snapshot roundtrip into an empty second database preserved all row
hashes and old business data. Missing/changed restored aliases were rejected
without repair. A stale preflight after lost acknowledgement was refused with
zero further writes. A legitimate later human revision created through the normal
application path remained intact; the adapter then refused the changed baseline
with DEMO_BASELINE_RECONCILIATION_REQUIRED, even with a fresh backup. Prior core
tests also preserve the immutable source revision alias across later revisions.
Qualification completed in382.6 seconds;34 focused controls and23 native
core/migration/authentication tests passed. Independent review must bind the
final adapter bytes before declaring local preparation GO.

Migration007 was separately tested on a disposable pre-007 copy already holding
35/46/46/4 business records. Failure before ledger receipt rolled back all new DDL;
successful additive007 preserved every old business row. The old PR110 migrator
then rejected007, confirming the rollback blocker rather than assuming compatibility.
Owned temporary clusters are stopped after tests; snapshots are private local
qualification evidence, not a transferable/cloud database package.

## Hard launcher/rollback prerequisites

The installed controller release `pr110-local-compat-a77da62b21ac` approves only
`891dfee8 → e84eaec0`. Candidate changes three pinned fixture-contract paths:
application-migrations, repositories, and Engineering QA API. Its exact source
transition requires a separately reviewed, hash-bound compatibility approval.
No global bypass, fixture reset or dependency/security relaxation is acceptable.

Candidate startup requires007 APPLIED. Unchanged PR110 rejects an007 ledger as
UNKNOWN_APPLICATION_MIGRATION, and launcher recovery requires old/new schema and
serialization probes to agree. Therefore neither switching first nor a direct
source-only rollback to exact e84 is a valid migration plan. Restoring an old dump
would destroy later changes and is not an automatic rollback substitute.

The controller-owned bridge is now implemented locally in
`local-controller-history-111/pdm_007_bridge.py`. PR110 application bytes remain
exactly e84; no MIGRATIONS monkeypatch or filtered ledger is used. The bridge
exposes all002–007 states and recognizes only the exact reviewed PG16 catalog
(SHA256 `7dc4b17be2b6281887fcd02fe2042794d8a5f1d67bf05cdad3856d54c8f56411`).
It pins both source SHAs and the ten fixture-contract Git objects, checks dirty
and untracked files in that scope, and rejects unknown ledger entries, partial
schema, wrong checksum, column/default/PK/FK/index/trigger/rule/RLS drift.

PR110 startup accepts only007 wholly absent/PENDING or exactly APPLIED. PR111
startup and forward compatibility require APPLIED. Dispatch binds the source
actually imported through PYTHONPATH; a candidate compatibility probe using the
old configuration cannot inherit PR110's pending-schema exception. Startup also
rejects an imported-source/config mismatch. All unrelated source paths retain
the original migrator and launcher behavior.

The task-local five-file controller release hashes the bridge as well as the
existing four modules. Its amendment explicitly binds e84 →85 and the exact007
schema hash; missing bridge, changed files, unknown source and stale/tampered
receipts fail closed. The original recovery equality guard remains unchanged.
A prepared installer defaults to a read-only report; it requires exact reviewed
files, installer hash, current wrapper/manifest/active-state hashes and a separate
execution acknowledgement. No installer apply was executed in this task.

Native isolated tests qualified pre/post007 startup and login, candidate refusal
before007 (including a compatibility probe retaining the old configuration),
atomic migration failure, twelve schema rejections, full173,147-cell/25,278-group
history readback after source rollback and preservation of a legitimate later
revision. Existing validate_recovery/_recover ran against real old/new probes;
process ownership/start/stop and backup boundaries were test doubles. This does
not claim a live systemd/TLS cutover or user UAT. The temporary cluster stopped.

## Exact future bundled execution proposal — separate permission required

1. Recheck main85, candidate/adapter/controller hashes, independent review,
   required CI, activee84, schema and business/grant state. Report any drift.
   Publication of this additional adapter/controller package remains held until
   the final local scope/review is reported and the next action is authorized.
2. Take and verify a fresh private full application backup through the existing
   managed owner path. Keep it local and owner-only. It includes auth/session
   content and must not be exported. Preserve all collector services/data.
3. Install only the reviewed five-file controller amendment atomically; retain
   wrapper/manifest preimages. Then use the existing managed source-selection
   path to select a clean managed copy of the SAME PR110 e84 source before DDL.
   This explicitly starts FE/API units with the new controller-owned bootstrap
   while preserving the old source/files. It is not a new application commit,
   forced checkout, active-metadata rewrite or global acceptance bypass.
4. Revalidate backup and allowlisted `127.0.0.1:15443/nadi_local_dev_01_test`.
   With existing owner `nadi_dev_fixture`, permit only007 pending and002–006
   intact. Apply only `007_pdm_source_history.sql`, SHA256
   `95806119fe0a131ec8c64733da9f41de85e59389cae3ee80820876f27abad524`,
   in one transaction through the existing application migration owner boundary.
   No startup DDL, empty-fixture prepare(), reset or blanket migration/grant_writer().
5. Separately authorize privileges ONLY on these seven new public tables for
   existing SQL role `nadi_local_dev_01`: `nadi_history_source`,
   `nadi_history_profile`, `nadi_history_cell`, `nadi_history_event`,
   `nadi_history_alias`, `nadi_history_batch`, `nadi_history_receipt`.
   Require SELECT+INSERT on all seven and UPDATE only on nadi_history_batch.
   No proof UPDATE/DELETE/TRUNCATE/REFERENCES/TRIGGER or ownership. No account
   role, asset grant, password, credential or old-table permission change.
6. Verify PR110 remains healthy through the new bridge after007, with unchanged
   old records/grants. Take a fresh managed post007 backup. Prepare and verify
   the private exact e84 →85 compatibility receipt: identical complete ledger,
   schema and typed current-record serialization; target/container/config/
   accounts/dependency/controller bindings unchanged.
7. Managed-select exact85 with FE/BE parity, TLS, login/access and health checks.
   Keep a valid source rollback to e84 under the NEW bridge controller. Never
   bypass certificates or infer authenticated acceptance from anonymous401.
   User login and visual UAT remain user handoffs.
8. Take and verify the fresh13-table source-import preimage (maximum15 minutes
   old): seven history plus six business tables, excluding auth/sessions/private
   attachments/factual stores. Reconcile any later business edits instead of
   overwriting them; do not renew snapshots around unexplained drift.
9. Approve the exact plan, seven source fingerprints, current AUTHOR/asset grant,
   target and preflight. Import at most250 new chunks per apply (qualification
   needed8 calls/1,792 chunks), preserving immutable receipts and committed
   prefixes on interruption. Refresh/reconcile a stale snapshot before resume.
   Required aliases cannot be rebuilt or silently repaired. Existing7 partial
   and25 complete samples remain links, not duplicates or overwritten revisions.
10. Read back all173,147 source proofs/25,278 groups, source provenance, aliases
    and coverage; replay must insert zero duplicates. Preserve old35 inspections,
    46 revisions/receipts,4 Cases (or explicitly reconciled later legitimate
    state), accounts/grants and collector data. Show the source history under
    Pusat PdM → Riwayat & Tren → Riwayat Sumber Excel. This is provisional source
    navigation, not25,278 inspections, canonical asset trends or new charts.

## Recovery boundaries and permission wording

Before007, failed controller metadata installation restores only its exact known
wrapper/manifest preimages, never concurrent unknown bytes. Source selection
uses the existing managed one-attempt failure recovery. After007, retain the NEW
bridge controller even when rolling application source back to exacte84; the old
four-file controller cannot recognize007 and must not be restored automatically.

Source rollback retains007, all imported source/history rows and later human
edits; PR110's older UI/API naturally does not expose the new source-history view.
No database downgrade, dropping007, deleting source groups, or restoring an old
pre-migration dump over later work is authorized. A destructive restore requires
new action-specific permission and reconciliation. The13-table import snapshot
is deliberately narrower than a full application backup.

Proposed request for the user: authorize this exact local-demo bundle after final
review/publication gates: install the pinned controller bridge, managed-reselect
PR110e84 to bind its bootstrap, apply only007 in nadi_local_dev_01_test, add only
the named seven-table SQL privileges, activate exact85 on https://localhost:3000,
then import the pinned seven-workbook provisional source plan in bounded calls
with fresh backups and verified readback. Risks are brief FE/API interruption,
additive schema/SQL privilege changes, extra local storage and loss of the old
controller as a post007 fallback. Recovery is source-only e84 under the new bridge;
no automatic destructive restore. Exclude cloud export/upload, collector changes,
operational asset mapping, user-role/grant changes and new trend/diagnostic work.

All steps above remain UNEXECUTED on the live demo in this preparation task.


## Supporting package publication boundary

The reviewed five controller files are packaged separately under
`deploy/development/pdm_history_111/controller/`; the generic launcher is unchanged.
The packaged installer accepts an explicit owner-private approval file and checks
its own new executable hash. No approval/config/baseline or source data is published.
The supporting package commit is not an accepted runtime application target:
compatibility stays exact PR110e84 →PR11185 with the same007 checksum/schema digest.
A different runtime target requires a newly reviewed compatibility set.
