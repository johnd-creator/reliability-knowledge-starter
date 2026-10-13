# FIX-06 evidence — PARTIAL

Synthetic disposable experiments only; no live/persistent QA acceptance.

- [Comparison](comparison.json), [common window](common-window.json),
  [timelines](timelines.csv), [figure](comparison.png).
- [Baseline](baseline.json): confirmed threshold replacement at79.85min.
- [Candidate](candidate.json): guard stop39.58min, extra PID identity UNKNOWN;
  requested95min NOT completed. No retry.
- [Debugging](debugging.json): original frames/breakpoint/RSC/component HMR.
- [Artifact counts](artifact-shapes.json): intermediate candidate only; terminal
  baseline deleted by framework restart and unavailable, not reconstructed.
- [Allocation stacks](allocation-summary.json): overlapping categories, no root ownership.
- [Preservation](preservation.json):12 hashes and known processes match; existing
  primary dirt/Node25/replaced-worker state still requires operational review.

Raw profiles/journals/cookies and failed private copies remain private. Original
worker heap only; post-replacement cgroup drop is NOT successful steady state.
Conditional WeakMap/ephemeron attribution from FIX-05 remains unresolved.
