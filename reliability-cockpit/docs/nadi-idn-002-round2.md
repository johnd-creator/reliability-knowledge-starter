# NADI-IDN-002A-R2 — controlled identity evidence round

**STATUS: PARTIAL. BLOCKED ON CONTROLLED HUMAN/CROSSWALK EVIDENCE.**
Three eligible hypotheses assessed; no exact equipment identifier bridge proven.
PROPOSED **0 → 0**, VERIFIED **0 → 0**. No CSV mapping dry-run/import/verify was
executed. Human verification remains PENDING; NADI-IDN-002 is not accepted.

## Baseline and preserved evidence

PR #17 MERGED **2026-10-07T14:00:31Z**. Fresh main/branch baseline
`83c529fd2d9ea5e3d3233f8d3b6025937a97054f`, branch
`codex/nadi-idn-002-crosswalk`. This candidate PR stays OPEN/UNMERGED.
Round-1 [packet](nadi-idn-002-pilot.md) and
[identifiers/audit](nadi-idn-002-pilot-evidence.json) remain byte-for-byte unchanged.
All timestamps here are UTC, 2026-10-07 unless stated otherwise.

Baseline **14:45:43.956236Z**: existing owner maximo-db/maximo_collector;
registry845, Asset Master11,845, maintenance69,617, WO113,884, all mapping status
counts0. WO cursor **14:16:12Z**, successful incremental cycle14:41:42Z:
25 rows/errors0/6.020149s; recovery-floor **2026-08-21T03:56:54Z** retained once.
Mart projection SUCCEEDED14:44:52Z. PI490 registry/433 active/433 snapshots,
history133,570; latest successful cycle14:35:59.944582Z,433/433/errors0.
PI migration004 stays applied; no migration, restart, volume or registry change.
Nine runtime container identities/images/start times are privately captured.
Runtime control checkout/accepted overrides remain those recorded by Round1.

## Local-first search and bounds

Before business source GETs, inspect exact local Collector equipment and
canonical asset_master records for the three assetnums; inspect stored vendor
identity quarantine, location, parent, ancestor, asset type, manufacturer,
plant/unit, assetid and eq5/eq9. No local specification table exists in the
19-table public catalog; collector normalization intentionally omits hrefs and
collection references. Local rows are evidence snapshots, not current source
acquisition claims. Manufacturer and eq5/eq9 semantics are not promoted into
external identity merely because values exist.

Local PI snapshots already contained the six Coal Feeder static texts below.
Known technical registry WebIds, the Round1 lineage/Element refs and direct lists
were consulted first. Static TEXT/Good values may have an epoch timestamp; their
use here is identity/configuration evidence only, not fresh process evidence.
TECHNICAL_PI_ATTRIBUTE remains distinct from GOVERNED_ASSET_SIGNAL.

Repository search covers **128 tracked text files** in maximo-knowledge,
pi-knowledge, reliability-data-contracts and the registry reconciliation note.
Exact three assetnum literals produced **0 hits** there. Reviewed authoritative
field catalog mxapiasset (verified2026-08-12), PI mapping YAML, topology artifact
and PI-001A/PI-002A investigation, plus equipment-mapping.example.yaml (VERIFY
placeholders, not a real crosswalk). File checksums are in the evidence JSON.
Historical investigation does not prove global absence or current identity.
Private environment/run exports, untracked spreadsheets and unrelated ignored
files were not interpreted as approved evidence. This is a bounded conclusion.

Remaining **16** original shortlist assets were screened locally against **50**
good TEXT identity-like PI snapshots. Exact assetnum/assetid/eq9 comparisons
produced **0 matches**; labels, unit context and partial pattern codes were not
eligible replacement keys. **0 additional candidates** selected, 0 replacement
source requests. Original20 population is retained; no new name-only pairing.

## Source reads

Round2 **PI25/30 business GETs**, all200:
3 exact Elements,3 bounded direct-attribute lists (maxCount100, no continuation),
6 identity metadata,6 corresponding current identity values,7 follow-up
configuration inspections. The follow-up explicitly inspected KKS plus the six
static attributes after Table Lookup/String Builder plugins were identified.
Source-provided Element/database relationships matched the known lineage refs.
No parent/child/template/server/database enumeration, PI Point guessing or
history call. PiClient preserved TLS, same-origin/root, no redirects, ≥2s spacing
and ≤1MiB responses. Configstrings were screened for credential markers before
persisting the quoted identity expressions. No credentials or process values
are published.

