# NADI-ING-PI-001A — governed condition evidence foundation

Implementation **CURRENT / candidate**; synthetic acceptance **PASS**.
Production PI projection **NOT DEPLOYED**. NADI-IDN-002 human crosswalk remains
**BLOCKED / EXTERNAL**, human verification PENDING. Phase 1 CURRENT / PARTIAL.
BFPT stays REJECTED / FROZEN / DO NOT VERIFY; no identity investigation here.

Baseline: PR #18 MERGED at 2026-10-07T15:17:53Z, origin/main
`f8c37f068102a06906cb3ca464fe08745e0351cf`; fresh branch
`codex/nadi-ing-pi-001a`. Existing primary runtime checkout was preserved.
No collector restart, deployment, production DDL, mapping import or verification.

## Projection and trust boundary

```text
existing registered canonical BSR/IP Asset in Maximo-owned Mart
  → one VERIFIED PRIMARY_EQUIPMENT CENTRAL_PI mapping
  → separately APPROVED exact signal definitions (maximum five)
  → trusted operator plan / GovernedEvidenceSource port
  → collector-owned GovernedSourceBoundary → guarded current PI snapshots
  → validated canonical ConditionEvidence
  → atomic governance recheck → existing Reliability Mart latest evidence
  → SELECT-only NADI GET /assets/{canonical_id}/condition-evidence
  → asset overview Condition Evidence panel
```

`ConditionProjectionService` gates before the source port and the command store
rechecks the entire mapping/selection plan at commit. The concrete transport is
a private operator-file handoff, also exercised in synthetic cross-project E2E.
There is no public live PI proxy or NADI mutation endpoint. NADI never imports
PiClient, reads PI source credentials or starts collection. Source authentication
is loaded only by the PI Collector operator command. Mart administration requires
its separate `RELIABILITY_MART_ADMIN_DATABASE_URL` and explicit expected owning
database; public queries use `RELIABILITY_MART_DATABASE_URL`, never legacy
`DATABASE_URL`. No implicit store fallback exists.

The plan is a trusted local administrative artifact, not cryptographic proof or
an authorization token. Do not accept a self-declared VERIFIED request body.
Only the separately authorized local operator may pass a freshly exported Mart
plan to the collector. Public HTTP endpoints do not expose this operation.
A lifecycle/approval change during the handoff blocks projection; read views
also resolve the current mapping and exclude retired/unapproved definitions.

## Contract and explicit signal selection

New additive Draft 2020-12 contracts:

- `condition-evidence.schema.json`: bounded typed evidence, no score.
- `condition-signal-selection.schema.json`: immutable signal definition identity,
  mapping reference, semantic_name and explicit approval provenance.
- `condition-projection-plan.schema.json`: one usable mapping and 1–5 selected
  signals, all approved. Runtime validation also rejects duplicate signal IDs,
  attributes/semantic names and mismatched mapping IDs.

Core evidence fields: contract_version, canonical_asset_id, mapping_id, signal_id,
semantic_name, value, value_type, unit, source_timestamp, collected_at,
quality_good/questionable/substituted/annotated, evidence_status and provenance.
`semantic_name` expresses the selected signal role; it is not an inferred label.
Vendor identity stays in `sources.pi`: pi_source_id, AF server/database/element
refs, mapping role/status, exact attribute_ref and source-returned attribute_name.
Selection attribute references also live under `sources.pi`. Provenance records
the governed source boundary and the signal approval actor/date/evidence ref.
Mapping_id links to the preserved human identity-verification audit.

Allowed value types: NUMERIC, TEXT, DIGITAL_STATE, BOOLEAN, NULL. No string-number
coercion; no nonnumeric/null value becomes zero. Digital source Name/Value/IsSystem become vendor-neutral name/code/is_system,
preserving their exact typed values, including false and zero codes; unknown fields stay explicit null.
Unknown units and source timestamps remain null. Source snapshots lacking an
aware timestamp are rejected by the existing live boundary; a local canonical
unknown timestamp is representable and never classified fresh.
Strict models reject unrestricted raw payloads, credentials/extra fields,
nonfinite values, naive timestamps and mismatched lineage. Text is bounded to
4096 characters, metadata/refs have explicit limits; handoff inputs ≤256 KiB.

