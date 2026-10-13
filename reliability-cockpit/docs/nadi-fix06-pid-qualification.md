# FIX-06 PID qualification — fast validation

Date: 2026-10-13 (WIB). Status: **PARTIAL — navigation smoke BLOCKED**.
This is isolated diagnostic evidence, not runtime acceptance or a merge recommendation.

## Baseline and scope

- Base: `1e2683a1c730ddcd331910b70372a608256eba9f`, [PR #80](https://github.com/johnd-creator/reliability-knowledge-starter/pull/80), OPEN DRAFT.
- Reviewed main: `2e190c2b51fde50e0467d6d5165ebb1060902867`.
- Branch: `codex/nadi-fix06-pid-qualification`, stacked on PR80.
- Diagnostic implementation: `0caa021a6ac9dd7bd631ceee253653a052461e9a`.
- Disposable application archive retains FIX06's `63b61d09c45630a76657cdb54991349fb0528e7b`; synthetic preparation produces a separate copy SHA recorded per run. It is not the official serving checkout.
- Latest Product Owner instruction cancels sustained testing. No 120-minute run was active when checked; all earlier disposable units had already cleaned up. No sustained test was launched in this task.
- Fast runner now rejects durations outside 60–600 seconds; its observation deadline is requested duration plus 120 seconds, followed by bounded cleanup. Candidate Node 22.23.1, heap 4096 MiB, MemoryMax 6144 MiB, CPU 200%, TasksMax128, Restart=no. Host startup floor8000 MiB, runtime floor1200 MiB, cgroup peak stop5900 MiB. Browser768 MiB. This budget change is explicit PO direction, not evidence of a memory fix.

## Historical PID 95687: UNKNOWN

The retained FIX06 candidate run recorded `[36574, 95687]` at 2374.535625 seconds. Parent36554 and original worker36574 were present. The old scanner selected any cgroup PID whose command contained `next-server`.

For95687, parent, start ticks, executable, exact command, process ancestry and listener ownership were **not captured**. Cgroup membership is supported only by the scanner's cgroup.procs observation. Lifetime is unknown: one observed sample does not establish birth/exit times. No95687 preload file, second server startup or memory-threshold warning appears in retained evidence. These absences do not prove a harmless helper or exclude a replacement attempt. Looking at today's reused PID cannot recover historical identity.

Classification: legitimate temporary child/fork/exec **UNKNOWN**; additional/replacement Next server **UNKNOWN**; unauthorized process **UNKNOWN**. The historical guard stop remains valid; it is not retrospectively reapproved.

## Guard implementation

[process_guard.py](../../deploy/development/vendor-maps/process_guard.py) binds the approved listener inode to exactly one worker and pins parent/worker PID, parent PID, start ticks, executable path/device/inode, command hash, comm, cgroup and systemd invocation. Initial listener must be IPv4 loopback. Both TCP tables are read; missing, ambiguous, shared, extra or changed listeners reject attribution. Membership and process identities are checked twice, including listening-FD ownership consistency. Unreadable/vanished evidence rejects the observation. No retry, descriptor-ignore policy, title whitelist or worker-generation reapproval is used.

An additional process with a Next server title still rejects, even without a listener. Auxiliary commands default to denied. Exact reviewed commands additionally require the original worker as direct parent, verified Node executable, exact cgroup, no listening socket and stable identity; reuse of an observed auxiliary PID rejects.

A fresh fast run captured PID147843 as `/usr/bin/node-22 …/next/dist/compiled/jest-worker/processChild.js`, parent147667, within the disposable cgroup. The failure occurred after the no-listener check. This establishes a different process role from the HTTPS listener; it does not attribute95687.

Locked `next-dev-server.js` explicitly constructs a Jest child for static paths. The runner permits only the exact resolved processChild command after checking SHA256 of processChild, next-dev-server and static-paths-worker; it rechecks hashes during monitoring. This is a source-reviewed role rule, not a discovered-PID allowlist. The actual IPC job module remains UNKNOWN because IPC was not captured. Next server replacements remain forbidden. Hashes are in [process_guard.py](../../deploy/development/vendor-maps/process_guard.py) and each private definition.

## Qualification and failures

Sanitized numeric results: [results.json](evidence/nadi-fix06-pid-qualification/results.json).

| Test | Result |
|---|---|
| Four bounded synthetic HTTPS cases | PASS: exact helper; duplicate Next title refusal; unauthorized listener refusal; replacement identity refusal |
| Local identity/controller/source safety suite | PASS,95 tests |
| Locked vendor adapter | PASS,21 cases |
| First HTTPS observation | Stopped7.18s, unreadable process evidence; no complete attribution |
| Enhanced attribution observation | Stopped7.19s, unverified auxiliary; evidence preserved |
| Initial4GB/6GB fast observation | Stopped9.23s, captured Jest processChild command; rule reviewed afterward |
| Reviewed-helper navigation smoke, requested180s | BLOCKED at117.37s: FileNotFoundError while scanning original worker151056 file descriptors |
| Committed-guard debugging/HMR qualification | PASS,9.26s complete workload; not a60-second stability pass |

The navigation guard held parent151038 and worker151056 for108 successful samples before a descriptor closed during scanning. Strict unreadable-evidence handling stopped the experiment. Six navigations,30 status requests and two DEV HMR edits were observed; both edits caused full reload, matching previous behavior. Browser cancellation followed guard cleanup and is not an independent application crash. Heap peak411.33 MiB, RSS peak730.90 MiB, cgroup peak773.42 MiB, CPU28.52s; sampled OOM counters zero and no journal V8 fatal error. These values do not establish retained-heap steady state.

The separate debugging qualification used parent156375/worker156469, eight monitor samples and three Client HMR cycles with state and document identity preserved. Client/server original frames, an application breakpoint, actionable vendor error, native source maps and two RSC responses passed. Cgroup peak691.95 MiB, heap281.51 MiB, RSS472.95 MiB, CPU10.67s, sampled OOM counters zero. This validates debugging safeguards only. It does not turn the failed navigation smoke into PASS or prove all routes/session behavior.

The fail-closed collector still encounters normal descriptor-lifetime races. A future change needs a stable, auditable listener-ownership collection strategy, with permission failures and lost process identities still rejected. Blanket ignoring disappearing descriptors is not approved by this change. No further experiment is scheduled.

## Operational review and preservation

Official frontend remains `f06abce76f8ef9b967ee5b1c2e0802112d77b056`, parent3078556/listener3744151. Actual executable is Homebrew Node25.6.1 while retained runtime configuration pins `/usr/bin/node-22`22.23.1. Journal confirms historical internal worker replacement at2026-10-13 03:31:52WIB after the memory-threshold warning; Ready03:31:54. Systemd NRestarts0 does not rule out an internal child replacement.

The serving checkout still has exactly the known generated next-env.d.ts reference change from `.next/types/routes.d.ts` to `.next-primary-dev/types/routes.d.ts`. It was inspected, not repaired. **Operational review remains required**; no official HTTP page/status request was made.

QA backend source remains `b348235ce6f82c84873a65344ad2ef5fe276987d`; parent1664250/child1664262, clean checkout. Both official units retained exact invocation, PID/start identity and NRestarts0 across task checks. Twelve hashes match before/after: five original PNGs, workbook, two private controllers, three runtime manifests and existing backup. Database/session contents were NOT accessed; no content-health or all35-container claim is made.

Official units were not stopped. Only owned disposable units and browser companions were stopped via the runner cleanup: candidate-f51851, candidate-e7882f, candidate-98fdd3, candidate-73e924, candidate-f73fbc, and four `nadi-pid-qual-*` synthetic fixtures. Final inventory shows no remaining loaded disposable units. Fixture processes also terminated. No worktree, backup or evidence was deleted; no application, collector, database, migration, session, account, freshness policy or operational configuration was changed.

Private originals remain in `/tmp/nadi-fix06-private/` under new `pid-*` output directories and `/tmp/nadi-pid-qual-private/`. They include definitions, private process commands, numeric metrics, heap/GC observations, browser results, journals, certificates and preservation checks. Never publish raw command attribution or private keys. PR75–80 remain untouched.

## Validation and next gate

Exact-head backend/frontend CI is reported in the follow-up PR checks and delivery message; local checks do not imply CI success. Markdown links, JSON, syntax and diff checks are required before delivery. Original application/frontend/backend files and official controllers have no branch diff.

The prior ≥95-minute matched baseline/candidate protocol is **superseded, not authorized and not scheduled**. If separately requested later, freeze identical app/dependency/source hashes, Node22.23.1,4GB/6GB budgets, synthetic records, navigation counts,15s dwell,5s polling,60s HMR and instrumentation policy; pin listener/parent identity once, log helper attribution separately, stop at the first unverified identity/resource/source failure, and clean up only owned units. Do not compare this higher-budget fast run directly with the prior2GB/2.5GB sustained runs as a causal memory result.

Current next action: review the collection-race blocker and isolated guard patch. Fast navigation acceptance and operational runtime acceptance remain unproven. No live cutover, merge or sustained rerun is authorized by this report.
