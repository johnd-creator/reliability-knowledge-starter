# F-03 traceability — B5 independent review

Scope: mechanisms supplied by AUD-02B B1–B5 briefs and pinned implementation.
No separately endorsed, exhaustive Astra F-03/AUD-11 register was available; this
matrix is an evidence-backed mapping, not a claim to have closed unseen findings.
Paths below are relative to `maximo-collector/` unless stated otherwise.

| Failure mechanism | Corrective implementation/file/function | Executed check | Limitation / result / operational gate |
| --- | --- | --- | --- |
| Changed source population between pages | `src/repositories/projection_store.py`: `capture`, `bounded_query`, `fingerprint` | B1 capture suite; B5 `test_concurrent_source_change_snapshot_consistency` | One co-located REPEATABLE READ capture; not a remote Maximo snapshot. Synthetic verification only. |
| Missing Equipment silently skipped forever after watermark advance | `deferred_store.py`: `_on_receipt`, `family_identity`; `replay_store.py`: `_due_query`, `_source` | B5 `test_pipeline_partial_targeted_and_final`; B3 backdated/exact query tests | Old WO timestamp unchanged; source cursor never used as replay progress. Non-owner replay grant gap remains. |
| Target commit separated from receipt/progress | `projection_store.py`: `process`; `mart.py`: `persist_in_session` | B5 pre-commit crash and lost reply; B1 physical transaction tests | One supplied SQLAlchemy Session/connection and PostgreSQL transaction. Cross-database targets unsupported. |
| Stale owner completes or overwrites newer target | `projection_store.py`: `_lock`, `_not_expired`, target sidecar check | B1/B3 expired/newer-generation tests; B5 expired claim and legacy conflict | Participating writers only; legacy writer can mutate canonical target before detection. RESTRICTED. |
| Repeated deferrals double-count population | `deferred_store.py`: `_on_receipt`; B4 reader `_domain` | B2 repeated/superseded tests; B5 checkpoint reader | Exact family/current version; historical attempts are not new records. Unknown pre-B2 debt not auto-enrolled. |
| Dependency readiness treated as resolution | `deferred_store.py`: `_proof`, `transition`; `replay_store.py`: `resolve_claim` | B2 proof tests; B3 readiness/PROJECTED/DONE cases | Committed receipt and matching target digest required; manual policies still pending. |
| Unbounded or poisoned recovery | `replay_store.py`: `ReplayPolicy`, `reserve_attempt`, `_change`; service `ProjectionReplay.run` | B3 deadline/backoff/history/poison tests; B5 exhaustion and 100-family queue | Candidate caps retained. Fairness measured within one domain, no cross-domain scheduling promise. |
| Recovery marked as full population COMPLETE | `replay_store.py`: `_coverage_incomplete`; B4 `_domain` | B5 targeted checkpoint and later full generation | Targeted manifest remains PARTIAL; old PARTIAL input/receipt unchanged. |
| Latest attempt hides earlier failure/debt | B4 `src/repositories/projection_coverage.py`: `_domain`; domain `DomainCoverage` | B4 latest-failed/old-complete tests; B5 partial checkpoint | Latest attempt and complete pointer separate. Historical evidence beyond bounded reader limit is UNKNOWN. |
| Legacy SUCCEEDED promoted to coverage proof | B4 reader and `ProjectionCoverageService.reconcile` | B4 legacy, missing schema, source freshness and DTO tests | Default path unchanged; candidate legacy history UNKNOWN, no invented receipts. |
| Reader mutates data or sees source payload | B4 `MartDatabase.read_snapshot`, `ProjectionCoverageReader.read` | B4 actual SELECT-role denial tests | Explicit DB identity; no source/cursor/payload grant. No public endpoint; future actor review required. |
| Schema/guard drift falsely accepted | B1 `_schema_preflight`, B2/B3 catalog pins, B4 `catalog_signature` | B1–B4 drift suites; B5 real SQL install and manifest hashes | Test result must distinguish ORM-created fixture from actual migration-created canonical tables. |
| Privilege plan cannot perform guarded replay | B3 `_source(lock=True)` | B5 `test_distinct_projector_source_grants_and_guards` | **B5-GRANT-01 unresolved:** FOR SHARE denied to source SELECT-only projector. Separate design/remediation gate. |
| Evidence destroyed by downgrade/restore | B5 private `backup.py`: `qualify_restore`, `fingerprints` | Three-checkpoint backup, TOC read and separate DB restore hash/count comparison | Synthetic selected-schema restore only. No operational restore approval or full deployment backup claimed. |

## Transaction and lock-order review

B1 processing: domain row → run row → target/read sidecar → target+receipt → B2
family/version/event → continuation → final expiry check → commit. B3 claim:
domain → queue → new/resumed run; replay write adds exact source Work Order and
Equipment SHARE locks before canonical target and atomic receipt. B2 transitions
lock domain then version; audit triggers also acquire/verify the same domain.

Participating writers serialize per domain and locks have a one-second cap.
Synthetic concurrent claim, expired lease, pre-commit disconnect and post-commit
lost reply regressions remain required. External writers do not share this order;
no global deadlock-free or conflict-free claim is made. Cross-domain/cross-store
mutations and malicious owner SQL remain outside the proof.

`MartWriter.persist_collection` owns a separate commit and is unsuitable inside a
B1 receipt transaction. The candidate uses `persist_in_session` instead. Source,
canonical targets, sidecars, ledger, queue and events must share one physical DB.
A future operator must verify actual DSNs and ownership; B5 does not connect to them.
