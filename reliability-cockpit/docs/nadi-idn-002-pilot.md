# NADI-IDN-002A — bounded real Asset ↔ AF pilot evidence

**STATUS: PARTIAL. HUMAN_REVIEW_REQUIRED: controlled identity evidence is missing.**
Evidence/proposal stage **PARTIAL**; human verification **PENDING**. Four explicit
AF lineages were verified, but **zero CONFIRMED_CANDIDATE** met the cross-system
identity rule. No production CSV, dry-run or import was fabricated to fill the
pilot. PROPOSED **0 → 0**, VERIFIED **0 → 0**. NADI-IDN-002 is not accepted.

## Baseline and runtime

PR #16 [MERGED](https://github.com/johnd-creator/reliability-knowledge-starter/pull/16)
at 2026-10-07T13:30:28Z, merge/main `a1c9270deea75d369548137a137f6eb5817c4242`; fresh branch
`codex/nadi-idn-002-pilot` starts there. Candidate PR must remain open/unmerged.
Audit timestamps below are UTC on 2026-10-07. Runtime control checkout remains
`feature/pi-governed-source-adapter` at `0c800dac1da6ef863afdb193021176fe7feac073`.
No service was restarted or redeployed for this task.

Existing Mart owner is `maximo-db / maximo_collector`, independent of the legacy
`cockpit-db / cockpit` store. At 13:40:19Z: registered assets **845**, Asset Master
**11,845**, maintenance events **69,617**, Work Orders **113,884**, mappings **0**
(all status counts zero). Canonical governance 002/003 and checksummed migration
ledger are already deployed; no DDL was needed or applied here.

NADI actual Mart login is `nadi_mart_reader`: SELECT works; no table DML grant,
no superuser/create-role/create-DB privilege, default transaction read-only on.
A zero-row UPDATE permission probe, after explicitly disabling transaction
read-only, failed **42501 / insufficient_privilege**. No mapping was changed.
Public API environment has no PI credentials or Mart administrative DSN.
Controlled administration remains separate in the private operator environment;
its bytes and DSNs are not published here.

PI existing store: **490** technical registry entries, **433 active**, **433
snapshots**, **133,570** historical rows. Latest completed snapshot at baseline:
**13:29:11.944076Z**, 433/433, errors 0, acquisition **509.851867s**. Prior
accepted first-cycle **508.142s** is historical measured evidence, unchanged.
The configured pause remains 300s; effective cycle start cadence is duration +
pause (~13.5 minutes). A collector success does not establish source freshness.
Migration **004**, applied **10:49:24.644410Z**, checksum
`b40f87fe86097bf2e1eda7c63063629903166627b1cca6c182de74c0dd3f1ffe`, remains intact.
Registry, history, worker ownership and scheduling were not modified.

## Selection and evidence rules

Read only the registered BSR/IP population and rank by factual maintenance event
count in 90 days, using `COALESCE(actual_start, source_changed_at)`. The bounded
shortlist below contains **20** assets. Labels helped choose **4** research
comparisons against locally collected technical attributes; they establish no
mapping. Canonical IDs for this list use the **observed** Mart prefix
`asset:MAXIMO:MXASSET:BSR:IP:` plus the asset number; the four full IDs are also in
the evidence JSON. Maintenance descriptions, people and raw WO payloads are not
included.

