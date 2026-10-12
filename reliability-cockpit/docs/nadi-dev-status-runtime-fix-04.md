# NADI-DEV-UX-STATUS-01-FIX-04 — heap retention investigation

Verdict: **PARTIAL — NEEDS FURTHER INVESTIGATION**. A development-only React
Flight retention mechanism is measured in the locked runtime. A safe application
fix and the complete retaining path for module-source allocations remain
unresolved. The Next heap-threshold replacement class was reproduced after
65.2 minutes in an instrumented isolated workload; precise live dominance and
timing are not established. No live cutover or merge is
authorized by this task. PR #78 is a diagnostic draft stacked on PR #77.

## Source identity and the failed acceptance checkpoint

The immutable application baseline is PR #77
`726ea1f1100c446112dcb71883d77839c5e5acfc`. Verified main is
`2e190c2b51fde50e0467d6d5165ebb1060902867`. Dependencies remain OPEN:
PR #75 `5e961b1bfe8ce3c34092613922c3b556de3d74a1`, PR #76
`8711ff3e86ff36c364290b4370863deb943c2b0b`, and draft PR #77. The exact
investigation HEAD and exact-head Actions run are recorded at the PR handoff.

FIX-03 live acceptance failed on 12 October at 16:38:25.260994 WIB, after
3475.85 seconds (57m55.85s) following the final startup. The Next development
heap safeguard replaced worker 3010264 with 3078400 while parent 3010238 and
systemd NRestarts=0 remained. Sampled heap peaked at 1652.4 MiB; sampled/kernel
cgroup peaks were 2123.7/2189.8 MiB. The threshold message and generation change
were observed; no V8 abort or OOM was observed. The required 60-minute gate
failed and 15-minute handoff was not run. Earlier browser/HMR/login successes
and CI cannot override that failure. Official recovery restored the known-good
frontend and original runtime/controller. Earlier reports remain historical
evidence, not current acceptance.

FIX-04 leaves HTTPS3000 serving
`f06abce76f8ef9b967ee5b1c2e0802112d77b056` on the restored Node 25.6.1.
QA API source remains `b348235ce6f82c84873a65344ad2ef5fe276987d`. No request,
reload, HMR edit, rebuild, service action or source switch was directed at that
frontend by this investigation.

## Controlled workload and measurement

The [reproduction tools](../../deploy/development/probes/README.md) archive the
baseline into a new private disposable directory. They use Node 22.23.1 / V8
12.4.254.21-node.56, Next 15.5.9, bundled Webpack 5.98.0, root React/React DOM
19.2.8 and Next's bundled React 19.2.0-canary-0bdb9206-20250818. The executable
SHA256 is `9d9f55f1f4497fe069d681020b728f77221c43b9a4e9576a89ff7cc537caf5cf`.
The locked app-page runtime SHA256 is
`f5642afec1b380029730444582c0af19300709dcb586f91c96cb002fc8bffddb`.
Installed versions of 244 packages matched the lock; 27 platform-optional
packages were absent. No installed dependencies or lockfiles were changed.

Each transient service retains old-space 2048 MiB, measured V8 heap limit
2096 MiB, cgroup MemoryMax 2500 MiB, CPUQuota 200%, TasksMax 128 and Restart=no.
Development filesystem cache is false, as in PR #77; Next's GC cache and
approximately 1676.8 MiB used-heap restart threshold are untouched. An initial
synthetic worker receipt is never refreshed for a replacement worker. A changed
generation or host available memory below 1200 MiB stops the disposable run.
Heavy probes are serialized after the initial two runs.

The browser cycles 21 factual, asset, Engineering, Advisory/Inbox, glossary and
login routes with a 15-second pause. The HMR variant edits and restores one
synthetic DEV label each minute and requires both rendered changes. Polling
retains the existing 5-second cadence except in the explicitly declared
no-poll archive. A fictional in-memory identity signs in and repeated session
reads verify the fixture cookie. Unsupported DTOs return 503 rather than
fabricated successful data. No source, persistent QA API or database is used.

