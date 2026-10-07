# NADI-ING-PI-001B — candidate synthetic projection acceptance

All identities, selected signals, AF links and measurements in this harness are
synthetic. It does not promote/import operational mappings or call a production
source. The Collector fixture constructs the real guarded adapter with synthetic
HTTP responses; NADI consumes only the controlled evidence document.

## Acceptance matrix

| Case | Evidence / expected behavior |
|---|---|
| VERIFIED + approved | Explicit selected plan → guarded Collector fixture → Mart → GET API → React evidence/trust views |
| PROPOSED / RETIRED / AMBIGUOUS / UNMAPPED | Plan rejected before source port; no silent winner |
| No approved signals | No plan/source invocation |
| Source unavailable | Degraded attempt, previous evidence and projection time preserved |
| Bad quality | Four source quality flags preserved; no health inference |
| NULL / TEXT / DIGITAL_STATE / BOOLEAN | Exact types, false and digital code zero preserved; null never zero |
| Epoch source timestamp | SOURCE_STALE with explicit policy; collector/projection may remain CURRENT |
| Older batch / replay | Older ignored; replay idempotent and cannot freshen evidence |
| Same collection, different payload | Conflict rejected atomically |
| Governance changes in flight | Current mapping/selection rechecked under write transaction; obsolete plan rejected |
| Canonical PostgreSQL 002 → 003 → 004 | Ordered ledger, idempotent apply, factual tables/cursor preserved |
| Reader versus writer | Named SELECT-only reader can query condition relations and cannot DML even with read-only transaction setting disabled |
| JSON / Python / handoff | Actual Collector outputs validate canonical evidence, selection, plan and handoff schemas plus semantic Python checks |
| Public boundary | GET-only read routes; no arbitrary plan/attribute proxy or PI credential/client construction |

`tests/test_condition_evidence.py` supplies the complete mapping/value/quality/
transaction matrix on SQLite and opt-in PostgreSQL. `test_projection_acceptance.py`
adds multi-signal handoff/storage/status, actual ASGI serialization/GET-only checks,
canonical migration/ACL and rendered React acceptance. Local UI test uses
`web/scripts/evidence-acceptance.mjs`, the real pure evidence/trust view components
and synthetic API documents. It requires Node dependencies, not a running service.
The PostgreSQL test container deliberately skips this Node-only case; it is run
separately on the host. Browser navigation/build remains a separate regression.

## Running safely

Install Cockpit test extra (`pip install -e '.[test]'`) in the intended test
environment. For isolated PostgreSQL use `NADI_MART_TEST_DSN` pointing only to
localhost/127.0.0.1 and a disposable `*_test` database. The guard refuses other
identities. The test fixture resets **only** its disposable schema, never an
operational store. Set `RELIABILITY_MART_MIGRATIONS_ROOT` to this candidate's
migration directory when reusing an older test image.

From Cockpit: `python -m unittest discover -s tests -p test_projection_acceptance.py`.
`python scripts/export_evidence_contracts.py --check` checks reproducible status/
handoff exports; `--write` is the explicit file-generation mode. Canonical
selection/condition schema assertions are reused, not weakened to transport
shapes. Domain validation additionally enforces cross-field lineage, uniqueness,
selection provenance and finite values. Timestamp numeric coercion was removed
to agree with ISO-8601 contracts.

No migration 004 deployment or production projection is claimed. Human mapping
verification and separately approved signals remain mandatory for a real pilot.
