# NADI-PDM-HISTORY-COMPLETE-01 — local source-history candidate

Checkpoint: 21 October 2026; authorized receipt correction: 22 October 2026. Base main `e84eaec0e38e57cf0f057abaeda04e34739b01f8`
(PR110). Local branch `codex/pdm-complete-history-local-01`; not committed,
published, merged or activated. Tests below use disposable databases only.

## Requirement and implemented boundary

Preserve the seven supplied workbooks as navigable historical source content,
including ambiguous content, without manufacturing asset mappings, measurement
units, dates, formula results, diagnoses, SRs, approvals or canonical evidence.
This is a read-only addition inside **Pusat PdM → Riwayat & Tren → Riwayat Sumber
Excel**. It does not add a historical chart or change the existing canonical plot.

The missing Boiler source sheet profile (index15, `wb-vib-boiler-s016-b01`)
retains five source-axis claims and265 populated value cells. Its missing unit
and unqualified date encoding remain unresolved; the source label is unmapped.
All other populated cells outside catalog measurement regions remain visible as
RAW/context rows, rather than being discarded or misclassified as measurements.

## Exact source reconciliation

A populated physical cell means a stored non-null value **or** a formula,
including a formula without a cached result. Formatting-only/blank cells do not
become measurements. Source coordinates, value types, null versus zero, original
clock claims, formats, formula XML/BIFF tokens and cache status are retained.
No macro, formula, external link or recalculation is executed.

| Workbook reference | Sheets | Populated cells | Navigable source groups |
|---|---:|---:|---:|
| WB-FAN | 10 | 16,385 | 2,072 |
| WB-MILL | 8 | 9,020 | 1,788 |
| WB-6KV | 5 | 6,782 | 1,132 |
| WB-CEP | 4 | 4,554 | 325 |
| WB-VIB-BC | 32 | 36,299 | 3,178 |
| WB-VIB-BOILER | 69 | 55,728 | 9,606 |
| WB-VIB-TURBINE | 72 | 44,379 | 7,177 |
| **Total** | **200** | **173,147** | **25,278** |

Every 173,147 physical populated cell is reachable through a source-group field;
zero populated source cells are omitted. Exclusive physical categories:
130,429 INPUT; 4,611 REFERENCE; 1,981 SOURCE_ASSESSMENT; 14,078 CONTEXT;
22,048 UNCLASSIFIED. These are source claims, not engineering qualification.

Groups: 11,862 measurement-source occurrences; 10 source-context occurrences;
13,406 RAW rows. This is **not 25,278 new inspections**. Classification:
20 SOURCE_READY (readable, still provisional), 25,258 RAW_UNRESOLVED. No optional
ambiguous date conversion rules are assumed by this exact plan. Empty 5,766
profile positions are excluded with counts; their blanks are not replaced by0.
There are 50 overlapping physical value claims: the cell is stored once, both
claims remain accessible and the occurrence remains RAW.3,404 formula cells have
stored results; 1 has no stored result. Neither is recalculated.

Private plan: `e87f84abf7a32a223ff5c3568cd41b1748ac8f05c55f4524b393e46688f17b88`.
Its manifest reconciles every workbook/sheet and authenticates all four streams,
source fingerprints, catalog hash and parser implementation hash. Private source
files, data streams, original equipment labels, recovery payloads and evidence
exports are excluded from the patch.

## Storage, authority, import and recovery

Migration 007 adds seven compact source/proof/profile/event/alias/batch/receipt
tables **inside the existing owning application store**. No new operational
application DB, startup DDL, writer API or canonical-table write is introduced.
Cells are stored once per source fingerprint/sheet/coordinate; source occurrence
identity excludes the importing custodian, preventing duplicate custody imports.
Only the batch cursor/state is mutable; proof, aliases and receipts are append-only.

GET routes use the existing trusted session authority and current asset scope.
Full RAW content is restricted to its AUTHOR owner and authorized asset.
ADMIN/REVIEWER are not implicitly granted the full workbook. Proof lookup follows
an authorized occurrence; hidden owners do not leak counts/proofs. Source aliases
validate immutable revision fingerprints and independently check current record
visibility. Seven partial samples and25 later samples link to existing revisions;
human documents/revisions are never overwritten or duplicated.

The new importer is **qualification-only**: PostgreSQL loopback, explicit
`pdm_history_complete_*_test` database, non-managed port and no DSN overrides.
The demo target on15443 is refused before connection. The existing25-event pilot
and original document-store guards remain unchanged. Its separate source-store
budget is240,000 rows/96 MiB JSON, 128KiB per item; transactions are bounded to
1 source/profile, 500 cells or25 occurrences. This is not a lifted human-record cap.