| Source assetnum (BSR/IP) | Asset label | Events 90d |
|---|---|---:|
| CS10LAC02AP001-001 | BOILER FEED PUMP TURBINE (BFPT) A | 46 |
| CS10HFC01AJ001-001 | PULVERIZER (MILL) A | 44 |
| CS10PAC01AP001-001 | CIRCULATING WATER PUMP A | 37 |
| CS10EAC01AF014-001 | TRANSFER CONVEYOR (TC) 7B | 34 |
| CS10HFC01AJ007-001 | PULVERIZER (MILL) G | 33 |
| CS10HLD01AC001-001 | AIR PREHEATER A | 33 |
| CS10HLD01AC002-001 | AIR PREHEATER B | 32 |
| CS10USD01BF001-001 | STRUCTURE & BUILDING COAL HANDLING AREA | 32 |
| CS10EAF01AE011-001 | TRACK DOZER E (CATERPILLAR D8R 03) | 29 |
| CS10HFC01AJ005-001 | PULVERIZER (MILL) E | 29 |
| CS10HNC01AN001-001 | INDUCED DRAFT FAN A | 29 |
| CS10EAC01AF013-001 | BELT CONVEYOR (BC) 51 | 28 |
| CS10EAC01AF007-001 | BELT CONVEYOR (BC) 47 | 27 |
| CS10HFB01AF001-001 | COAL FEEDER A | 27 |
| CS10HFC01AJ002-001 | PULVERIZER (MILL) B | 27 |
| CS10LAC03AP001-001 | BOILER FEED PUMP TURBINE (BFPT) B | 27 |
| CS10SGA05AE001-001 | FIRE TRUCK A (HOWO) (SAFETY) | 27 |
| CS10EAC01AF024-001 | BELT CONVEYOR (BC) 54 | 26 |
| CS10HFC01AJ003-001 | PULVERIZER (MILL) C | 26 |
| CS10SGA05AE002-001 | FIRE TRUCK B (HINO) | 26 |

Four researched comparisons: **1 REJECTED**, **3 INSUFFICIENT_EVIDENCE**, **0
AMBIGUOUS**, **0 CONFIRMED_CANDIDATE**; **16 not assessed**. Zero ambiguous here
is a bounded observation, not a claim about the entire AF database. Pilot
selection/import count **0** (target 3). This preserves the identity gate.

Allowed evidence methods remain NATIVE_IDENTIFIER, GOVERNED_LOOKUP,
MANUAL_VERIFICATION and MIGRATED_VERIFIED. No method was assigned: there is no
proven native bridge, controlled lookup, human identity verification or migrated
verified evidence for these pairs. The earlier bounded investigation in
`pi-knowledge/discovery/topology.json` is historical context, not current proof
that a native key is globally absent.

## Auditable evidence package

[Source-safe evidence JSON](nadi-idn-002-pilot-evidence.json) contains exact
canonical identities, source-returned AF Attribute/Element/Database/Server
WebIds, paths, direct attribute names, quality/timestamp/unit metadata and the
18-GET audit. SHA256: `f3b022b53d602a981bc0c43fc8806ae207286be9456ce80680232470f811436c`.
It is an investigation packet, **not an import file**. It contains no credentials,
process values, raw production exports or production verification actor.
The static KKS identifier in the rejected case is identity evidence, not a
process measurement.

Source-side chain for each packet:

```text
existing local technical Attribute WebId
  → GET Attribute metadata → returned Links.Element
  → GET that Element → returned Links.Database
  → GET that Database → returned Links.AssetServer
  → GET that Server
```

Attribute WebId equals the known registry WebId; returned relationship URLs
were constrained to the configured PI origin/root and their terminal WebIds
matched the returned resource identity. Database/server responses were reused
across candidates. AF parent paths come from returned Element metadata; the
local flattened `af_path`/equipment labels omit equipment-instance detail and
must not act as canonical identity. All four Elements are distinct direct
references, not generic system-level substitutes. This chain proves technical
lineage, **not** the missing link between Maximo Asset and AF Element.

All packets share server `piaf`, database `Indonesia Power Corporate` with exact
references in JSON. No server/database/hierarchy enumeration was performed.

### Packet 1 — BFPT A / BFPT1A: DO NOT VERIFY

NADI `asset:MAXIMO:MXASSET:BSR:IP:CS10LAC02AP001-001`, source assetnum
`CS10LAC02AP001-001`, BSR/IP, BOILER FEED PUMP TURBINE (BFPT) A, **46** events/90d.
Known technical attribute `BSR-BSR1-bsr1_bfpt-unclassified-kks-bfpt1a`
links explicitly to AF Element `BFPT1A`, path
`\\piaf\Indonesia Power Corporate\BSR\BSR1\Turbine System\BFPT\BFPT1A`.
The bounded direct listing returned **only KKS**, no continuation link.

