# NADI-PDM-HISTORY-STAGING-01 — local candidate, 21 October 2026

Base: merged PR109 `891dfee8a6606cbab64553a829863518f89e2cac`.
Implemented locally and qualified in isolation; not committed, published, deployed
or an authorization to import more data into the active demo. No method, threshold,
canonical identity, data-retention policy or operational acceptance is inferred.

## Factual access message

Executive Overview now preserves the distinction between HTTP403 insufficient
capability/scope, HTTP401 expired session, and unavailable upstream/network/500/503.
Messages are static and do not expose backend bodies. The factual policy, pinned
operator portfolio capability, AUTHOR/REVIEWER roles and Registry checks are unchanged.
The active `local-engineer` can work on owned PdM drafts; the pinned `local-operator`
has factual portfolio READ but no implicit AUTHOR or access to other authors' drafts.

## Staging and storage boundary

Install the optional `history` extra in an isolated environment, or use `test`
for qualification. `scripts/pdm_history_plan.py` only reads local XLS/XLSX files;
it cannot connect to a database. It writes a new private0700 directory containing
`events.jsonl` and a content-addressed `manifest.json`, both0600. Source workbooks
are unchanged. No operational DB, application schema, migration, collector client,
browser upload, external link evaluation or macro execution is introduced.

The source specification is a private JSON array of `path` and existing catalog
`source_ref` pairs. Run from `reliability-cockpit`, for example:

```sh
python scripts/pdm_history_plan.py --sources PRIVATE/sources.json \
  --catalog web/lib/pdm-capture-catalog.ts --existing PRIVATE/existing-events.json \
  --out PRIVATE/new-plan --as-of 2026-10-21
```

`--existing` carries exact source event keys, record IDs and captured cell/value/unit
metadata from an authorized owning-store inventory; no credentials belong there.
A key hashes source bytes, sheet index, profile, row/column axis and position. It
does not depend on the selected field subset or batch label. The seven existing
partial samples are identified before expansion and remain `EXISTING_PARTIAL`;
they are not updated or cloned into wider rows. Conflicting source values are held.
Single-cell partials require a proven axis from the exact catalog/source range.

Each staged event retains raw scalar/null/zero, original serial, source date precision,
cell, header/unit evidence, formula/cache status, source hash, profile and exclusions.
Formula bodies are never executed. Shared/array result regions are marked as formula
cache as well. REFERENCE and SOURCE_ASSESSMENT cells remain in the offline exclusion
evidence rather than becoming diagnostic readings. The planner reports ACCEPTED,
REJECTED, UNRESOLVED and existing events, with overlapping reason counts and per-file
coverage. Empty source positions are rejected rather than becoming zero readings.

Acceptance is deliberately conservative: exact source hash (or explicitly reviewed
hash supplied to the library), matching headers and units for populated input fields,
one source date with known precision, no unresolved formula result and domain schema
bounds. Future dates, conflicting dates, unknown units, source errors and changed
hashes are held. Native dates/ISO dates do not acquire a timezone. Numeric YYYYMMDD
needs an explicit source-hash/sheet/profile/axis/locator/encoding/rationale date rule;
it never becomes `inspected_at` or `measured_at`. Six-kV block equipment/date offsets
remain unresolved by default. Boiler/Turbine byte changes need source review even
where selected headers match. ACCEPTED means provisional transcription eligibility,
not approved technical semantics or an operational asset mapping.

The detailed temporary JSONL proof is intentionally verbose (about205MiB for this
seven-file inventory). It is not a production archive or a new application store.
A full-history product needs an owning import-ledger/uniqueness/retention/recovery
decision and likely compact source/profile references; that architecture is deferred.
Do not raise or disable the existing10000-document/128MiB recovery probe limits.

## Bounded pilot and recovery

`HistoryPilot` is a library adapter **for disposable PostgreSQL copies only**:
database names `pdm_history_pilot_*_test`, explicit loopback test ports (not15443
or5432), and an already prepared owning ApplicationStore. It has no live/demo CLI
switch. A separate reviewed demo adapter/activation decision is required before
writing `nadi_local_dev_01_test`; this candidate cannot accidentally target it.

At most25 new records are written per run. Current trusted-provider AUTHOR and asset
scope are checked and the provider guard is held through the commit. All imports use
the existing InspectionService CREATE, CAS repository, revision and receipt path.
There is no raw-SQL insertion, approval, Case linkage, fabricated SR, grant change or
session generation. DRAFT/provisional/DEMO-HISTORIS is mandatory; original historical
performer is unknown and the application author is explicitly the demo entry custodian.

