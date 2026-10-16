# Historical exceptions, governance and bounded capacity

## Decision register — no automatic resolution

All decisions below are **PENDING owner/operator approval**. B5 neither imports
historical debt nor deletes/forgives records, changes epochs or resets attempts.

| Case | Current behavior / fail-closed result | Impact and reviewed options | Required authority/evidence; prohibited shortcut |
| --- | --- | --- | --- |
| Legacy SUCCEEDED without candidate manifests | Activity only; B4 coverage UNKNOWN | New full capture alone cannot invent earlier missing evidence; assess unknown-history boundary | Mart/data owner approves reconciliation population/date and backup; no fabricated receipts |
| B1 unlinked items / pre-B2 debt | UNKNOWN/unlinked count; holds complete coverage | Bounded explicit lineage enrollment proposal or documented separate history treatment | Source and Mart owners; exact IDs/checksums, scope, dependency/version evidence; no auto-import/debt deletion |
| Earlier incomplete runs | Original PARTIAL immutable; later full COMPLETE requires current proof | Retain both attempts and last complete pointer | Operator audits immutable rows/receipts; no status rewriting to hide failure |
| Deleted/missing source WO | B3 SOURCE_ABSENT, blocked queue, unresolved B2 debt | Investigate archived local evidence or owner-confirmed absence policy | Source data owner plus operator; no live source fetch or silent exclusion under B5 |
| Missing Equipment | Open debt, bounded readiness probes/backoff | Repair exact local dependency only under separately authorized workflow | Governed exact identity and scope; no fuzzy match, invented Equipment or cursor reset |
| Unknown BSR/IP or invalid mapping | UNKNOWN / review-blocked; never proven exclusion | Review verified mapping/scope or mapper epoch correction | Data owner/engineer evidence; no guessed site/org/prefix or automatic poison reset |
| Overtaken run/expired fence | FencedOut or unreconciled stale claim; no late commit | Inspect recorded owner/fence/receipt; propose explicit new ownership and retained-history reconciliation | Operator-approved ownership/queue transition evidence; no forced lease reset |
| Abandoned WRITING/PROJECTED | Resume same run only when current, within budgets; verify committed receipt | Distinguish pre-commit loss from post-commit lost reply | Durable journal, target digest, exact family/version/receipt; no accept-by-phase alone |
| Policy/epoch mismatch | Refusal/BLOCKED, original debt and queue retained | Explicit migration/re-enrollment design with preservation proof | Owner governance and exact old/new policy digest; no dropping mismatched rows from counts |
| Retry/history/retention limit reached | BLOCKED/UNKNOWN; existing evidence kept | Capacity or retention decision with independent authorization | No cap increase, event pruning or inferred forgiveness as an automatic retry |

## Phase 1 / AUD-11 alignment

[Authoritative Phase 1 acceptance](../../../plans/NADI-PHASE-1-ACCEPTANCE.md) retains
CURRENT/PARTIAL. Its 72h audit records monitoring PARTIAL and product readiness
UNKNOWN. The later owner-revised GOV-03 hard expiry was **13 October 2026 00:00 WIB**,
with manual enforcement. That date precedes this B5 audit. No later renewal or
actual runtime policy state is established by B5; operator must resolve this under
separate authority. The historical GOV-02 calendar date is not a substitute renewal.
No policy setting is read, extended, activated or rolled back here.

| Governance concept | Candidate evidence | Gate retained |
| --- | --- | --- |
| Started/latest activity | recorded run state/start, not success | Unknown/failed work cannot be CURRENT |
| Full successful coverage | sealed full manifest + receipts + debt/target proof | Targeted recovery remains PARTIAL |
| Deferred/failed outcomes | family/version/replay stage, reason and immutable journal | No operational forgiveness or invented assessment |
| Source freshness | caller-supplied independent source observations/policy | Source cursor/record timestamp is not projection completeness |
| Projection freshness | verified last COMPLETE clock only | Partial attempt does not refresh complete time |
| Thresholds and expiry | existing policy object; synthetic test values 660/660/1800 | No new thresholds or extension; both condition policies remain independent |
| Identity/provenance | exact run/fence/manifest/source/target proof internally | No new public DTO/route or actor authorization |
| Legacy evidence | explicit historical UNKNOWN | No fabricated past acceptance |
| Engineer/operator boundary | isolated synthetic proof only | 26 engineering decisions unchanged; engineer UAT/operational acceptance pending |

AUD-11 standalone authoritative decisions/endorsement were unavailable in the
pinned repository. Alignment is **PENDING_GOVERNANCE**, not Astra endorsement.
Astra F-03 operational closure remains OPEN.

## Capacity results and limitations

Final exact-head CI contains measured JSON metrics for Python 3.11/3.12 and its
actual PostgreSQL version; use those over earlier development timings. Local settled
runs used Python 3.14.3 / PostgreSQL18.6. Representative development observations:

| Experiment | Tested population / limits | Observation |
| --- | --- | --- |
| Default full capture | 10,000 rows; 15s / 16MiB / page100 | SEALED, about3.1–3.5s; ~6.67MB WAL; ~5.74MB manifest+indexes |
| Default over-budget population | 10,001 rows; unchanged default | BUDGET_REFUSED, zero durable items; WAL/allocated relation space still consumed by rolled-back work |
| Explicit hard-limit capture | 100,000 rows; 60s /64MiB / page100 | SEALED locally in34–44s; ~66.65MB WAL; ~56.89MB manifest+indexes; measured worker peak RSS roughly110MiB |
| Illegal configured limit | 100,001 configured rows | Constructor rejects; no claim of successful capture above hard limit |
| Deferred ledger / receipts | 100 current families, 100 receipts | ~174receipts/s in one local sample; indexed due page20 ~3ms |
| Fairness | 100 same-domain queue families | First not-ready family backoffs behind next due family; no global scheduling guarantee |
| Reader | Small final integrated checkpoint | 63 SQL executions including settings/transaction setup, about47ms locally; bounded internal query counter remains separate |
| Reader population/proof cap | rows1 against integrated fixture | Explicit UNKNOWN, never zero debt or CURRENT |
| Contention | Held domain row lock | Refused around1s, below test's4s upper bound |
| Concurrent source change | Snapshot captured CAN, source then COMP | Old captured value retained; not a live source-system snapshot |

The hard-limit experiment uses explicit existing candidate maxima for that one
synthetic capture; defaults are unchanged. It does not qualify 100,000 target writes,
100,000 debts, full retention, full-scale B4 proofs, production IOPS/WAL/archive/replica
load, cross-domain fairness or long-running operational contention. Peak RSS is the
preparation worker's process peak, not a whole-cluster memory measurement. WAL bytes
include capture/preflight traffic; they are not a dedicated production WAL estimate.

Candidate envelope recommendation: retain defaults (10k capture,16MiB,15s), bounded
processing batches and independent reader proof limits. A capture can legitimately
exceed B4's default1000-row aggregate proof budget; reader then returns UNKNOWN.
Do not silently raise limits to make large histories current. Rollout needs agreed
population partitioning/retention and a measured production-like environment. Resource
qualification remains PARTIAL outside the explicitly tested experiments.