Parent/worker heap, spaces, RSS, external/array buffers and resource counts are
sampled every five seconds; cgroup CPU/memory/events, compiler module counts,
route and request counts are recorded. In-process inspector allocation sampling
uses 512 KiB and private profiles every 120 seconds, capped at 64 MiB/process.
No TCP inspector, heap snapshot, forced GC, heap increase or V8 safeguard change
is used. Raw profiles and journals remain private.

Two scenarios additionally expose the already-rooted Flight `pendingOperations`
Map through a guarded initializer in disposable process memory. Read-only
traversal follows `previous`/`awaited` at most 500,000 nodes every 120 seconds;
truncation is a lower bound. It never dereferences promise WeakRefs or reads
owner data. Installed bundle bytes and async-hook algorithms are untouched.
This traversal and module-load interception add overhead and are explicitly
distinguished from the two sampler-only runs.

## Results

Three baseline scenarios completed ≥75 minutes. The corrected HMR trial
reproduced a framework worker replacement at 65.2 minutes and was stopped without
retry. This satisfies the earlier-failure reproduction exception; it is a failed
runtime gate. None is a remediated-candidate acceptance.

| Scenario | Seconds | Navigation / status / HMR | Heap peak/final MiB | Warm heap / post-major-GC slope MiB/min | Kernel cgroup peak MiB |
|---|---:|---|---:|---:|---:|
| Navigation + polling | 4522.8 | 276 / 1057 / 0 | 1249.4 / 1198.7 | 9.837 / 9.186 | 1874.9 |
| Polling-dominated | 4528.1 | 0 / 908 / 0 | 545.5 / 545.5 | 3.168 / 3.109 | 1059.2 |
| Navigation without polling, with graph probe | 4528.0 | 281 / 0 / 0 | 934.4 / 855.6 | 6.797 / 6.502 | 1625.1 |
| Navigation + HMR, with graph probe — FAILED | 3911.8 | 225 / 1004 / 65 | 1637.8 / 1635.6 | 17.112 / 16.242 | 2274.2 |

The completed runs have unchanged parent/worker identities, zero browser page
exceptions, V8 aborts, OOMs or unapproved replacement workers. All have positive
post-major-GC warm slopes. Absence of a reproduced restart is not resolution of
the earlier live failure. See [sanitized evidence and fixture screenshots](evidence/nadi-dev-status-runtime-fix-04/README.md).

At 22:12:15 WIB the corrected HMR journal reports the Next used-memory threshold
restart. Worker3355751 became3427089; parent3355725 stayed unchanged. The sampler
can miss the actual threshold crossing between five-second observations. Cgroup
OOM/max counters stayed zero; no V8 fatal message was observed. The service was
stopped immediately after generation refusal; no replacement receipt, source
repair or retry occurred. Browser cancellation after fail-stop is not an
independent application/browser error. There were65 completed edit/restore HMR
cycles,225 navigations and22 successful in-memory session reads before stopping.
The disposable tree retained only the exact regenerated next-env route reference
(`.next` → `.next-primary-dev`), confirming the same integrity consequence as live.

The original worker ended with750.9 MiB old space and844.1 MiB large-object space.
External/array-buffer peaks160.1/156.0 MiB, stable final FSEventWrap46, parent heap
peak23.6 MiB and worker RSS peak2041.2 MiB do not explain this as a parent-process,
watcher-count or solely native-buffer growth. These measurements still do not
identify every retaining root. The final402.3 MiB cgroup sample is **after worker
replacement** and must not be treated as a good steady-state result.

## Retention evidence and attribution

In the first HMR diagnostic, a sample at about two minutes had 8,741 live Map
entries but 114,015 reachable ancestry nodes. At twenty minutes only 66 entries
still reached 351,303 nodes, including 343,883 WeakRef wrappers and 102,494 stack
frames. Several later traversals hit the 500,000-node cap. Evicting Map entries
does not bound the strongly linked history reachable from surviving entries.
Weak references to promises do not make the `previous`/`awaited` edges weak.
This establishes retained development metadata in this locked runtime, without
claiming that every heap byte is owned by that graph.

