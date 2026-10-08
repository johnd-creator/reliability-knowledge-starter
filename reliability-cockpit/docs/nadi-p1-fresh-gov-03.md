# NADI-P1-FRESH-GOV-03 — public activation acceptance summary

## Scope and provenance

**PASS — three provisional activity-monitoring policies activated.** Phase 1
remains **CURRENT/PARTIAL**; product readiness is **UNKNOWN**. No condition policy,
source acquisition, projection, mapping or signal approval was performed by GOV03.

Fauzi authorized activation as project owner and accountable internal technical
approver. No external Maximo/PI owner endorsement or signed document is claimed.
The original approval remains **8 October 2026, DATE_ONLY, timestamp NULL**.

[Activation register](nadi-p1-fresh-gov-03-activation-register.json) supplements the
unchanged [historical GOV02 register](nadi-p1-fresh-gov-02-approval-register.json).
The explicit owner-revised expiry is **2026-10-13T00:00:00+07:00**, Asia/Jakarta,
earlier than the historical 15 October reference. It is not seven days after activation.

Reviewed main `1f7c25a711e68afc87ee0c4b1322bfca4be6ba97` contains merged PR27. Serving application
source `1cf7fed971594581913e8e7f635691f834133b6e` is identical to that main for the relevant API,
build and runtime contracts. This PR contains audit documentation only.

## Controlled change

Only the NADI API was replaced, using the previously accepted application image.
All other **22 containers**, workers, persistent storage and network attachments
were preserved. Effective configuration comparison allowed exactly three API
environment differences. Accepted configuration overlays were preserved and a
minimal API-only policy overlay connected the three approved settings to the
existing private platform configuration authority. No build, worker restart or
database migration was required.

The private configuration backup retains restricted access and original ownership;
unrelated settings and authentication material were preserved. No credential file,
value or secret-derived fingerprint is published. Concrete host paths, deployment
identifiers, image digests, backup locations, topology and executable rollback
instructions are retained in ignored operational evidence for the accountable operator.

## Effective policy

| Setting | Seconds / state |
|---|---|
| NADI_MAXIMO_WO_MAX_AGE_SECONDS | 660 |
| NADI_MART_FACTUAL_PROJECTION_MAX_AGE_SECONDS | 660 |
| NADI_PI_COLLECTOR_MAX_AGE_SECONDS | 1800 |
| NADI_COLLECTOR_MAX_AGE_SECONDS | UNSET |
| NADI_SOURCE_MAX_AGE_SECONDS | UNSET |
| NADI_PROJECTION_MAX_AGE_SECONDS | UNSET |
| NADI_CONDITION_SOURCE_MAX_AGE_SECONDS | UNSET |
| NADI_CONDITION_PROJECTION_MAX_AGE_SECONDS | UNSET |

Exclusive component mode was validated. Missing and future timestamps remain
UNKNOWN; legacy and component numeric policies cannot be mixed. Maximo monitoring
uses successful WO polling activity, not general asset source freshness. Factual
Mart monitoring requires success from **both asset and maintenance projectors**.
PI monitoring uses complete successful technical snapshot cycles; partial/error
cycles retain the preceding full-success timestamp.

Condition source/projection thresholds remain NULL and their freshness remains
UNKNOWN. Technical collection cadence does not establish a condition-use-age SLA.
Good quality describes evidence quality, not equipment HEALTHY. No timestamp was
changed to manufacture CURRENT.

## Acceptance and preservation

Accepted pilot payload, numeric type, source unit, quality flags, source/collection/
projection timestamps and governed lineage matched exactly before/after. Full
comparison evidence and original identifiers are retained privately. VERIFIED=1 /
PROPOSED=0; approved signal/latest evidence/projection state=1/1/1 remain unchanged.
Registry=490 total /433 active; snapshots=433. Registry reload, acquisition and
replay were not performed. Reader remains SELECT-only; cursors, recovery floor,
projector state, schema ledger and 34 historical artifacts were preserved.

Six local API routes and three web routes returned HTTP200. Browser checks confirmed
the pilot evidence and Data Trust panel render activity freshness independently
from condition freshness and signal quality. No fake health state was shown.
Technical bad-quality signals (18) and epoch source timestamps remain visible.
The existing rejected/frozen candidate and unresolved AF identity issue remain open.