Round2 **Maximo3/10 business GETs**, all200: one exact mxapiasset query per
assetnum with `siteid="BSR" and orgid="IP" and eq11="CS01"` plus exact
assetnum equality, pageSize1. The verified identity fields plus assetspec were
selected. Each returned exactly the requested scoped Asset with inline specs;
no detail/specification/pagination follow-up was needed. Existing read-only
client, rate/1MiB limits and prescribed in-memory authentication were used.
No sync trigger, collector upsert, cursor write or business mutation occurred.

Maximo returned inline spec metadata counts **14 / 14 / 20** (A/G/Coal Feeder).
Attribute IDs are numeric and returned rows have no alnvalue/numvalue/tablevalue;
these bounded results establish no crosswalk. No dictionary meanings were
invented, values guessed or complete specification absence claimed.
Live eq9 for both Mills is `BSR26/19033`; Coal Feeder is `BSR26/19067`.
The older local eq9 values differ, so local/live provenance is kept separate.
The shared Mill value is another reason not to assume eq9 is a unique Asset key.
No existing Collector record was overwritten to reconcile these observations.

## Exact comparison and classification

Full canonical identities/AF refs and source audit are in
[Round2 evidence JSON](nadi-idn-002-round2-evidence.json), SHA256
`3b6ba85f27a366e4d9194fa39b9f5c9cf1d380d8f7b1df02b209b6c5e5ffe092`. This is investigation evidence, not an importable mapping batch.

All canonical IDs below have the observed prefix
`asset:MAXIMO:MXASSET:BSR:IP:` plus the exact source assetnum (JSON/CSV show full IDs).
AF identities remain the source-returned refs from the known lineage.

| Source assetnum | Candidate AF Element | Maximo identity field/value | AF identity field/value | Exact equipment identity | Contradiction | Classification / action |
|---|---|---|---|---|---|---|
| CS10HFC01AJ001-001 | BSR1.Pulverizer A | assetnum=CS10HFC01AJ001-001; assetid=656462 | No equipment-ID field in bounded14 direct attributes | NO | None established | INSUFFICIENT_EVIDENCE / technician crosswalk |
| CS10HFC01AJ007-001 | BSR1.Pulverizer G | assetnum=CS10HFC01AJ007-001; assetid=656468 | No equipment-ID field in bounded14 direct attributes | NO | None established | INSUFFICIENT_EVIDENCE / technician crosswalk |
| CS10HFB01AF001-001 | BSR1.Coal Feeder A | assetnum=CS10HFB01AF001-001; assetid=656454; eq11=CS01 | KKS=No Data; Kode Equipment=%AF%; Kode System=%HFB%; Unit Code=CS; Unit=CS01 | NO Asset key; YES shared unit only | No usable KKS; lookup table authority unresolved | INSUFFICIENT_EVIDENCE / controlled table record or technician evidence |
| CS10LAC02AP001-001 | BFPT1A (Round1 only) | assetnum=CS10LAC02AP001-001 | KKS=CS10BJC31GH000-001 | NO | Exact other Asset: STATION SERVICE MCC B, unregistered | REJECTED / FROZEN / DO NOT VERIFY |

Counts: confirmed0, ambiguous equipment candidate0, insufficient3, frozen
rejected1. Unit-code equality is explicitly **non-unique context**: CS01 matches
**11,153 Asset Master rows / 837 registered Assets**. No silent winner is chosen.
Names, letter suffixes, class/context and `%` pattern fragments never become
exact equipment equality. No trimming/case folding/prefix assembly/fuzzy matching
was used to convert a near-match into an identifier.

## New structured lookup configuration, not a proven bridge

Coal Feeder A direct static results (String, Good=true, timestamp epoch):

| AF attribute | Exact returned text | Plugin | Meaning for this task |
|---|---|---|---|
| Eq Name | Coal Feeder | none | generic label |
| Equipment Name | %Coal Feeder A% | String Builder | description pattern, not a key |
| Kode Equipment | %AF% | Table Lookup | pattern fragment, not full assetnum |
| Kode System | %HFB% | Table Lookup | pattern fragment, not full assetnum |
| Unit | CS01 | String Builder | shared unit context |
| Unit Code | CS | Table Lookup | partial unit code |

Exact source-returned KKS configuration:

```sql
SELECT ASSETNUM FROM [BLT ASSET] WHERE DESCRIPTION LIKE @[Equipment Name] AND EQ11 = @Unit AND ASSETNUM LIKE @[Kode Equipment] AND ASSETNUM LIKE @[Kode System] ORDER BY ASSETNUM
```

