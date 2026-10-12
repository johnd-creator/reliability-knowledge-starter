# FIX-04 sanitized diagnostic evidence

Scope: **isolated disposable HTTP fixtures**, not the running HTTPS3000 preview,
persistent QA acceptance, engineer UAT or operational data. Baseline application:
`726ea1f1100c446112dcb71883d77839c5e5acfc`. The archived copy SHA differs because
health/proxy endpoints and diagnostic hooks are declared fixture variants.
Synthetic worker receipts/compatibility values in screenshots are not approvals
for a real frontend/backend pair.

See the [investigation report](../../nadi-dev-status-runtime-fix-04.md) and
[reproduction instructions](../../../../deploy/development/probes/README.md).

## Numeric measurements

- [Navigation + polling](nav-poll-summary.json).
- [Polling-dominated](poll-only-summary.json).
- [Navigation without polling](nav-no-poll-summary.json), with declared graph-probe overhead.
- [Navigation + HMR](nav-hmr-summary.json): **worker replacement after65.2min**, stopped without retry; original generation metrics only.
- [Incomplete first HMR trial](hmr-incomplete-summary.json), harness timeout at55min, excluded from the complete comparison.
- [First HMR ancestry timeline](flight-incomplete-timeline.json).
- [Corrected HMR ancestry timeline](nav-hmr-corrected-flight-timeline.json).
- [No-poll ancestry timeline](nav-no-poll-flight-timeline.json).
- [Standalone mechanism controls](mechanism-controls.json): artificial hot loop,
  no application/network/backend; `weak` is rejected negative experimental evidence.
- [Preservation summary](preservation-summary.json): source/PID/file hashes,
  explicitly **not a fresh persistent QA or container audit**.

Final figures are [heap/GC comparison](heap-timeline.png) and
[Flight ancestry](flight-ancestry.png). The red dotted line marks the original
HMR worker's final observed time at replacement, not a successful low-heap
recovery. Sampling can miss the request-level threshold crossing.
Warm slopes are OLS after minute15. Post-major-GC measurements are observer-time
approximations. Allocation sampling identifies stacks, not object dominators or
all retaining roots. Comparisons have request/session/instrumentation differences
documented in the report. Positive slopes are not extrapolated to a crash date.

## Reviewed fixture screenshots

Real rendered Next browser from the completed navigation+polling disposable run.
All displayed counts, records, personas, hashes/receipts and availability are
fixture values. These files contain no plant evidence, login credentials, real
personnel or persistent QA records and were not regenerated or edited.

- [Desktop 1440px](fixture-only-1440.png).
- [Tablet 768px](fixture-only-768.png).
- [Mobile 390px](fixture-only-390.png).

Raw heap profiles, per-process logs, failure journals and private preservation
snapshots are retained locally and are **not committed**. Exact-head GitHub CI
and sustained isolated measurements are separate evidence gates. No live
cutover, runtime fix or Product Owner visual acceptance is asserted.
