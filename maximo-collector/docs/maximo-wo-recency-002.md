# MAXIMO-WO-RECENCY-002 — operational evidence

**PASS — reviewed deployment, floor reconciliation, automatic cursor, cheap
routine + scheduled worker, local Mart and factual NADI acceptance verified.**
Evidence date: 2026-10-07. This is scoped to the registered BSR/IP WO pipeline,
not complete platform/Phase 1 acceptance.

## Reviewed deployment baseline

PR #13 merged 2026-10-07 09:04:16 UTC. Main/merge/deployed Maximo source SHA:
`2eacce47f4653aceb56f01441bcfd14b50dbaeb9`; reviewed feature HEAD was
`40c68c5cb6d1e2c4e574231e4b9bb60fb9d6cf67`.

Deployment image `reliability-cockpit-platform-maximo-reviewed:2eacce47` was built
from that main tree, labelled with the SHA. Deployed recency source SHA-256
matches the main checkout: `93ab90a847a75b53ad35bf6ef04271b7849ea7fcb963300f0f61d2d896eaa16e`.
The existing runtime control checkout remains `0c800dac1da6ef863afdb193021176fe7feac073`.
Its established Compose project, DB driver/identity, volume mounts, projector and
NADI Mart connection were retained through a local ignored image/build override;
only Maximo worker/API/projector source images changed to exact merged main.
Unrelated PI/CEMS/Cockpit containers were not rebuilt/restarted. PR #12 is HOLD
and was not merged/rebased/changed/deployed. Do not run a broad plain-main Compose
up: audited main still lacks parts of the existing managed runtime wiring.

## Preserved baseline and backup

Existing project: `reliability-cockpit-platform`; existing Maximo DB owns both
Collector and Mart. Before recovery: 112,259 WOs; WO maximum and Maintenance
projection watermark `2026-08-21T03:56:54Z`; no WO cursor; zero floor markers.
Maintenance Mart rows 68,001, newest actual_start `2024-10-15T05:08:57Z`;
newest COALESCE(actual_start, source_changed_at) `2026-08-21T03:56:54Z`.
NADI API before: 845 registered assets; 7d/30d activity 0/0.
Latest legacy WO run: 2026-10-07 08:06:27–08:53:42 UTC, partial,
25,000 seen/skipped, zero upserts, one pagination error; runtime cursor absent.

Legacy worker and projector were quiesced before deployment. A private ignored
local PostgreSQL custom backup of the whole existing owning DB (WO, cursors,
runs, maintenance, other Mart state included) was saved. Size 12,986,851 bytes,
SHA-256 `e98acdf7288d85f193638e7714f08bd1c31617c640338ce552786110e7d7054f`.
pg_restore catalog validation succeeded and required tables were present; no
production restore/reset/delete or restore-drill claim. Backup contents were
not committed or exposed. Backup remains available in the local ignored
`secrets/backups/maximo-wo-recency-002` directory.

## Missing-cursor canary

Reviewed image `mxcollector sync mxwodetail`: BOOTSTRAP_REQUIRED,
0 pages, 0 business requests, 0 rows/upserts. WO count remained 112,259 and
cursor remained absent. Exit 1 is the expected incomplete operational state.

## Runtime image validation

181 hermetic Maximo tests passed on the built Python 3.12 deployment image,
with read-only test/contract fixture mounts. Initial test harness attempts
omitted contract paths and failed fixture lookups; adding the expected
repository-relative read-only contract mount resolved them. No implementation
change or production DB/source test access was involved.

## Recovery attempts

Projector stays quiescent during recovery so its watermark cannot leap past
partially acquired older tail records. Floor remains frozen at the original
August timestamp despite the rise in local maximum.

Attempt 1: page size25, page cap40, request budget60; 40 pages/GETs, 1,000 rows,
1,000 upserts, count-derived 882 inserts +118 updates, zero unchanged;
source range 2026-09-28 08:20:48 to 2026-10-07 16:08:02 +07:00.
PAGE_LIMIT; floor not reached; cursor absent before/after. No source errors,
order/scope violations or prefix skips. Duration 151.88 seconds.

Attempt 2: page size25, page cap80, request budget100; 80 pages/GETs,
2,000 rows, 1,000 upserts, count-derived 568 inserts +432 updates, 1,000 unchanged;
source range 2026-09-07 15:15:51 to 2026-10-07 16:08:02 +07:00.
PAGE_LIMIT; floor not reached; cursor absent before/after. No source errors,
order/scope violations or prefix skips. Duration 343.57 seconds.