Whole chunks are transactional. A stricter9500-document/120MiB budget is checked
before and after writing, so a post-write overrun rolls back the complete chunk.
Owning-store duplicate checks also protect existing partials when a supplied index
is absent. Another author's hidden record is not returned by duplicate detection.
Stable event request IDs/receipts are authoritative; a private atomic journal is only
a resumable cursor. A lost ACK after commit is recovered from receipts, without
creating another revision. A changed payload for an existing receipt is held.

Qualification uses an owned disposable PostgreSQL16 cluster, restored from a private
read-only snapshot of the demo or initialized with test-only accounts. Tests cover
CREATE/audit/readback, replay, lost ACK before journal, admin/revoked-author denial,
existing partial refusal, target exclusion, tampered plan and pre/post-write budgets.
The owned cluster is stopped after testing; it does not share active demo storage.

Before a future demo pilot: approve an exact plan ID and at most25 listed source
events, qualify a target-bound demo adapter, take and verify a fresh private backup,
recheck the seven existing records/grants/runtime, and verify every CREATE/readback
and history after the chunk. Do not overwrite existing records or perform an automatic
full-DB restore. After any later user writes, recovery is reconciliation through owning
application revisions or a separately approved selective recovery. There is no normal
product delete/undelete promise. Full historical expansion remains a separate decision.

## Evidence and limits

Local evidence is retained in the task's private manifest and `review-evidence/`;
real source data and backups are excluded from Git. UI tests use the actual component
with all requests intercepted before network/TLS. They are not an authenticated
browser UAT of localhost3000. The active preview remains on PR109 until a separately
approved publication/activation. No new CI run or operational acceptance is claimed.


## Local qualification checkpoint — 08:32 UTC

Historical v1 checkpoint: self-review only at that point. The independent v2
review and corrections are recorded below; no remote CI is claimed. Focused backend qualification:
42 contracts/reader/manual-inspection tests passed without skips. Disposable-copy
qualification: 9 new pilot scenarios plus 25 existing condition fixture tests passed
(34 total, no skips). A separate exact selection of 25 real-source events (13 FAN,
12 MILL) was created/read back through the owning service in another restored copy;
all 25 CREATE histories and exact payloads matched, replay created zero duplicates,
and the preexisting ten records in that copy remained unchanged. Both owned test
clusters were stopped. No active/demo database writes were performed.

Frontend: ten existing factual-policy assertions, the new error/policy checks, and
four actual Overview browser scenarios (403,503,500,network) passed. TypeScript and
Next production build passed under Node22. ESLint passed with one existing
EngineeringWorkspace hook warning. A supplemental broader HTTP test invocation was
interrupted after hanging in the network sandbox; the bounded42-test invocation was
rerun with permitted local-server access and passed. No full backend suite claim.

Current seven-file manifest (catalog profiles, not every workbook cell):

| Workbook | ACCEPTED | Existing partial | Empty/rejected | Unresolved |
|---|---:|---:|---:|---:|
| FAN | 13 | 1 | 997 | 981 |
| MILL | 337 | 1 | 293 | 514 |
| 6 kV | 0 | 1 | 1356 | 115 |
| CEP | 0 | 1 | 15 | 181 |
| BC/EPA | 0 | 1 | 77 | 1543 |
| Boiler | 0 | 1 | 2577 | 4602 |
| Turbine | 0 | 1 | 460 | 3516 |
| Total | 350 | 7 | 5775 | 11452 |

The 350 accepted events contain1278 populated input fields; these are provisional
transcription candidates. All226 existing profiles cover199 of200 sheets. One Boiler
sheet (zero-based15) has no existing capture profile and is
not classified/importable by this pilot. No silent all-workbook coverage is claimed.
The seven partial markers represent source events, not an expansion of the existing
16 captured values. Full planID:
`caa96c25dd55a8847966c41b18fe15bf5323d6d7b5102c8b6e716f34e8f1e7fd`.
Pinned25-event selectionID:
`3d1d830396ad9d74e229873c914794f29091f5a3bc33d8d259383daf4d2babaf`.