A separate mechanism control loads the **actual locked Flight bundle**, not a
copied/stubbed algorithm, and drives a bounded long-lived await loop without
Next server, Webpack, HTTP or application records. Plain Node ran about 21
million iterations for 30.1 seconds with 6–7 MiB heap. With Flight loaded,
100,773 iterations reached about 202.1 MiB heap and at least 500,000 ancestry
nodes in 2.0 seconds; sampled previous-chain depth was 258,611. It stopped at
the diagnostic graph bound, not an OOM. This isolates a framework mechanism;
the artificial request-free hot loop is not reproduction of the live workload.

Allocation sampling also identifies a large navigation-related module-source
component. In navigation+polling, sampled module-read allocation grew from
83.6 to 225.4 MiB during the first 22 minutes; polling-dominated stayed at
59.7 MiB. Flight debug allocations rose in both. At 75 minutes the navigation
worker's large-object space was 765.7 MiB versus 105.5 MiB polling-dominated.
Stacks include `defaultLoadImpl`/`readFileSync`, CommonJS module loading and
Webpack require paths. These are allocation stacks, not a full path-to-GC-root
or dominator analysis. The owners retaining all module-source strings remain
UNKNOWN; attribution of that whole component to Flight or Webpack is not proven.

| Area | Evidence and practical conclusion |
|---|---|
| Webpack modules/cache | Filesystem cache is disabled in all scenarios. Compiler/module counts and source-read allocations are recorded. Next's own GC cache remains; cache false does not mean no in-memory caches. No complete cache-retainer attribution exists. |
| Navigation / RSC | Broad navigation adds substantial large-object/module-source allocation. Flight ancestry is strongly retained in the graph variants. No unsupported claim of a production leak or application data leak. |
| HMR / invalidation | 65 actual edit/restore cycles,801 compiler completions and threshold replacement after65.2min with cachefalse. The reproduced workload has the steepest warm post-GC slope; graph/sampling overhead and unequal request counts prevent attributing the entire increment to HMR alone. |
| DEV polling / Git inspection | Polling-dominated grows after major GC; no-poll navigation also grows. Polling is a contributor/workload, not established as the sole cause. Archive Git inspection is smaller than the live repository. |
| Authentication/session | In-memory fixture login/read flow works and existing hermetic auth suites remain required. This does not profile real password hashing, persistent sessions, RBAC or database middleware. |
| File watchers/resources | Final FSEventWrap counts were 46 (navigation+polling) and 45 (polling-dominated). Counts do not identify watch paths or prove correct cleanup of every resource. No measured accumulating watcher count explains the slope. |
| Native/external memory | External and array-buffer observations are separated from heap/RSS/cgroup. Increasing post-major-GC JavaScript heap and old/large-object spaces show that this is not explained solely by native buffers. |

