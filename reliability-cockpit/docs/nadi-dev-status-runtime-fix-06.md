# NADI-DEV-UX-STATUS-01-FIX-06 — vendor-map mitigation assessment

**PARTIAL — sustained candidate acceptance NOT ESTABLISHED.** Vendor exclusion
reduced heap growth in the observed common window and preserved essential
application debugging. Baseline hit Next's heap safeguard at79.85min. Candidate
stopped at39.58min on an extra-PID guard observation whose owning process was not
captured sufficiently to establish a real replacement. No retry, live acceptance,
leak-fixed claim, deployment or merge is made.

## Baseline, source and delivery

Base FIX-05 / [PR79](https://github.com/johnd-creator/reliability-knowledge-starter/pull/79):
`63b61d09c45630a76657cdb54991349fb0528e7b`. Branch
`codex/nadi-dev-status-runtime-fix-06`; [DRAFT PR80](https://github.com/johnd-creator/reliability-knowledge-starter/pull/80)
is stacked on FIX-05. Verified main at preflight:
`2e190c2b51fde50e0467d6d5165ebb1060902867`. Adapter/qualification implementation
was committed before the candidate run; final immutable delivery HEAD/CI appear
in the PR handoff. Actual archived application source is63b61d0 with declared
fixture/config wrappers, not a new application deployment. Definition hashes and
private copies retain each experiment's exact tooling and synthetic Git identity.

Application source, app Next config, locks, backend, migrations, collectors,
official controller, operational policy and original assets are byte-identical
to FIX-05. Only experimental tools/tests/CI and documentation/evidence change.

## A — read-only primary runtime: OPERATIONAL REVIEW REQUIRED

Frontend source`f06abce76f8ef9b967ee5b1c2e0802112d77b056`, parent3078556,
listener worker3744151 and exact generated `next-env.d.ts` dirt (`.next/types/routes.d.ts`
→ `.next-primary-dev/types/routes.d.ts`) were present before this task.
Retained journal establishes that Next replaced historical3078570 at13October2026
03:31:52WIB after its used-memory-threshold warning. Parent/start identity and
systemd NRestarts0 survived; that counter misses internal replacements.
Actual executable is Node25.6.1, while retained runtime JSON describes Node22.23.1.
No acceptance is inferred from matching controller/asset hashes.

QA parent1664250/child1664262, source
`b348235ce6f82c84873a65344ad2ef5fe276987d` and clean tree remain. Verified TLS1.3
handshake onHTTPS3000, TCP listeners13036/8000, and targeted port8000 ownership
`reliability-cockpit-platform-cockpit-api-1` / diagnostics image tag1cf7fed.
No HTTP request was sent to the preview. QA `/development/status` runs SELECT
current_database(); it was not called because database access is forbidden here.
Backend application/database/session readiness is UNKNOWN; TCP availability is
narrower. No source reconciliation, reapproval or service action was performed.

[Postflight preservation](evidence/nadi-dev-status-runtime-fix-06/preservation.json):
all12 original asset/workbook/controller/selection/runtime/backup hashes match;
known process exe/parent/start identities, unit starts/restarts and source states
match. HTTPS3000 still belongs to3744151. Both sustained disposable units are
inactive/collected. No database/session contents, migration ledger or all35-container
health audit is claimed. Persistence preservation is by non-interaction.

## B — guarded adapter: IMPLEMENTED / DEFAULT OFF

[Tooling and reproducible protocol](../../deploy/development/vendor-maps/README.md).
Explicit opt-in is allowed only in new private FIX-06 disposable roots. Guards
check Node22.23.1, Next15.5.9, Webpack5.98.0, React/DOM19.2.8 and bundled
React19.2.0-canary-0bdb9206-20250818; exact fork/config/loader/core/Flight fingerprints;
constructor identity; unique map plugin; complete expected properties/options;
config mode/cache/devtool/name; root acknowledgment. Unknown/production/ambiguous/
already-mutated configurations refuse before mutation.

Only documented `exclude` is added. It matches complete node_modules path components
before a resource query, preserving app paths containing vendor aliases in queries.
App eval/maps/source contents, native Node maps and existing safeguards remain.
The locked fork returns original vendor module source when excluded, losing vendor
per-module eval wrapping as well as mappings. This is a compound intervention,
not proof that source-map payload alone owns the leak. No React private internals,
installed vendor package or global Node setting is modified.

## C — debugging / functional compatibility

[Actual final qualification](evidence/nadi-dev-status-runtime-fix-06/debugging.json)
passed client error mapping to`app/fix06-debug/Client.tsx:7`, a CDP breakpoint on
that original line, Next client/server original-frame resolution, server native
maps and an actionable React.Children.only error with app callsite atline10.
RSC navigation produced two Flight responses. Three client HMR edit/restore cycles
preserved state/document identity. Debug pages exist only in disposable archives.
Vendor original-source mapping is intentionally lost; generated vendor location,
message and original application callsite remain available. No claim of complete
vendor debugging equivalence is made.

The existing DEV-label workload performed full document reloads in BOTH variants:
80/80 baseline cycles and40/40 candidate cycles. Component Fast Refresh qualification
is separate; full NADI DEV-label HMR-without-reload is **NOT PASS**. No warning or
reload was suppressed, and that existing boundary was not redesigned in this scope.
455 intercepted fixture browser assertions passed login/logout/expiry, review/CAS,
Advisory/ACK UI, states/keyboard,1440/768/390 and dark mode. They do not prove
persistent QA, real grants, HTTPS sessions, engineer UAT or operational acceptance.

## D — sustained comparison: NOT PASS

Same corrected FIX-04 protocol:21-route mix,15s dwell,5s DEV polling,60s HMR,
fictional session read each10 navigations. Sequential runs, one browser each;
Node22.23.1/V8 12.4.254.21-node.56,2048MiB old-space,2500MiB service,200% CPU,
128 tasks,Restart=no. Browser768MiB/200%/192 tasks. Heap/resource/GC observers5s,
allocation sampling512KiB/120s,64MiB/process cap. No forced GC or Flight graph exposure.

Source/PID/start identity, OOM,2400MiB peak and1200MiB host headroom are fail-stop.
New-copy generated restoration/HMR mutations are exact-only; staged/untracked/env
changes refuse. Candidate startup additionally required4500MiB available memory
and clean fixture environment; baseline had ample initial headroom too. Observer
vendor-label checking was corrected before candidate; it changes reporting, not
application behavior. App versions/limits/workload and heap instrumentation match.
Actual counts differ with compilation latency and failed duration. No equal-count,
replicate/confidence interval or live-workload equivalence is claimed.

| Metric | Baseline | Candidate |
|---|---:|---:|
| Requested duration |80min|95min (15min headroom beyond baseline failure)|
| Observed duration |79.85min|39.58min|
| Navigation / status / HMR / session |277 /1222 /80 /27|139 /612 /40 /13|
| Original parent / worker |4102270 /4102290|36554 /36574|
| Guard outcome |worker exit/replacement; confirmed threshold|extra PID95687 alongside original; cause UNKNOWN|
| Heap peak/final MiB |1648.9 /1615.9|560.2 /417.0|
| Kernel cgroup peak MiB |2343.2|1030.5|
| Warm post-major-GC slope MiB/min |+11.211|−0.152 (shorter window)|
| OOM counters / observed V8 abort |0 /none|0 /none|

[Comparison](evidence/nadi-dev-status-runtime-fix-06/comparison.json),
[timelines](evidence/nadi-dev-status-runtime-fix-06/timelines.csv),
[figure](evidence/nadi-dev-status-runtime-fix-06/comparison.png).
Natural GC callback values are observer-time approximations. Overall peaks/slopes
span unequal durations and must not be compared as an80min reduction.
[Common39.575min window](evidence/nadi-dev-status-runtime-fix-06/common-window.json):
baseline peak1110.5MiB versus candidate560.2MiB; warm natural-major slopes+10.324
versus−0.152MiB/min. This supports mitigation during that window, not≥75min stability.

Baseline09:04→10:24WIB: Next warning at10:24:27, unapproved33574 started; first
identity loss stopped the experiment without receipt refresh/retry. Sampled heap
can miss the actual crossing. Locked start-server.js checks used_heap_size >80%
heap_size_limit (~1676.8MiB); exact crossing value is UNKNOWN. Post-replacement
247.8MiB cgroup is not steady state. Restart also cleared vendor/page artifacts;
no fresh terminal baseline map capture exists.

Candidate10:26→11:06WIB: final guard row lists[36574,95687], with original still
present. No threshold message, second server-start sequence, V8 fatal or OOM exists
in retained journal; no preload file for95687 exists. Only cmdline substring was
captured for candidate membership, without extra PID parent/exe/start/listener.
A transient fork/exec child inheriting title/argv is a **hypothesis**, not confirmed
cause. Real generation replacement is **UNKNOWN**. Browser close error follows
fail-stop cancellation, not an independent proven app error. No retry followed.
Metadata capture now records private parent/exe/start/comm/cmdline-hash evidence
for future diagnosis, keeping the SAME rejection rules. It does not admit, ignore
or reapprove extra PIDs and has not been claimed sustained-qualified.

## E — attribution and uncertainty

FIX-05 retained133.7MB source allocations, including59.2MB across four vendor
Script sources, with direct fetch/style paths and conditional WeakMap paths.
Its projection does not implement ephemeron semantics; one owning root remains
UNKNOWN. Current sampling and artifact reduction corroborate a material vendor
execution/map cost, not exclusive retained-byte dominance or root deletion effects.
[Allocation summaries](evidence/nadi-dev-status-runtime-fix-06/allocation-summary.json)
contain overlapping live-sampling stack categories; never sum them as ownership.
Raw profiles stay private. Baseline hit its64MiB profile budget, so later sampling
files are absent; heap/GC metrics continue. Profiling overhead is matched/bounded,
but no new long sampler-off control quantifies feedback into Flight history.
Historical FIX-05 <1% short overhead is not a long-run bound.

[Intermediate candidate artifact counts](evidence/nadi-dev-status-runtime-fix-06/artifact-shapes.json)
show vendor-next2,777,100bytes/0 inline maps and21 application pages retaining map
contents. These counts supplement actual debugging, not replace it. Historical
FIX-05 baseline counts are labelled historical; no deleted baseline artifacts were
recreated or relabelled as new. No late snapshot was forced into the primary trial.

Next measurable work: strengthen/qualify PID attribution with private process-start
and executable/parent/listener evidence; keep uncertain processes fail-closed;
obtain explicit authorization for a NEW sustained candidate run, not automatic
retry. Repeat≥95min and sampler-off/replicate comparison under equivalent protocol.
If retention remains, compare supported vendor-only sourcesContent reduction while
preserving vendor eval, with separate constructor/shape/debugging review. No
speculative React weak-link surgery, raised limits or accepted replacements.

## F — validation, review and release position

70 hermetic controller/confinement/analyzer checks and21 adapter cases PASS;
TypeScript, syntax, lint/build and455 intercepted browser assertions PASS.
Existing hook/Next ESLint-plugin warnings remain recorded. Exact final-head
backend/frontend CI is mandatory and linked in PR delivery. CI cannot override
PARTIAL or the uncompleted candidate duration.

Meaningful findings retained: initial fresh-runner root-confinement failure
(1/230 backend tests), corrected with child-path guard/mock-absent-root regression;
reporter matcher mismatch corrected without changing baseline data; resource-query
false vendor match prevented; candidate ambiguous PID stop and richer future
metadata; terminal baseline artifact loss explicitly unavailable. A postflight
int/string PID-key comparison falsely differed and was normalized before delivery;
raw process identities match. Broad local script batch was rejected by approval
review; reviewed hermetic subset and isolated CI completed safely.

Graph generation2026-08-24 excludes deploy and misses current tests; coverage
checked and exact sources used, no graph-completeness claim. All prior PR75–79,
worktrees, records, backups and assets are retained. No database/session/ledger
reads/writes, source acquisition, collector retry, operational restart, global
Node replacement, freshness change or merge occurred. CI databases are disposable
remote test stores, not persistent QA/operational databases.

No live acceptance plan is justified yet. Resolve the operational review separately,
qualify process attribution and complete the new sustained gate before proposing
an immutable official-controller integration. Any live work requires new explicit
Product Owner authority. Keep this PR DRAFT; do not promote the adapter as fixed.

Technical basis: [Webpack EvalSourceMapDevToolPlugin](https://webpack.js.org/plugins/eval-source-map-dev-tool-plugin/).
Locked-source fingerprints and actual debugger evidence establish version-specific
compatibility; current upstream documentation alone does not describe every Next fork detail.