Approval is a separate local administrative act naming an exact attribute and
its meaning, reviewer, date and controlled evidence. It cannot change an Asset
mapping to VERIFIED. Definitions have stable IDs; changes require retiring an
old definition and explicitly approving a new one. Neither registry membership,
Element membership nor name similarity approves a signal. The 433 technical
registry remains untouched and is never consulted as an automatic selection list.

## Storage and deliberate migration ownership

Canonical additive Cockpit Mart migration `004_condition_evidence.sql` extends
the **existing maximo-db / maximo_collector Mart**, not legacy Cockpit DB:

| Table | Retained data |
|---|---|
| condition_signal_selection | explicit approval definition and lifecycle per signal ID |
| condition_evidence_latest | one latest evidence row per selected definition, with collected/projected timestamps |
| condition_projection_state | one latest attempt/status envelope per canonical Asset |

FKs preserve canonical Asset, mapping and signal lineage; indexes bound Asset
and mapping reads. These models belong only to MartBase, never legacy Base.
No raw history is copied. Inactive evidence remains behind governance gates;
there is no unbounded measurement time-series/history table.

Existing `cockpit mart-migrate` owns 002/003/004, with explicit owning DB/anchor
preflight, ledger checksum/prefix validation, advisory lease, transactional DDL,
validated columns/PK/FK/indexes and factual count/fingerprint preservation.
Status is non-destructive; `--apply` is deliberate. The accepted two-entry ledger
is tested to apply **only 004**, and repeat application is a no-op. Existing
002/003 SQL bytes/checksums remain unchanged. This Cockpit Mart 004 is separate
from accepted **PI Collector 004_signal_quality_fields.sql**, which is untouched.

Future reviewed deployment must back up the existing Mart, deliberately apply
only pending additive DDL and extend SELECT grants using `cockpit mart-reader
--apply`. Wrong/legacy DBs fail closed. Updated managed/external Compose retains
existing store ownership and explicit Mart reader wiring; optional NADI freshness
variables go only to Cockpit. No service or worker is enabled by this patch.
Existing managed readiness now includes the new canonical migration: do not
redeploy candidate init/projector services before deliberate deployment review.

No production DDL was applied here. The three new operational tables remain
absent, and the operational Mart ledger remains accepted 002/003. On a candidate
reader against a pending schema, condition evidence is unavailable/unknown;
existing factual routes remain independent.

## Deterministic projection and degraded behavior

Identical handoff replay writes zero evidence rows and retains original
projected_at. An older batch cannot replace newer collection evidence. Conflicting
values for the same selection/collected_at fail atomically. Projection rejects
future collected_at and rechecks registered BSR/IP membership, exact active
mapping and unchanged approval definitions. Mapping rows are locked while
committing; no mapping lifecycle mutation is performed by projection.

PROPOSED, RETIRED, UNMAPPED and AMBIGUOUS have no usable target. Wrong source/role
also fail before source access. A selected attribute must pass the existing
bounded Element→Database→Server lineage checks and direct-attribute guard.
Only selected value endpoints are read: maximum 5 signals × 5 guarded GETs = 25
per plan. Direct listing remains ≤100 attributes, no pagination/crawl/history.
The existing ≥1-second request floor, 1 MiB response cap and origin/root/link
checks remain enforced. No scheduler, parallel polling or technical-worker change.

Degraded states: NO_VERIFIED_MAPPING, NO_APPROVED_SIGNALS, SOURCE_UNAVAILABLE,
SOURCE_STALE, BAD_QUALITY, PARTIAL_SIGNAL_SET and PROJECTION_ERROR. Additional
UNKNOWN_VALUE, UNKNOWN_QUALITY and PROJECTION_NOT_RUN states preserve uncertainty.
Good=false or Questionable=true produces BAD_QUALITY while preserving the value.
A partial batch retains valid selected evidence and exposes missing/failing
signals. Failures preserve earlier successful evidence with its old timestamps;
a recent failed attempt does not make old values current. Invalid documents and
DB failures fail closed. No score/healthy classification is inferred.

## Independent freshness dimensions