Final read-only preservation confirms PR109 frontend/backend still AVAILABLE,
stale=false,35 container identities/states/ports and runtime unit PIDs unchanged;
ten business records,21 revisions/21 receipts, Cases and seven existing drafts are
unchanged. The three demo accounts retain their previously verified roles/scopes,
active state and grant_version1. Account/session whole-row hashes changed and session
count rose62→63 during concurrent user activity; the cause is not attributed by this
review. No credential/session security-column comparison was performed. Automated
review denied an unnecessary all-account-column comparison before execution; the
permitted narrow non-secret grant check passed. No denied operation was retried.

Next delivery is bounded: review/publish/activate this code only when authorized;
qualify a separate target-bound demo adapter before any active import. Proposed
import scope is the pinned25 events only, with a fresh verified backup and exact
allowlist/reconciliation before and after CREATE. There is no normal application
undelete, so recovery needs the verified backup plus separately reviewed selective
recovery, or full restore only while quiescent with explicit approval. Do not blindly
restore over later user edits. Cross-version event reconciliation, durable owning
import ledger, retention and recovery for full history remain architecture decisions.


## Independent review and bounded v2 correction

The original22-file patch9c2a7acb2f0acd1992e6557596a204264660d21c0378d54fcc73ce7ace3de6d7
and its checkout remain unchanged. Two independent reviewers reconstructed all22
files against base891dfee8 and returned UI GO / importer REVISE. Four P2 findings
were corrected in a separate v2 checkout:

- Every populated DATE claim is checked even when another date parses. TIME
  components remain raw and cannot become dates; formula/error clock evidence is
  held. A numeric date rule preserves other source clocks instead of dropping them.
- Unit evidence matches the entire case-sensitive expression, either plain or inside
  parentheses/brackets. No dimensional/prefix/suffix conversion or inferred alias:
  mm/s², xmm/s and mm/s-rms cannot satisfy mm/s. Formula header/unit proof is held.
- Duplicate reservation includes immutable owning inspection revisions as well as
  current documents. Editing/removing capture coordinates cannot free a source event
  for cloning; another author's document is still never returned.
- Receipt selection uses the owning exact CREATE fingerprint contract, including
  omitted optional fields. Removing work_origin is an idempotency conflict rather
  than a false replay. Ordinary retry after a later user edit preserves that edit.

Target validation is shared with qualification setup and runs before test migrations
or test-account creation. CI now supplies a dedicated disposable history database,
loopback15953 mapping and explicitly executes HistoryPilotTest. This is CI fixture
configuration only; laptop network/auth/runtime settings are unchanged.

Focused v2 qualification:30 planner/reader/capture-contract tests and37 PostgreSQL
checks (12 new pilot scenarios plus25 existing condition fixture tests), all passed
without skips. Seven-file regeneration retains350 accepted/7existing/5775empty/
11452unresolved positions; the additional checks add explicit reasons to already-held
source positions. V2 full planID:
563c234229e4fc148fbabfaffee6b5b3e79e51f81bc2be64f57e24f03f89412c.
V2 pinned25-selectionID:
2f08b1bfd102a16b9a1e0461c9083c1be8f480dff23b06c1838f6e7a83de178e.
The old IDs above are historical and must not be used for a future v2 import.

UI files are byte-identical to the qualified original patch, so its policy/browser/
types/build evidence remains applicable; no redundant UI test rerun is claimed.
Publication/activation remains unauthorized in this task. Proposed next steps are
separate: first review/publish the UI-only fix and terminal CI, then managed local
activation with existing rollback; independently review a target-bound demo importer
before any pinned25-event import with fresh backup and reconciliation. Do not widen
the disposable-copy guard to activate a demo writer.

V2 also passed37 checks on a freshly initialized disposable database matching the
CI setup, with the document-budget regression independent of copied Case counts.
The regenerated25 real-source drafts passed exact readback/CREATE histories and
replay with zero duplicates, preserving all ten copied records. All owned clusters
were stopped. Independent delta-review outcome is reported separately against the
new immutable v2 patch, without modifying the original22-file v1 artifact.


## Publication authorization checkpoint — 21 October 2026

The Product Owner authorized publishing the reviewed22-file V2 candidate as a new
branch/draftPR and running exact-headCI. Earlier local-only authorization statements
above describe their dated checkpoints. This publication includes the UI message
fix, offline planner and disposable-copy qualification writer; it includes no source
workbooks, real measurement rows, private backups or local evidence dumps. A separate
demo-target adapter is being prepared and reviewed locally; it is not part of this
candidate. Merge, activation, grants/security changes and additional demo imports
remain unauthorized. Snapshot/cloud portability is feasibility-only and deferred
until the Excel target is complete; no data export or upload is authorized here.