Attempt 3: page size25, page cap160, request budget180; 108 pages/GETs,
2,700 rows, 691 upserts, count-derived 175 inserts +516 updates;
2,009 total skipped (includes unchanged and strictly older-than-floor rows).
The deployed CLI/run persistence does not expose those two skip reasons
separately; an exact unchanged counter is not claimed for this attempt.
Source range 2026-08-21 07:16:30 to 2026-10-07 16:22:46 +07:00.
RECOVERY_FLOOR_REACHED; floor reached YES. Cursor absent before,
automatically established at 2026-10-07T09:22:46Z after complete reconciliation.
Started 09:23:40.921951 UTC, finished 09:31:03.085177 UTC (442.16 seconds).
No source error/order/scope/prefix violation. The oldest timestamp is strictly
below 03:56:54 UTC on August 21; all equal-floor ties are included by the code.
Cursor is older than the successful bootstrap start, not seeded from local MAX.
One floor marker remains at 2026-08-21T03:56:54Z; it is evidence, not a cursor.

Insert/update counts use quiescent local population deltas and committed
upsert totals because generic WO upsert does not return per-row outcome;
unchanged/duplicate/older skips are reported separately where available.

## Remaining safety and semantics

Business source writes remain 0; authentication uses only the prescribed login.
No new DB/project/volume, no cursor seed/reset, no floor deletion, no canonical
rule changes. A moving source may still skip rows under offset/timestamp-only
paging without an observable order violation. MXR-004 remains PARTIAL.
NADI uses registered asset membership and COALESCE(actual_start, source_changed_at).
The existing operational schema/local projector does not retain actstart/actfinish;
new projected tail activity therefore uses source-change fallback, not a claim
about actual maintenance execution dates. No maintenance/risk scores invented.


Worker acceptance profile: existing service maximo-worker uses the reviewed
`mxcollector sync mxwodetail` every 300 seconds in a serial shell loop. Existing
non-WO source cursors are also absent, so starting the multi-group legacy command
would unnecessarily acquire unrelated historical populations during this WO
operation. Other Maximo groups remain parked pending separately bounded baseline
review; existing local stores/API remain available. This is an operational
source-load restriction, not an implementation/source access expansion. PI/CEMS
and Cockpit workers were not stopped or changed.


## Routine and scheduled worker acceptance

The bootstrap CLI's immediate routine verification consumed 1 page/GET,
25 rows, 0 upserts, NO_NEW_ROWS. A separate explicit normal sync at
09:31:37.848132–09:31:47.108473 UTC also consumed 1 page/GET, 25 rows,
0 upserts, NO_NEW_ROWS. Worker startup at 09:32:18.875123–09:32:27.341953 UTC
had the same bounded result. All had unchanged cursor 2026-10-07T09:22:46Z,
no errors and no historical traversal. The 25 skipped routine rows include
older-than-cursor boundary rows; do not label them all unchanged.

Scheduled cycle after the 300-second pause:
09:37:29.042419–09:37:35.520259 UTC; 1 page/GET, 25 rows, 0 upserts,
25 skipped, 0 errors, NO_NEW_ROWS. Cursor unchanged. API/worker/projector
remain running on reviewed main revision with zero container restarts.
Collector and Mart populations/maxima were rechecked after this cycle and
remain at the accepted values below.

## Collector after

112,259 → 113,884 WOs (+1,625); maximum source_changed_at
2026-08-21T03:56:54Z → 2026-10-07T09:22:46Z (16:22:46 WIB).
Recovery attempts made 2,691 upserts: 1,625 count-derived inserts and
1,066 updates, with no concurrent local WO writer during those attempts.
Routine cycles to this snapshot made no further upserts.
Collector API /sync/status exposes the accepted WO cursor and 113,134
scope-filtered WOs; the SQL population above includes all retained local rows.
These counts have different scopes and are not interchangeable.

## Local Mart acceptance and eligibility

First LOCAL ONLY incremental projector: COMPLETE/SUCCEEDED;
2,719 WOs read (one-day overlap from prior watermark), 2,710 written:
1,616 inserts, 1,062 updates, 32 unchanged. Nine missing-equipment skips;
zero scope/unproven-scope/mapping skips and zero null source_changed_at.
Asset projection read 1,200 unchanged local rows, no inserts/updates/source access.
Projector uses the reviewed image without source credentials.