| Dimension | Evidence / interpretation |
|---|---|
| Mapping readiness | current unique VERIFIED identity, not a timestamp age |
| Collector freshness | separately supplied latest successful collector cycle, not source freshness |
| Source freshness | each value's source_timestamp, including stale epoch values |
| Projection freshness | when a new evidence observation actually entered Mart; replay does not refresh it |
| Collection time | collected_at on each observation; independent of source timestamp |
| Latest attempt | attempt envelope; failure can be newer than retained evidence |

Optional policies: NADI_COLLECTOR_MAX_AGE_SECONDS, NADI_SOURCE_MAX_AGE_SECONDS,
NADI_PROJECTION_MAX_AGE_SECONDS. Empty/default = UNKNOWN, no assumed production
SLA. Negative source age/future timestamps are UNKNOWN. Policy thresholds can be
set independently. Historical measured acquisition duration (~508s), configured
post-cycle pause (300s), and effective start-to-start cadence (~808s) are separate
from all freshness dimensions and were not rewritten.

The fixture proves COLLECTOR_CURRENT + SOURCE_STALE + MAPPING_VERIFIED +
PROJECTION_CURRENT simultaneously under an explicit 60-second test policy.
The operator adapter's collector-success timestamp is an optional trusted input;
its CLI currently leaves this UNKNOWN rather than guessing technical collector
success from the newly acquired source snapshot. Future integration-status
orchestration may supply independently verified local collector metadata.

## Operator workflow (implemented, NOT executed against production)

Run each project's own CLI in its own runtime/environment. Keep handoff files
private and ignored; the source-containing output is created exclusively at 0600.
Only a registered, legitimately human-verified mapping and separately approved
signals may generate a plan. Synthetic examples are **TEST ONLY**, never imports.

```bash
# Cockpit operator, separate existing Mart admin DSN:
cockpit condition approve-signal --file <controlled-approved-signal.json>
cockpit condition plan --asset-id <canonical-id> --output <private-plan.json>
# PI Collector boundary, source credentials supplied only here:
picollector condition-evidence --plan-file <private-plan.json>   # dry run, GET0
picollector condition-evidence --plan-file <private-plan.json> --output <private-evidence.json> --execute
# Cockpit operator, no PI credentials:
cockpit condition project --file <private-evidence.json>
# Optional definition retirement, never deletes mapping/evidence history:
cockpit condition retire-signal --file <controlled-signal-id.json>
```

Library orchestration uses GovernedEvidenceSource / EvidenceDocumentSource and
ConditionProjectionService. The private handoff is implemented; automatic
production transport/scheduling and cross-source integration-status acceptance
remain separate work. No operator source invocation was made during this task.

## Synthetic acceptance and exact validation

Committed plan/batch/evidence examples under
`reliability-data-contracts/examples/condition-evidence/` contain only synthetic
identities/values/actors. Cross-project tests use the real PiClient request guards
and GovernedSourceBoundary with a fake HTTP session. They execute guarded lineage,
selected snapshot serialization, command-store projection, Mart reads and actual
FastAPI ASGI serialization. PostgreSQL fixtures apply the real canonical SQL and
use a real nadi_mart_reader that cannot mutate evidence even with read-only off.
No production mappings, source requests or test identities enter operational DBs.

From repository root, the final commands were:

```bash
# Disposable fixtures, no host ports, no operational volumes:
docker run -d --name nadi-ing-mart-test --network none --tmpfs /var/lib/postgresql/data -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test-only -e POSTGRES_DB=nadi_governance_test postgres:16.4-alpine
docker run -d --name nadi-ing-pi-test --network none --tmpfs /var/lib/postgresql/data -e POSTGRES_USER=test -e POSTGRES_PASSWORD=test-only -e POSTGRES_DB=pi_runtime_test timescale/timescaledb:2.16.1-pg16
# Mount this candidate's source; historical images supply existing dependencies:
docker run --rm --network container:nadi-ing-mart-test -v /home/john-d/.codex/worktrees/nadi-ing-pi-001a/reliability-knowledge-starter:/workspace:ro -w /workspace/reliability-cockpit -e RELIABILITY_MART_MIGRATIONS_ROOT=/workspace/reliability-cockpit/migrations -e DATABASE_URL=sqlite+pysqlite:///:memory: -e NADI_MART_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/nadi_governance_test reliability-cockpit-platform-nadi-runtime:runtime-002 python -m unittest discover -s tests -q
docker run --rm --network container:nadi-ing-pi-test -v /home/john-d/.codex/worktrees/nadi-ing-pi-001a/reliability-knowledge-starter:/workspace:ro -w /workspace/pi-collector -e PI_MIGRATIONS_PATH=/workspace/pi-collector/migrations -e PI_MIGRATION_TEST_DSN=postgresql+psycopg://test:test-only@127.0.0.1:5432/pi_runtime_test reliability-cockpit-platform-pi-reviewed:3e981a3 python -m unittest discover -s tests -q
```