Before writes, all authenticated plan streams are copied into anonymous read-only
descriptors, eliminating stream-path replacement races. Source bytes and exact
plan ID are bound; changed files/parser/interpretation fail closed. Advisory import
serialization, per-chunk current grant guards, immutable fingerprints/receipts and
atomic cursor advancement support lost acknowledgements and safe replay.
Receipt V2 fingerprints the exact bounded commit-time alias rows (including source
occurrence, existing record/revision, capture hash and relation). Replay requires
both stream facts and these alias rows to exist unchanged. Missing/changed aliases
fail closed; they are not rebuilt from current or later human revisions. Legacy
receipts without this evidence are refused. No live receipt conversion is needed:
migration007/source-history tables have never been activated on the demo target.
Numeric zero/one and Boolean false/true remain distinct. Genuine absent physical blanks
can match old captured nulls; they never match zero.

A fresh private recovery preimage is required (maximum 15 minutes), bound to the
actual target identity, schema/PK/FK/OIDs, migration checksums and business rows.
It covers **seven new tables plus six existing business document tables**;
it excludes accounts/password hashes, sessions, attachments and factual stores.
Current business changes require a fresh snapshot. There is no automatic purge,
restore or overwrite of later user work. Recovery qualification rehydrates into an
independent empty migrated DB; any future live recovery needs an explicit target,
conflict/dependency check and separately authorized operator action.

## UI and tests

The view provides authorized workbook/sheet/kind/status filters, keyset paging,
per-sheet reconciliation, original source-cell evidence, bounded field pages,
formula/cache metadata and immutable sample links. Indonesian dates preserve
source precision; RAW dates remain explicit with original claims accessible.
List/batch/detail responses stay below the unchanged browser cap through byte
pagination; shared long evidence cannot trap the UI on an unreadable page.
Desktop/mobile proof content wraps without expanding the whole page.

Verified locally:

- Full seven-source PostgreSQL16 qualification: all 173,147 cell proofs and25,278
  occurrence documents compared with authenticated streams; every group reached
  through keyset reads; seven workbook samples plus missing-profile detail read.
- Lost ACK after commit resumes; completed replay inserts nothing; 32 existing
  immutable sample aliases (7 partial/25 complete); all 35 inspections/46 revisions/
  46 receipts/4 Cases and related business rows stay byte-equivalent in the copy.
- Seven tables total200,683 rows, 38,910,679 bytes JSON in qualification.
  Complete 13-table recovery snapshot 80,838,017 bytes; separate-empty-DB roundtrip
  preserves all row hashes. Owned temporary PostgreSQL clusters stopped afterward.
- 131 related Python tests: 112 passed, 19 skipped for explicit prior PG-fixture
  prerequisites. Separate opt-in public importer, migration/grant and local-auth tests:
  23/23 passed on dedicated empty disposable databases, including append-only rights.
- 15 mounted-component browser checks: synthetic intercepted GETs only, readable
  date-only display, zero/null, unknown units, raw conflicts, source/current revision
  distinction, variable detail cursor, keyset paging, 403/503/401, desktop1440/mobile390.
- Receipt correction controls: 30 focused tests pass; independent reviewer ran
  all 12 transaction/alias controls offline. The public PostgreSQL importer test
  loses an acknowledgement after alias commit, resumes, accepts a legitimate later
  human revision with a fresh preimage, and retains source revision 1/current 2.
  The full-source recovered copy rejects missing/changed aliases without repair;
  fixture fault rollbacks leave the correct restored rows and business data intact.
- TypeScript, focused ESLint and production build passed; final scoped regression
  and independent frozen-patch review are recorded separately before delivery.

Automated component screenshots are not an authenticated live UI/UAT session.
No login credentials were entered; no TLS warning was bypassed. The active runtime
and data have not been migrated or replaced by this candidate.

## Trending and next acceptance

PR110's current measurement plot reads canonical `measurements[]`; provisional
workbook captures do not populate that contract. It is not a multi-date Excel trend.
One verified source-field viscosity series has9 literal numeric observations with
consistent reported `Cst` and explicit source dates, suitable for a separately
labelled provisional source scatter. Physical point/instrument/procedure equivalence
is unverified. Never combine different workbook assets through the shared QA asset.
No chart subsystem, diagnosis or canonical trend is implemented in this package.

The next proposed package is publication/review/exact-head CI, followed by separate
approval for migration 007/controller compatibility and managed activation. A
reviewed full-history **demo-target adapter**, fresh current-state reconciliation,
13-table backup/empty-copy recovery and bounded readback are still prerequisites
before any live/demo import. The old25-event adapter does not authorize this plan.
No live schema, access/grant, runtime, source collector, cloud export/upload or
external deployment action is covered by the present implementation stage.