## Measured nine-gate readiness

Initial post-activation readiness was **8 PASS /1 UNKNOWN**. At the final recorded
observation `2026-10-08T14:54:51.142814Z`, the unchanged background technical
collector had completed **432/433 with one error**. That cycle started before policy
activation; its cause was not diagnosed or inferred, and no retry/probe was performed.
The last full-success timestamp was retained. Final readiness is **7 PASS /1 PARTIAL /
1 UNKNOWN**, overall **UNKNOWN**. `phase1-readiness --require-pass` exits2.
These are recorded GOV03 observations, not a new live measurement by SEC01.

| Gate | Final recorded verdict | Reason |
|---|---|---|
| P1-MAXIMO-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT |
| P1-MART-CURRENT | PASS | LOCAL_EVIDENCE_CURRENT |
| P1-PI-COLLECTOR-CURRENT | PARTIAL | LOCAL_EVIDENCE_DEGRADED |
| P1-MART-GOVERNANCE-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-CONDITION-SCHEMA-READY | PASS | READER_SCHEMA_COMPATIBLE |
| P1-IDENTITY-MAPPING-READY | PASS | VERIFIED_PILOT_AVAILABLE |
| P1-SIGNAL-SELECTION-READY | PASS | APPROVED_PILOT_SIGNALS_AVAILABLE |
| P1-CONDITION-PROJECTION-READY | UNKNOWN | UNKNOWN_SOURCE_OR_PROJECTION_FRESHNESS |
| P1-INTEGRATION-STATUS-READY | PASS | STATUS_CONTRACT_VALID |

## Manual review and expiry

- Activation: **2026-10-08T21:45:26.619585+07:00**.
- 24-hour review: **2026-10-09T21:45:26.619585+07:00**.
- 72-hour review: **2026-10-11T21:45:26.619585+07:00**.
- Fauzi-confirmed checkpoint: **2026-10-12T20:00:00+07:00**.
- Hard expiry: **2026-10-13T00:00:00+07:00**.
- Accountable rollback operator: **Fauzi**.

Future reviews remain PENDING. Fauzi reviews local success/error histories, both
projector timestamps, stale episodes, partial cycles, false alerts and timestamp
anomalies without additional source requests. Changes or extensions need explicit
approval. The activation clock is separate from the original date-only approval.

There is **no automatic expiry scheduler**. Fauzi confirmed manual checkpoint and
rollback before expiry if no extension exists. Documentation alone does not enforce
rollback. The detailed approved recovery procedure and its source-free validation
remain private. It restores only the three approved values to UNSET, preserves
unrelated settings, reloads only the authorized API if required and verifies UNKNOWN,
unchanged accepted evidence and preserved workers. Release or authorization drift
requires reconciliation before execution. Expiry rollback was not executed by SEC01.

## Validation and safety evidence

Historical GOV03 targeted regression: **54 discovered, 45 PASS, 9 optional PostgreSQL
fixture skips**. No application changes were made. Public, source-free commands
can run from `reliability-cockpit` using a prepared component Python environment:

```sh
python docs/validation/nadi-p1-fresh-gov-01-simulation.py
python docs/validation/nadi-p1-fresh-gov-02-validation.py
```

The first validates 14 historical simulation cases; the second validates the five
historical owner-policy records and preserved original artifacts. Their older
UNSET/PENDING states are frozen historical evidence, not the active GOV03 state.
Activation-register/date arithmetic and local documentation links were checked;
`git diff --check` passed. Complete original infrastructure inventories and recovery
instructions were preserved privately before public redaction.

SEC01 is documentation sanitization only: production deployment/restart/configuration
changes, upstream PI/Maximo/CEMS requests, source writes, acquisition/replay,
mapping/signal/evidence writes, DDL and scheduler changes are **all zero**.
Git history was not rewritten: older public revisions remain accessible. A separate
private remediation proposal covers historical disclosures; no whole-repository
credential-clearance claim is made.

## Next steps

[Public migration-readiness summary](nadi-pre-migration-readiness-gov-03.md) records
engineering prerequisites only. Server migration, target connectivity and restore
acceptance remain separately authorized work. Monitoring activation is not a
database-migration prerequisite. Complete operator reviews and expiry enforcement,
then address condition freshness engineering acceptance. Phase 1 is not COMPLETE.