The related [React issue #36836](https://github.com/react/react/issues/36836)
is closed as stale/unconfirmed and describes different versions. It is
corroborating context, not proof about NADI. [Next issue #85666](https://github.com/vercel/next.js/issues/85666)
links to [React draft #37134](https://github.com/react/react/pull/37134), which
proposes keeping history needed by live requests while expiring older debug
ancestry. That proposal is stacked on other framework work and is not an
approved, version-compatible patch for NADI's bundled canary. No upgrade or
backport was applied.

## Rejected intervention and remaining diagnostic

A weak-link causal control was tried only in a standalone disposable module
load. At 4.0 seconds it consumed about 523.9 MiB heap (65,163 iterations), worse
than the unmodified Flight control, and stopped at its 512 MiB diagnostic bound.
It alters private React diagnostic semantics and adds per-edge WeakRef/accessor
cost. It is **rejected**, never selectable by the application probe or official
launcher, and never installed in dependencies. Its source remains solely as
reviewable negative experimental evidence.

No remediation is promoted. Candidate-versus-baseline 75-minute acceptance is
therefore NOT APPLICABLE, not PASS. Disabling polling, increasing limits,
disabling safeguards or accepting a new worker generation would mask symptoms.

The next diagnostic should isolate the persistent module-source retainer with a
bounded private snapshot in a low-memory **disposable** worker, or targeted
module-generation/source-map cardinality instrumentation. Compare an uninstrumented
control and the same read-only graph probe under equal request/session counts.
Then review a framework-supported repair/backport with explicit bundled-React,
RSC/HMR/debug-channel compatibility and regression analysis. Keep upstream
request-lifetime semantics; do not indiscriminately sever debug ancestry.

## Measurement limits and failed attempts

These runs use HTTP loopback, a smaller fixture population and archive Git
history, not live HTTPS or persistent QA. Both backend bases share one fixture
HTTP origin, unlike the two live backend services; connection-pool, latency and
async-context diversity consequently differ. Fixture auth only imitates cookie
login/read shapes: no real password hashing, RBAC, CSRF, audit or persistence
proof is claimed. Polling-dominated also performs a session read each 15 seconds
(300 reads), whereas navigation reads once per ten navigations (27 reads in the
first complete run). Counts and graph instrumentation differ; these are not
perfectly controlled estimates of polling's marginal memory cost.

GC callback heap is measured when the PerformanceObserver executes, an
observer-time approximation after GC. Warm slopes use ordinary least squares
after minute 15, with no confidence interval or replicate estimate. Sampling
and profile serialization allocate memory; the sampling inspector's asynchronous
work can itself enter Flight debug tracking. A matched sampler-off/minimal-heap
counter control is still needed to quantify that contribution. Module-load interception for graph
access also affects source loading; strong reachability is observed, but its
byte contribution and exact live dominance remain unquantified. A positive
slope over 75 minutes is concerning, not proof of indefinite linear growth.
The earlier Node25 fast-API/deoptimization abort was not reproduced here; it
remains separate from the observed Next heap-threshold generation change.

Early pilots failed because of translated locator case, premature hydration,
`networkidle` on polling pages, invalid list-shaped summary DTOs and rapid reverse
HMR edits. These were harness/fixture defects; those incomplete trials were
retained and excluded from the valid comparison. A corrected pilot completed
36 navigations and two actual HMR edits with zero page exceptions.

The first sustained HMR trial stopped at 55.0 minutes on a DEV marker timeout
after `/login` → application layout. Worker identity stayed fixed with no V8
abort, OOM or threshold restart. Its 54 completed HMR cycles, 189 navigations and
zero page exceptions are partial evidence, not 75-minute PASS. The harness now
waits for application hydration/status and HMR-client settlement before editing;
the corrected sustained result is reported independently: it passed this harness
transition and later failed at the real Next memory safeguard after65.2 minutes.

## Preservation, validation and proposed future live procedure

FIX-04 adds diagnostics, confinement tests, CI syntax checks and documentation.
It changes no application source, Next config, lockfile, runtime controller,
authentication, database, collector or operational configuration above PR #77.
The Node22 pin and all existing generated-file/worker-integrity safeguards remain.

Private before/after hashes cover five original PNGs, `23496711.xls`, active
controller/helper/release/selection/runtime files and the retained private backup
dump. Runtime continuity is checked by exact frontend/API PID/start/listener and
clean source identity. Final comparison found zero changed preserved files,
unchanged root status (only original untracked workbook), and clean frontend/API
sources. Frontend parent3078556/worker3078570 retain the16:38:28 start; API1664250
retains11October07:53:34 start; both systemd restart counters remain0. The
[preservation summary](evidence/nadi-dev-status-runtime-fix-04/preservation-summary.json)
records the scope of this proof. Exact-head CI is recorded at handoff.
No worktree, backup, session, audit or source asset is removed.

A proposed read-only persistent QA schema/record/session inventory was rejected
by automatic approval review because this investigation is non-operational. It
did not execute and was not retried through an API or backup decode. Fresh
database/schema/session/record and 35-container before/after comparisons are
**NOT VERIFIED**. No database or Docker action was performed. Prior live
preservation reports remain historical evidence; service continuity and file
hashes are narrower proof, not a current database audit.

Local checks include 44 controller tests, six new confinement/privacy tests,
syntax, TypeScript and lint (zero errors; one existing EngineeringWorkspace
hook-dependency warning). Required exact-head CI covers frontend assertions,
build and 455 network-isolated browser checks, backend trusted HTTP/security
regression with disposable PostgreSQL, and canonical contracts. CI does not run
the 75-minute probes and cannot establish live stability.

Graph discovery used Tier2; coverage generation 2026-08-24 excludes deployment
and lacks current symbols. Every operated code path was read directly after
coverage fallback. No claim relies on absent graph results.

Before any future live test: complete cause-specific remediation and a matched
baseline/candidate ≥75-minute run; pass exact-head CI and security/HMR regression;
obtain **new Product Owner approval** for immutable source/controller SHA. Only
then use the official frontend-only backup/preflight/compatibility/recovery
procedure, preserve Node22 pin/caps and all rejection gates, and observe exact
parent/worker generations. Any crash, generation or integrity failure requires
official recovery to the retained known-good source without automatic retry.
This is a proposal only. FIX-04 ends without live acceptance or auto-merge.

## Changed files above PR #77

Only the diagnostic paths below change; application/backend/controller source,
configuration, migrations and dependency locks are byte-identical to PR #77.

- `.github/workflows/nadi-engineering-candidate.yml`: confinement/privacy suite
  and diagnostic JS syntax, no runtime activation.
- `deploy/development/probes/README.md`, `run.py`, `heap.cjs`, `webpack.cjs`,
  `fixtures.cjs`, `workload.mjs`, `summarize.py`, `plot.py`, `flight-ancestry.cjs`,
  `weak-flight-map.cjs`: bounded disposable tools and rejected control.
- `reliability-cockpit/tests/test_heap_probe_safety.py`: four output confinement
  and two export privacy checks.
- `DEV-LOG.md`, this report and the files in the
  [evidence index](evidence/nadi-dev-status-runtime-fix-04/README.md): appended
  actual milestones, sanitized numeric/identity JSON, two figures and three
  fixture-only screenshots. No raw heap profile, database dump or journal is
  committed. Corrected trial startup captures nine diagnostic script SHA256s;
  runtime probe code is at9edac65bf3c87ff8cdf842a1b96a2fe45a16093f. Only offline
  plot annotation changed after the trial to mark its failed generation.

## Distinct review findings

| Severity | Finding | Disposition |
|---|---|---|
| HIGH | A 15-minute isolated PASS did not establish sustained live stability; internal worker replacement is invisible to systemd NRestarts. | Retained prior failure, ≥75-minute isolated workloads, exact generation fail-stop; no live retry or weakening of safeguards. |
| MEDIUM | Fixture summary DTOs and login/layout hydration races could invalidate browser conclusions. | Corrected harness/fixtures, excluded failed pilots, separately retained incomplete HMR trial; no application defect inferred from those failures. |
| MEDIUM | Webpack functionName may embed an absolute module path even when callFrame.url is suppressed. | Suppress entire path-bearing function ID before publication; Windows/Unix/URI and length-bound regression tests PASS. Raw profiles never uploaded. |
| MEDIUM | Parallel probes could unnecessarily pressure the active host. | Rejected third concurrent probe was not started; later heavy workloads serialized, unchanged caps and host-headroom stop retained. |
| OPEN | Flight ancestry and module-source allocation increase, but complete live retaining ownership and safe framework repair are unresolved. | PARTIAL; no runtime fix or sustained candidate acceptance claimed. |