This proves an existing AF **lookup expression targeting an ASSETNUM column**.
It does **not** prove that table [BLT ASSET] is an approved current BSR/IP
Maximo crosswalk or that its result equals CS10HFB01AF001-001. Current KKS remains
bad-quality No Data locally; names/pattern selectors are not acceptable identity
by themselves. Table name/site ownership/version and row provenance are UNKNOWN.
The expression contains no explicit siteid/orgid predicate; BSR/IP ownership
cannot be assumed from its selector. No raw table was downloaded. The KKS metadata exposes no direct Table link;
Tables/paths/WebIds were not guessed or enumerated to chase the table name.

Other configured lookups reference [KKS Table] (equipment/system code by Eq Name)
and [Table Unit] (unit code from hierarchy); Equipment Name and Unit use String
Builder. Exact expressions appear in JSON. They are configuration evidence,
not separately approved business semantics or completed cross-system links.
**Actually proven new structured Asset↔AF bridges: NONE.**

## Technician review packet — three unresolved identities

[Technician review CSV](nadi-idn-002-technician-review.csv) contains **3 rows**,
exact canonical/Maximo/AF identities and the question in Indonesian. It is
explicitly **not the mapping import schema**. No mapping_status, verified_by,
credentials or process values. Decision/reviewer/date/evidence fields are blank.
Do not submit this CSV to `cockpit mapping import`.

For each pair ask:
**Apakah kedua identity ini secara resmi merepresentasikan physical equipment
yang sama?** Answer **MATCH / NOT_MATCH / UNKNOWN**, with responsible reviewer
identity, date and controlled evidence reference naming both sides.

- Mill A: Maximo CS10HFC01AJ001-001 versus AF
  `\\piaf\Indonesia Power Corporate\BSR\BSR1\Boiler System\BSR1.Pulverizer\BSR1.Pulverizer A`.
  Available: exact source record, local maintenance context, technical lineage.
  Missing: authoritative physical-equipment crosswalk or responsible review.
- Mill G: Maximo CS10HFC01AJ007-001 versus AF
  `\\piaf\Indonesia Power Corporate\BSR\BSR1\Boiler System\BSR1.Pulverizer\BSR1.Pulverizer G`.
  Same evidence limitation; A/G agreement in labels is not the missing bridge.
- Coal Feeder A: Maximo CS10HFB01AF001-001 versus AF
  `\\piaf\Indonesia Power Corporate\BSR\BSR1\Boiler System\BSR1.Coal Feeder\BSR1.Coal Feeder A`.
  Missing: [BLT ASSET] authority/scope/version and exact ASSETNUM crosswalk row,
  or a responsible physical-equipment identity review. Confirm the lookup's
  ownership; do not repair it by assigning a NADI mapping from its patterns.

BFPT is not an unresolved review row or selectable replacement. Preserve
REJECTED/FROZEN/DO NOT VERIFY. Its wrong KKS is a separate AF data-quality issue;
no AF, Maximo or NADI source correction was made.

## Governance and negative acceptance

No CONFIRMED_CANDIDATE, official mapping CSV, dry-run or import. Dry-run
rows/accepted/rejected/conflicts **N/A**, not a fictitious clean result.
All mapping counts stay0, VERIFIED unchanged, public resolution UNMAPPED/null.
No production `cockpit mapping verify` or automated verification actor.

Hermetic governed tests reject PROPOSED/UNMAPPED/AMBIGUOUS before source and
mapping tests leave ambiguity without a winner. Captured Round2 AF refs with a
synthetic canonical identity were checked separately: **9 unusable targets
rejected, 0 source requests**. Frozen BFPT excluded from all Round2 source calls.
Actual reader login nadi_mart_reader still cannot mutate mapping: zero-row UPDATE
with read-only turned off fails42501. Public mapping API is GET-only;
administrative writer credential remains separate from NADI. No production
mapping row or plausible replacement was constructed merely for testing.

## Targeted tests — no implementation changes

No code, runtime, Compose, schema or test implementation changed. No new tests
added for this evidence-only task. Existing targeted suites:

| Component/pattern | Count | Result |
|---|---:|---|
| Cockpit test_asset_af_mapping*.py | 22 | PASS |
| Cockpit test_reliability_mart.py | 41 | PASS |
| Cockpit test_api.py | 5 | PASS |
| Cockpit test_runtime_wiring.py, Compose enabled | 9 | PASS |
| PI test_governed*.py | 26 | PASS |
| PI test_runtime_wiring.py | 14 | PASS |

