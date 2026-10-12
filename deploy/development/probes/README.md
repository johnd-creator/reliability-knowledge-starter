# FIX-04 disposable heap diagnostics

These tools **do not operate the NADI development controller**. They archive an
immutable PR SHA into a new directory beneath `/tmp/nadi-fix04-private`, bind
ephemeral loopback ports, and stop their transient services on completion/failure.
Do not point them at HTTPS3000, a live worktree or a persistent backend/database.

The archived Next application uses its locked dependencies and Node22.23.1,
2048MiB old-space, 2500MiB cgroup limit, CPU quota200%, TasksMax128, Restart=no.
The global Node installation and every official runtime setting remain unchanged.
Run **at most two** probes concurrently, preferably sequentially on a busy host.
The host headroom guard stops disposable testing below1200MiB available RAM.
It does not relax the application/worker safeguard or retry a replacement worker.

Example (use actual absolute repository/dependency paths):

```sh
python3 deploy/development/probes/run.py \
  --repo /absolute/repository \
  --sha 726ea1f1100c446112dcb71883d77839c5e5acfc \
  --deps /absolute/locked/node_modules \
  --output /tmp/nadi-fix04-private/new-run \
  --mode nav-poll --seconds 4500
```

Modes: `nav-poll`, `nav-no-poll`, `poll-only`, `nav-hmr`. Navigation cycles21
factual, Engineering, Advisory/Inbox and login/glossary routes at15-second pauses;
actual request counts, latency and route counts are recorded. HMR edits/restores
one synthetic label once/minute; the client must show both changes. Each test
authenticates a fictional fixture identity and repeatedly verifies its in-memory
session. No business commands or persistent QA access occur.

The explicit fixture variants are:

- Fixed development health URLs and proxy bases target an in-memory loopback API.
- A measurement-only compiler hook records counts/modules without retaining Stats.
- Only `nav-no-poll` disables polling, in the archived copy.
- Each archive has an independent Git identity and private fixture approval/worker
  receipt exercising the real status reader. These are **synthetic diagnostic
  fixtures**, not official compatibility approvals, backups or launcher releases.
- The sole known Next-generated type transformation is byte-audited and restored
  in the disposable archive. No running worktree reconciliation occurs.

This is HTTP loopback, not live HTTPS/security acceptance. The fixture implements
only an in-memory cookie login/read contract, **not production auth, password
hashing, RBAC, CSRF or persistence**. The existing hermetic security suites cover
those independently. Unsupported factual contracts return503; no measurements or
severity rules are invented. Fixture cardinality is smaller than persistent QA.
Git inspections use a smaller archived repository. The request rate is measured,
not asserted identical to the earlier live run. These differences limit inference.

`heap.cjs` uses an in-process inspector session (no TCP inspector) with512KiB
allocation sampling, private profiles every120s, capped64MiB/process. Five-second
heap/space/RSS/external/resource samples and GC observer events are recorded.
There is no forced GC, heap-limit change or heap snapshot in the sustained run.
Profiler/GC/serialization overhead is shared across variants and remains a
limitation. GC callback heap is an observer-time post-GC approximation, not an
exact dominator/retainer measurement. Active-resource counts are not a per-path
watch inventory. Sampling identifies allocation stacks, not retaining edges.

Optional `--flight-graph` is a separately declared diagnostic variant. The
disposable process intercepts only the locked `app-page.runtime.dev.js` load and
exposes its existing `pendingOperations` Map through one guarded initializer
assignment. It does not write installed dependencies or change hook callbacks,
eviction, links, framework safeguards or source approval. Every120s a bounded,
read-only traversal counts Map entries, `.previous`/`.awaited` ancestry, owners,
stack frames and WeakRefs **without dereferencing WeakRefs or reading owner data**.
At500,000 nodes it reports truncation/lower bounds. The traversal adds allocation
and CPU overhead, so record it explicitly and don't equate it to the uninstrumented
live worker. The Map is already held by enabled async hooks; this accessor is only
for disposable diagnostics and must never be installed in the live launcher.

`flight-ancestry.cjs` is a separate mechanism control: plain Node versus loading
the actual locked Flight runtime with that same read-only Map accessor. It drives
a bounded, artificial long-lived await context with no HTTP or app records, then
stops at its time/512MiB/graph bound. It is not a comparable navigation workload,
not a reproduced live failure, and not an application/library patch proposal.
Use the same transient resource caps and serialize it after sustained probes.

Raw profiles/journals stay inside the private output directory. Never commit them.
`summarize.py` emits only aggregate numeric timelines, source identities and
bounded allocation categories/function names. Review even those before publishing.
Screenshots from this tool are **disposable fixtures**, never live HTTPS3000.

On interruption, SIGINT the **exact identified disposable Python controller**;
its finally block stops its own transient service/browser/fixture. Do not use
broad process-name kills. Preserve output as failed/incomplete evidence.

Sustained runtime acceptance, a root-cause fix and live Product Owner acceptance
are separate gates. A75-minute negative reproduction alone does not prove a fix.