KKS text is **CS10BJC31GH000-001**, Good=true, source timestamp
**1970-01-01T00:00:00Z**, units absent. Exact local Asset Master lookup finds
`[E] STATION SERVICE MCC B`, **not registered** in NADI. It differs from the
shortlisted BFPT asset number and equipment class. BFPT B is a separate
registered asset and cannot be silently substituted. This is a concrete
contradiction, not an approximate string comparison.

**REJECTED. DO NOT VERIFY.** Resolve this discrepancy with a responsible AF/
Maximo engineer and controlled records; do not edit PI or expand registry as a
workaround. Epoch timestamp also prevents treating this as a fresh process
signal despite Good=true and recent collection.

### Packet 2 — Pulverizer A: NEEDS MORE EVIDENCE

NADI `asset:MAXIMO:MXASSET:BSR:IP:CS10HFC01AJ001-001`, source
`CS10HFC01AJ001-001`, BSR/IP, PULVERIZER (MILL) A, **44** events/90d.
Known technical Outlet Temperature attribute links explicitly to
`BSR1.Pulverizer A`, path
`\\piaf\Indonesia Power Corporate\BSR\BSR1\Boiler System\BSR1.Pulverizer\BSR1.Pulverizer A`.
Direct listing: **14** attributes, no continuation; no KKS/asset-number/static
identity attribute among those returned. Representative snapshot: NUMERIC,
Good=true, Questionable/Substituted/Annotated=false, unit °C, source timestamp
**13:30:00.985000Z**. Measurement value is not retained in the packet.

A/G returned different Element WebIds and paths; local registry also carries
B–F technical instances. Similar letter/name/system context cannot select an
Asset counterpart. No cross-system key, controlled crosswalk or human review
record ties this AF Element to the Maximo asset. **INSUFFICIENT_EVIDENCE.**
Require controlled BSR/IP equipment identity evidence citing both exact refs.

### Packet 3 — Pulverizer G: NEEDS MORE EVIDENCE

NADI `asset:MAXIMO:MXASSET:BSR:IP:CS10HFC01AJ007-001`, source
`CS10HFC01AJ007-001`, BSR/IP, PULVERIZER (MILL) G, **33** events/90d.
Known technical Outlet Temperature attribute links explicitly to
`BSR1.Pulverizer G`, path
`\\piaf\Indonesia Power Corporate\BSR\BSR1\Boiler System\BSR1.Pulverizer\BSR1.Pulverizer G`.
Direct listing: **14** attributes, no continuation; no identity field in that
bounded listing. Snapshot: NUMERIC, Good=true, other three flags=false, °C,
source timestamp **13:38:45.689010Z**. No process value retained.

Distinct A/G AF identities avoid conflating those technical Elements, but do
not prove which canonical Asset owns G. Check a controlled diagram/equipment
crosswalk or technician identity review; apparent label agreement is only the
shortlist rationale. **INSUFFICIENT_EVIDENCE. NEEDS MORE EVIDENCE.**

### Packet 4 — Coal Feeder A: NEEDS MORE EVIDENCE

NADI `asset:MAXIMO:MXASSET:BSR:IP:CS10HFB01AF001-001`, source
`CS10HFB01AF001-001`, BSR/IP, COAL FEEDER A, **27** events/90d.
Known technical KKS attribute links explicitly to `BSR1.Coal Feeder A`, path
`\\piaf\Indonesia Power Corporate\BSR\BSR1\Boiler System\BSR1.Coal Feeder\BSR1.Coal Feeder A`.
Direct listing **10** attributes, no continuation, including Eq Name, Equipment
Name, KKS, Kode Equipment, Kode System, MPI, Unit and Unit Code. Presence of
these names is not usable identity evidence. KKS live metadata: DIGITAL_STATE,
Good=false, other flags=false, timestamp **13:38:28.228948Z**, units absent;
the result is **No Data**, not an Asset identifier. Local KKS snapshots for
Coal Feeder B–G and HP/IP turbine also have bad-quality digital state, not
usable cross-system identifiers. No extra reads of these values were needed.

No authoritative key or controlled crosswalk was obtained. **INSUFFICIENT_EVIDENCE.
NEEDS MORE EVIDENCE.** Do not infer from the A label or consume the invalid KKS.

## Source request accounting and bounds

Executed **18 PI business GETs / budget 30**, all HTTP 200:

| Operation | Count |
|---|---:|
| Known Attribute metadata `/attributes/{knownWebId}` | 4 |
| Source-linked Element metadata `/elements/{ref}` | 4 |
| Source-linked Database metadata `/assetdatabases/{ref}` | 1 |
| Source-linked Server metadata `/assetservers/{ref}` | 1 |
| Direct attributes of those Elements, `maxCount=100` | 4 |
| One source-linked current Value per known Attribute | 4 |

No continuation page followed, no child/hierarchy traversal, no history, no
business source write. Existing PiClient enforced TLS verification, origin/root,
GET-only, no redirects and ≤1 MiB body; pilot spacing **≥2s after each response**
(the collector's ≥1s floor remains unchanged). Runtime credentials stayed in
memory at the source boundary; never copied into NADI or evidence artifacts.
The background technical worker's normal requests are not pilot requests.

## Governance execution and human gate

Selected candidates **0**. Actual-Mart CSV dry-run/import/re-import and selected
candidate structural pre-canary were **NOT EXECUTED: NO ELIGIBLE ROWS**. Reported
rows/accepted/rejected/conflicts are **N/A**, not a fictitious clean dry-run.
Creating an importable CSV for the name-based hypotheses would bypass the
explicit identity rule. PROPOSED/VERIFIED/RETIRED counts remain zero.
No `cockpit mapping verify` was executed on production; no verification actor
was persisted. A real selected target can only be constructed after explicit
identity evidence clears the gate.

Isolated/operator negative checks used captured AF refs with a **synthetic**
canonical ID: PROPOSED, UNMAPPED and AMBIGUOUS were rejected before source access
for all four refs (**12 checks, 0 GETs**). Public NADI resolution for Pulverizer A
is HTTP 200 / **UNMAPPED**, pi_af=null. Operational OpenAPI exposes mapping GET
only and no mapping mutation method. Actual reader promotion is denied (42501).
Synthetic PostgreSQL lifecycle/import tests remain separate from production.

**HUMAN_REVIEW_REQUIRED.** Minimum evidence: a controlled lookup or a responsible
technician's identity review, with canonical assetnum + BSR/IP + exact AF
server/database/Element refs, authority, date and evidence reference. A label
comparison or agent judgment cannot become MANUAL_VERIFICATION. Human production
verification remains a later explicit decision even after proposals exist.

## Regression and tests

At baseline Maximo incremental WO cycles each saw **25 rows**, **0 errors**, last
three durations **8.013614 / 8.048988 / 8.885043s**. Cursor
**13:29:23Z**, latest completed cycle **13:40:00.280219Z**; recovery floor
**2026-08-21T03:56:54Z** exists exactly once. Mart Asset/maintenance projection
SUCCEEDED (13:39:30Z); populations unchanged by this task.
NADI decision overview HTTP 200 at **13:43:23Z**: registered845,
maintenance7d **791**, 30d **1,988**, 90d **4,226**. These roll with observation
time; business dates and collection success are separate.

Final metadata-only regression at **13:48:10Z**: all 9 inspected operational
container IDs/images/start times unchanged; same Mart populations/mappings,
registry845, PI490/433 and history133,570. WO cursor advanced naturally to
**13:43:02Z**; last incremental25/errors0 completed13:45:09Z in7.806865s;
recovery-floor record unchanged. PI latest success **13:42:35.032203Z**:
433/433/errors0, acquisition503.073393s; no additional pilot request was made.
Public mapping resolution remained UNMAPPED/null. These natural worker advances
are independent of pilot source timestamp checks.

One existing PI runtime test still expected an inline Mart owner DSN after
merged PR #16 switched Compose to required explicit reader substitution. Only
that assertion was corrected: required explicit DSN, example targets existing
Maximo-owned Mart using nadi_mart_reader, API has no admin DSN. No product/runtime
code or Compose service changed.

Commands below run from this branch. Test DSNs are **synthetic only**. Full
commands/fixture isolation are in the test appendix. Results:

- Cockpit `python -m unittest discover -s tests`, PostgreSQL fixture + SQLite
  legacy test DSN: **140 run, 135 pass, 5 Compose checks skipped in container**.
- Host `NADI_COMPOSE_TESTS=1 ...python -m unittest discover -s tests -p test_runtime_wiring.py`:
  **9/9 pass**, including those **5** skipped checks; **140 distinct Cockpit tests
  passed across these runs**, not 149 distinct tests.
- PI `python -m unittest discover -s tests`, Timescale fixture: **165/165 pass**,
  including **11** integration tests; no skipped tests.
- `...pi-collector/.venv/bin/python tests/compose_clean_check.py`: **PASS**, synthetic
  clean managed Compose, worker-only secrets, non-default pause, no dotenv dependency.
- Operator negative targets **12/12 rejected before source**; actual NADI reader
  zero-row promotion probe denied. `git diff --check`: PASS.

Historical first runs: hermetic Cockpit140 (121pass/19skip), PI165
(153pass/1fail/11skip). The one failure was the stale test above; fixed and full
Timescale run passed. No production request was made by any test.

## Next checkpoint

NADI-PI-001 MERGED; NADI-PI-RUNTIME-001 ACCEPTED; NADI-RUNTIME-002 **MERGED/ACCEPTED**
via PR16; NADI-IDN-002A evidence/proposal **PARTIAL**, human verification PENDING.
Phase 1 remains **CURRENT / PARTIAL**. Governance runtime is ready, but no
identity-qualified production proposal exists yet.

Prepare **NADI-IDN-002B — Human Verification & Governed PI Canary** only after
controlled identity evidence permits a clean actual-Mart dry-run and a small
PROPOSED import. Keep BFPT rejected until its contradiction is resolved. No
production governed canary is authorized by a technical lineage check alone.

Safety totals: PI business writes0, Maximo business writes0, PI history/backfill0,
broad AF crawl0, production verification0, operational DB resets/deletes0, new operational
DBs0, registry modifications0, service restarts0, CEMS/NK changes0. Temporary
network-isolated tmpfs test DBs were synthetic fixtures and removed after tests.

## Test command appendix

All networked DB tests below use private synthetic fixtures (`--network none`,
tmpfs, no published port). Test application containers share only the fixture
loopback network and mount this branch read-only. No production environment file
is used. Both fixture containers were removed afterwards.

From repository root:

```bash
docker run -d --name nadi-idn-governance-test --network none --tmpfs /var/lib/postgresql/data -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test-only -e POSTGRES_DB=nadi_governance_test postgres:16.4-alpine
docker run -d --name nadi-idn-pi-test --network none --tmpfs /var/lib/postgresql/data -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test-only -e POSTGRES_DB=pi_runtime_test timescale/timescaledb:2.16.1-pg16

docker run --rm --network container:nadi-idn-governance-test -v /home/john-d/.codex/worktrees/nadi-idn-002-pilot/reliability-knowledge-starter:/workspace:ro -w /workspace/reliability-cockpit -e DATABASE_URL=sqlite+pysqlite:///:memory: -e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test reliability-cockpit-platform-nadi-runtime:runtime-002 python -m unittest discover -s tests
# 140 run / 135 passed / 5 Compose skips

docker run --rm --network container:nadi-idn-pi-test -v /home/john-d/.codex/worktrees/nadi-idn-002-pilot/reliability-knowledge-starter:/workspace:ro -w /workspace/pi-collector -e PI_MIGRATION_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/pi_runtime_test reliability-cockpit-platform-pi-reviewed:3e981a3 python -m unittest discover -s tests
# 165/165 passed, including 11 Timescale tests

docker rm -f nadi-idn-governance-test nadi-idn-pi-test
```

From `reliability-cockpit/`:

```bash
NADI_COMPOSE_TESTS=1 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_runtime_wiring.py
# 9/9 passed, including the 5 skipped Compose checks above
```

From `pi-collector/`:

```bash
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python tests/compose_clean_check.py
# PASS: clean synthetic Compose configuration, no service deployment
```

Metadata-only private audit files are ignored in the runtime control checkout
under `secrets/nadi-idn-002a/`: baseline, live requests and final regression,
reader negative check, unusable-target check. Raw response bytes and process
values were not persisted. Graph coverage was stale relative to merged main;
material source semantics were read directly in this branch, not inferred from
the old graph generation.
