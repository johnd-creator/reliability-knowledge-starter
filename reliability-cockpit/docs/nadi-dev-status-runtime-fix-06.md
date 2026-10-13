# NADI-DEV-UX-STATUS-01-FIX-06 — vendor-map mitigation assessment

**IN PROGRESS — no isolated or live acceptance claimed.** This draft checkpoint
will be completed with sustained baseline/candidate evidence and an explicit final
verdict. Short debugging/regression successes cannot establish memory stability.

## Exact scope and runtime review

Base FIX-05 / [PR79](https://github.com/johnd-creator/reliability-knowledge-starter/pull/79):
`63b61d09c45630a76657cdb54991349fb0528e7b`. Branch
`codex/nadi-dev-status-runtime-fix-06`; [DRAFT PR80](https://github.com/johnd-creator/reliability-knowledge-starter/pull/80)
is stacked on FIX-05. Application source, Next application config, locks, backend,
collectors, official controller, databases and operational policies are unchanged.
Only experimental tooling/tests/CI and evidence documentation change.

**OPERATIONAL REVIEW REQUIRED.** Read-only primary inspection on13October2026
found frontend source`f06abce76f8ef9b967ee5b1c2e0802112d77b056`, parent3078556,
worker3744151 and exact generated `next-env.d.ts` dirt (`.next/types/routes.d.ts`
→ `.next-primary-dev/types/routes.d.ts`). The retained journal establishes that
Next replaced historical worker3078570 at03:31:52WIB after warning about the used
memory threshold. Parent/start identity and systemd NRestarts0 survived; that
counter alone misses internal replacements. Active executables are Node25.6.1,
while the retained runtime JSON describes Node22.23.1. No current acceptance or
clean provenance is inferred from matching asset/controller hashes.

QA parent1664250/child1664262 and source
`b348235ce6f82c84873a65344ad2ef5fe276987d` are unchanged and clean at preflight.
Verified TLS1.3 onHTTPS3000 and TCP listeners13036/8000. No HTTP request was sent
to the preview. `/development/status` on QA runs SELECT current_database(); it
was not called because this task prohibits database access. Backend application
readiness/database/session content are UNKNOWN; listener availability is narrower.
No repair, generated-file reconciliation, reapproval, service action or live source
switch was attempted. The operational finding needs separate authorization.

## Adapter and compatibility

[Default-disabled adapter/tooling](../../deploy/development/vendor-maps/README.md)
uses the documented Webpack `exclude` option only in new private disposable copies.
Node22.23.1, Next15.5.9, Webpack5.98.0, rootReact/DOM19.2.8 and bundled
React19.2.0-canary-0bdb9206-20250818 are checked. Fingerprints cover the Next fork,
config base, Webpack loader/core and Flight bundle. Exact constructor, unique map
plugin, complete options/property shape and development config are checked before
mutation. Unknown/production/ambiguous/already-mutated configs refuse.

The matcher selects a complete `node_modules` path component. App source maps,
eval behavior, native Node maps and existing memory safeguards remain. The locked
Next fork returns original vendor source on exclusion, losing vendor eval wrapping
as well as inline mappings. This is a compound vendor intervention, not evidence
that removing map payload alone fixes an owning retainer. No React internals or
installed vendor packages are modified.

Actual disposable debugging qualification passed: client error resolved to
`app/fix06-debug/Client.tsx:7`, a CDP breakpoint hit that original line, Next's
original-frame endpoint resolved client/server application frames, and server
native source maps remained enabled. RSC navigation produced two Flight responses.
Three client edit/restore cycles retained state and document identity. A deliberate
React.Children.only error retained an actionable message and generated location;
vendor original-source mapping is intentionally lost. Synthetic debug pages exist
only in test archives and are not added to NADI application routes.

The existing DEV-label experiment triggers full reloads in the baseline even when
markers update successfully. This is recorded separately from state-preserving
component Fast Refresh; the sustained comparison must not conceal it or call all
HMR behavior PASS. Fixture login/read shapes and455 fully intercepted browser
assertions passed, including logout/expiry, CAS/review/Advisory/ACK UI, response
states, keyboard behavior,1440/768/390 and dark mode. This proves no persistent QA,
real RBAC grant, engineer UAT or HTTPS-session behavior.

## Sustained method — baseline failed, candidate pending

Corrected FIX-04 nav-HMR protocol:21 routes,15s pause,5s DEV polling, HMR once per
minute, one fictional session read each10 navigations. Node22.23.1,2048MiB old-space,
2500MiB service,200% CPU,128 tasks,Restart=no. Browser has separate768MiB/200%/192
cleanup group. Both baseline and candidate use identical heap/GC observers and
512KiB allocation sampling/120s private profiles, capped64MiB/process.
No forced GC or Flight initializer/ancestry instrumentation is used.

Source/PID/start identity, OOM,2400MiB service peak and1200MiB host headroom are
fail-stop checks. Exact generated-file restoration and declared HMR edits apply
only in NEW copies; staged/untracked/env changes refuse. Worker replacement is
never accepted, reapproved or retried. Baseline requested80minutes and failed at79.85minutes on the Next used-heap
threshold. Candidate is requested95minutes to supply15minutes additional
headroom beyond that observed failure; actual duration/counts govern acceptance.
Profile overhead is matched but its long-run causal contribution remains uncertain;
FIX-05's <1% short instrumentation overhead is historical, not a long-run bound.

Natural post-major-GC samples are observer-time approximations. Growth slopes,
heap/RSS/external/cgroup, compiler counts, session/navigation/HMR counts, threshold
distance and worker generations will be reported. Sampled allocation stacks are
not exclusive ownership. FIX-05's conditional WeakMap paths and unresolved root
attribution remain; this experiment does not perform weak-link surgery.

Baseline original worker4102290 exited after4791s; journal recorded threshold
restart and unapproved worker33574. Fail-stop detected the first identity loss and
stopped the disposable units without retry or receipt refresh. 277 navigations,
1222 status requests,80 HMR cycles (all full reloads) and27 fictional session reads
completed; kernel cgroup peak2343.2MiB, heap peak1648.9MiB, OOM counters0.
Warm post-major-GC slope11.211MiB/min. No V8 abort observed.
[Baseline and final debug evidence](evidence/nadi-dev-status-runtime-fix-06/README.md).

## Validation / corrections

Local69 hermetic controller/confinement/analyzer tests PASS; five environment/path
adapter cases plus16 locked-plugin positive/refusal cases PASS. TypeScript, lint,
production build and syntax PASS; one existing EngineeringWorkspace hook warning
and Next's existing ESLint-plugin warning remain.455 intercepted browser assertions
PASS. Exact final-head CI remains required and will be linked at delivery.

Initial CI exposed a confinement bug hidden by the local already-existing private
root: `/tmp/nadi-fix06-private` itself was accepted on a fresh runner. Guard now
requires a child path; a mock-absent-root regression verifies refusal. The first
backend run failed1/230 tests; failure evidence is retained. No baseline runtime
repair/retry was performed. A broad local check-script batch was rejected by
approval review; only individually reviewed hermetic scripts were then executed.
The remaining checks run in isolated CI. No permission blocker is bypassed.

Graph generation2026-08-24 excludes deploy and lacks current diagnostic/test paths.
Coverage checked; exact sources read. No graph-completeness or operational DB/
35-container preservation audit is claimed. Raw profiles, fixture sessions,
screenshots and journals stay private until sanitized evidence selection.

Technical basis: [Webpack EvalSourceMapDevToolPlugin](https://webpack.js.org/plugins/eval-source-map-dev-tool-plugin/).
Version-specific behavior is established by the locked Next fork and actual debugger
checks, not by assuming current documentation exactly describes Next's fork.

## Live proposal

No live acceptance is justified at this checkpoint. Resolve the operational review
through separately authorized work, finish sustained comparative validation and
review final debugging/growth findings before proposing an immutable live candidate.
Any future cutover requires new explicit Product Owner authority. PR75–79 remain
independent and unmerged; this draft grants no merge or deployment permission.