Maintenance Mart 68,001 → 69,617 rows (+1,616).
Watermark and actual maximum source_changed_at both advanced from August 21 to
2026-10-07T09:22:46Z; newest COALESCE(actual_start, source_changed_at) agrees.
Global newest actual_start remains 2024-10-15T05:08:57Z; actual_finish is absent.
The restarted local projector's immediate repeat was idempotent:
173 seen, 172 unchanged written, 1 missing-equipment skip, 0 insert/update.

1,625 new Collector WOs versus 1,616 new canonical events is a net difference of
9. In the recovered local tail, 6 WOs lack asset identity and 3 point to an asset
absent from the local equipment population. None of those 9 can be identified
as a registered asset via its existing source asset number. No required WO
identity or mapping failures occurred. Of 1,616 new Mart events, 1,612 reference
registered assets and 4 belong outside the controlled 845-asset population.
Registered maintenance population rose 35,260 → 36,872. The canonical rules
and asset registry were not expanded to force dashboard counts.
Net population differences are not a per-WO insertion audit: projector also
updates previously existing events and replays the overlap window.

## NADI factual acceptance

API observed 2026-10-07T09:32:58.834270Z:
7-day activity 0 → 808; 30-day 0 → 1,988; 90-day 4,226;
845 registered assets, 346 active in 7d, 476 active in 30d.
SQL over the same registry/site/org/date scope and exact API as_of confirms
808/1,988. Registered latest source and factual activity timestamp are
2026-10-07T09:22:46Z. The date-desc Maintenance API shows the same newest
source timestamp with actual_start/actual_finish null.

Browser reload confirmed Overview cards 808/1,988 and latest activity
7 October 16:22 WIB. Maintenance page visibly shows 36,872 registered events
and recent records at that time. No new UI code was required.

NADI is CURRENT within its existing registered BSR/IP population: Collector
has completed recovery and cheap live reads, Mart maximum/watermark agree,
and both API and UI read the updated Mart. The 9 non-eligible source rows and
4 non-registered new canonical rows are retained/excluded according to existing
population rules; current does not claim every source WO appears in NADI.
All 1,616 newly created Mart rows have null actual_start/actual_finish.
Activity is source-change fallback and is not proof that maintenance was
executed on the displayed date.

## Operator evidence and continuation

Existing CLI/logs distinguish BOOTSTRAP_REQUIRED (0 requests), partial
PAGE_LIMIT (cursor absent), RECOVERY_FLOOR_REACHED (complete + automatic cursor),
and NO_NEW_ROWS/CURSOR_REACHED (routine complete). Collector API exposes
cursor and latest collect-run dates/errors; Mart state exposes watermark and
last_success. SOURCE STALE is assessed from those dates and the source-read
outcome, not from the UI's static projection label. No new observability
feature/SLO guarantee was added.

The runtime override is local, ignored and intentionally not committed:
secrets/maximo-wo-recency-002.runtime.yaml. Operator Compose commands must keep
existing .env.platform, project reliability-cockpit-platform and all three
files: compose.yaml, compose.dev.yaml, that runtime override. It pins the
Maximo image/build source and WO-only serial schedule; omitting it may revert
to the existing control checkout's older/default worker behavior. Reconcile
main's runtime driver/Mart/projector wiring separately before a future broad
main deployment. Existing databases and volumes remain the source of state.

Controlled WO business GET total through 09:37:35.520259 UTC: **232**:
canary 0 + recovery 40/80/108 + immediate/explicit/startup/scheduled routine
1/1/1/1. Projector business GETs 0. Pre-quiescence legacy worker activity is
outside this controlled total and was not retroactively request-metered.
Business writes 0, DB resets/deletes/truncations 0, cursor seed/reset 0,
credential exposure 0. Login uses the existing approved authentication POST.
Ongoing scheduled GETs after the evidence cutoff are not included in that total.

MXR-004 stays PARTIAL: descending timestamps + tie replay/validation cannot
prove lossless offset paging while Maximo changes. The recovery session lock
and serial WO worker do not establish a global lease across all trigger paths,
backfill and operational groups; deterministic paging and concurrency work
remain open. Phase 1 is incomplete. Future changes must preserve the frozen
floor/cursor safety; never reset state to repeat this recovery.

Next: PR #12 / NADI-PI-001 development/review may resume with WO acceptance passed,
with PR #12 still HOLD/unmerged. Resolve paging/global scheduling debt and the
parked non-WO groups in separately bounded tasks. This documentation PR must
not merge/deploy PR #12 or imply full platform readiness.