**117/117 targeted tests passed, zero skips.** Full PostgreSQL/Timescale suites
are preserved Round1 evidence; they were not rerun for documentation-only work.
Operational reader denial and live factual route checks complement these tests.

Exact commands, from respective component directories:

```bash
# From reliability-cockpit/
DATABASE_URL=sqlite+pysqlite:///:memory: NADI_COMPOSE_TESTS=1 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p 'test_asset_af_mapping*.py'
DATABASE_URL=sqlite+pysqlite:///:memory: /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_reliability_mart.py
/home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_api.py
NADI_COMPOSE_TESTS=1 /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_runtime_wiring.py
# From pi-collector/
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python -m unittest discover -s tests -p 'test_governed*.py'
/home/john-d/Music/reliability-knowledge-starter/pi-collector/.venv/bin/python -m unittest discover -s tests -p test_runtime_wiring.py
```

Python virtualenv paths above are actual task environments; no operational
credentials are loaded to run source tests. Markdown links, evidence whitelist,
JSON/CSV counts, Round1 preservation and `git diff --check` are validated.

## Post-investigation runtime regression

At **15:02:00.519139Z**, nine inspected operational container IDs, images and
start times match baseline. Mart populations remain registry845, assets11,845,
maintenance69,617, WO113,884, mappings0. Canonical migration state and existing
DB/volumes preserved. Services were not restarted.

| Service | Container ID | Accepted image |
|---|---|---|
| maximo-api-1 | ed047f359f0a | reliability-cockpit-platform-maximo-reviewed:2eacce47 |
| maximo-worker-1 | c048faaddb64 | reliability-cockpit-platform-maximo-reviewed:2eacce47 |
| mart-projector-1 | b4e968d59bf4 | reliability-cockpit-platform-maximo-reviewed:2eacce47 |
| cockpit-api-1 | 09c8e0b560d2 | reliability-cockpit-platform-nadi-runtime:runtime-002 |
| pi-api-1 | 415e9089e842 | reliability-cockpit-platform-pi-reviewed:3e981a3 |
| pi-worker-1 | af1c19eb1c6d | reliability-cockpit-platform-pi-reviewed:3e981a3 |
| maximo-db-1 | 81e2460cd91c | postgres:16.4-alpine |
| pi-db-1 | 08516a94ed6d | timescale/timescaledb:2.16.1-pg16 |
| cems-api-1 | f371ba970c81 | reliability-cockpit-platform-cems-api |

WO cursor advanced naturally to **14:56:55Z**; latest incremental completed
**14:57:04.176483Z**,25 rows/errors0/**6.065836s**. Recovery-floor record unchanged.
Mart projections SUCCEEDED; NADI assets/registry/decision-overview/data-trust
routes HTTP200, maturity CURRENT LOCAL PROJECTION. Latest factual summary:
845 registered, maintenance7d779 /30d1,988 /90d4,226. Rolling business windows
are not collector freshness and can change with time.

PI remains490 total/433 active/433 snapshots/history133,570; latest successful
completed cycle **14:49:15.323880Z**,433/433/errors0/**495.332906s**. Acquisition
plus configured300s pause is ~13.3min start-to-start, not a fixed5min schedule.
Migration004 checksum/applied time unchanged; no backfill or registry rewrite.
Public Asset mapping remains HTTP200/UNMAPPED/null; reader mutation denied42501.
Private metadata-only audit files are ignored under secrets/nadi-idn-002a-r2.

Safety: PI business writes0, Maximo business writes0, history0, broad AF crawl0,
source hierarchy pagination0, operational DB resets/deletes0, new operational
DBs0, cursor resets0, registry changes0, service restarts0, CEMS/NK changes0.
Authentication remained a prescribed in-memory handshake, not a business write.
No raw Maximo business export, personal values, PI process values or credentials
were persisted in the review package. Graph generation is older than main;
material current semantics were checked by direct source and executed regression.

## Roadmap / next step

NADI-PI-001 MERGED; NADI-PI-RUNTIME-001 ACCEPTED; NADI-RUNTIME-002 MERGED/ACCEPTED;
NADI-IDN-002A/R2 evidence/proposal PARTIAL, human verification PENDING.
Phase1 stays CURRENT/PARTIAL. **HUMAN CROSSWALK REQUIRED.**
A controlled MATCH with auditable evidence can support a later small PROPOSED
batch/clean dry-run. It does not itself authorize automation to promote a
production row. NADI-IDN-002B human verification/governed canary follows those
prerequisites; no production canary can start from the current empty registry.