Cockpit/Mart: **194 run, 189 PASS, 5 Compose tests skipped in fixture**.
PI Collector: **173 PASS, 0 skipped**, including **11 existing Timescale tests**.
One pre-existing off-hours test was corrected to freeze its service gate as its
comment already intended; no runtime guard changed.

From `reliability-cockpit/`:

```bash
NADI_COMPOSE_TESTS=1 DATABASE_URL=sqlite+pysqlite:///:memory: /home/john-d/Music/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python -m unittest discover -s tests -p test_runtime_wiring.py -q
```

**9 PASS**, including all five clean managed/external Compose checks skipped in
the container run. No existing PI .env/private override is needed for those tests.

From `reliability-data-contracts/`:

```bash
/home/john-d/Music/reliability-knowledge-starter/maximo-knowledge/.venv/bin/python -m unittest discover -s tests -q
```

**14 PASS**, validating all **27** Draft 2020-12 schemas and evidence type,
quality, timestamp, source-quarantine and governance negatives.

From `reliability-cockpit/web/`:

```bash
./node_modules/.bin/tsc --noEmit
node scripts/product-safety-check.mjs
npm run build
```

Type-check PASS; product safety PASS (15 UI source files); Next.js production
build PASS (13 generated pages, Asset dynamic route included). `git diff --check`
PASS. These are candidate artifacts, not deployed UI or operational projection.

## Production preservation — local inspection only

Inspected 2026-10-07T15:27:21Z before / 15:54:10Z after:

- PROPOSED0→0 / VERIFIED0→0 / total mappings0→0; public resolution UNMAPPED.
- Registered845; asset_master11845; maintenance69617; work_order113884 unchanged.
- Reader SELECT=true, mapping write privileges=false; admin remains separate.
- WO cursor retained `2026-10-07T14:59:45Z`; recovery floor retained
  `2026-08-21T03:56:54Z`, one recovery-floor record. Latest cheap incremental
  cycle 25 rows/errors0, 6.690s; no bootstrap/recollection.
- Both factual Mart projections SUCCEEDED; registry and decision-overview HTTP200.
  Registered maintenance activity: 7d779 / 30d1988 / 90d4226.
- PI registry490 total/433 active; snapshots433; latest completed collection
  433/433/errors0 at15:42:41.219626Z. Accepted PI migration004/checksum/application
  timestamp unchanged; Timescale/operational DB and volumes preserved.
- All inspected operational container IDs/images/start times unchanged,
  including Maximo/PI workers, NADI and CEMS API. CEMS/NK source code unchanged.
- New operational condition tables still absent; no production migration applied.

Task-attributable PI business GET0 / writes0; Maximo GET0 / writes0; history0;
AF crawl0; registry changes0; operational DB reset/delete0; new operational DB0;
restart/redeploy0; source credential exposure0. Existing autonomous collector
cycles continued normally; they were neither triggered nor reconfigured.
Private aggregate evidence stays ignored, outside the PR. Only the two isolated
synthetic test containers were created and removed.

## Roadmap effect and next step

NADI-PI-001 MERGED; NADI-PI-RUNTIME-001 ACCEPTED; NADI-RUNTIME-002 ACCEPTED.
NADI-IDN-002A R1/R2 evidence rounds completed without a proven bridge; human
crosswalk BLOCKED / EXTERNAL. Production VERIFIED identity remains0.
NADI-ING-PI-001A implementation CURRENT / candidate, synthetic foundation PASS.
No production projection, PI canary or Phase 1 completion is claimed.
Next recommendation: **NADI-INTEGRATION-STATUS-001**, preserving independent
collector/source/projection/mapping readiness. Production evidence additionally
requires reviewed migration deployment, real human-verified identity, explicit
signal approval and separately authorized bounded source execution.
