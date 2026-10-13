# FIX-06 vendor-map mitigation experiment

Default OFF. No application config or official launcher imports this adapter.
`adapter.cjs` accepts an explicit opt-in **only** inside a new FIX-06 disposable
archive. It checks Node22.23.1, Next15.5.9, Webpack5.98.0, React19.2.8, bundled
React19.2.0-canary-0bdb9206-20250818, exact fork/config/Flight fingerprints,
constructor identity and complete expected plugin/options shape. Unknown,
duplicate, already-mutated or production configurations refuse before mutation.
Only the documented plugin `exclude` option is added, matching a complete
`node_modules` path component. Application eval and full source maps stay enabled;
Node native source-map handling is not changed. Vendor modules lose their eval
wrapper as well as inline map under this locked fork: this is an explicit
compatibility cost, not a payload-only causal intervention.

```sh
python3 deploy/development/vendor-maps/run.py \
 --repo /absolute/repository \
 --deps /absolute/existing/locked/node_modules \
 --output /tmp/nadi-fix06-private/new-baseline \
 --mode baseline --seconds 4800 --sampling
# Separately run the identical protocol with --mode candidate and a NEW output.
# Debugger qualification uses --debug --seconds 120 on a separate disposable copy.
```

The corrected FIX-04 workload cycles21 routes with15s dwell, existing5s DEV
polling, one HMR edit/restore per minute and a fixture session read every10
navigations. Actual completed counts are recorded, not presumed identical.
`hmrReloads` records document replacement separately from a successful marker
update. No real QA identities, sessions, source data or database are involved.
Raw CDP/debug data remains local. Debug pages exist only in archived test copies.

Limits remain2048MiB old-space,2500MiB service,200% CPU,128 tasks,Restart=no.
Before starting, host available memory must be >=4500MiB. Fixture/Next/browser
environments are explicitly clean; no operational env file is loaded.
Browser cleanup group has768MiB/200% CPU/192 tasks. Fail-stop on parent/worker/start
identity change, source drift, OOM,2400MiB peak or <1200MiB host available memory.
Generated-file restoration applies only to the exact known bytes in the NEW copy.
No active worktree reconciliation is authorized. All units are temporary and
removed by systemd after stopping; all evidence/copies are retained.

Heap/RSS/external/space counters and natural GC observer metrics are sampled at5s.
Optional allocation sampling is512KiB with120s snapshots capped64MiB/process;
matched experiments use the same option. No forced GC, Flight graph exposure,
private React changes, raised limits or accepted replacement workers. Natural
post-major-GC measurements are observer-time approximations, not exclusive retained
byte accounting. Allocation stacks never prove a root's exclusive ownership.

Run `adapter.test.cjs` directly with Node (not via a system-wide Node change).
`NADI_FIX06_TEST_DEPS` optionally enables16 real locked-plugin refusal/positive
cases when the executable is exactly22.23.1. Otherwise only the five environment
and path matcher tests run; no positive locked-version PASS is implied.

`debug.mjs` proves actual client error-to-original-line mapping, a CDP breakpoint,
Next client/server original-frame resolution, native source-map enablement,
RSC navigation and3 state-preserving client HMR cycles. A deliberately triggered
React.Children.only error must retain an actionable message and location. Vendor
original-source mapping is intentionally unavailable and must be disclosed.
The large existing fixture browser suite separately tests authorization/session UI
semantics; neither synthetic suite proves persistent QA or operational UAT.
