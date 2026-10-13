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

## QUAL02 — stable listener evidence collection (2026-10-13)

**PARTIAL: descriptor correction exercised successfully; single navigation smoke BLOCKED.** This checkpoint follows the original PR81 evidence above without replacing its historical results. Base `ebc42d1422f4bda197e339f859713c5af8c2d151`; implementation `96720d2b614bc4aed9623a6f23b144ee10f4a3a5`. [Sanitized results](evidence/nadi-fix06-pid-qual02/results.json).

The original 117.37s failure was a descriptor collection failure, not an established Next crash, leak or replacement. `process_guard.py` now separates identity reads from FD collection. A descriptor-specific ENOENT creates an explicitly incomplete observation; no descriptor is skipped and no partial view is returned as verified. A maximum of three complete acquisitions may be attempted within250ms, with10ms pauses. Retry requires unchanged approved parent/worker identities, a still-readable identity for the affected process, a reviewed role, the original listener inode still present, and no observed unauthorized listener. Permission errors, missing process identity, changed membership, changed listener, unknown role and identity changes remain terminal. Every accepted fresh view must pass the original full listener/ownership checks and service identity checks before and after collection. The exact source-hashed Next Jest rule remains unchanged. Historical95687 remains UNKNOWN.

Pre-smoke validation passed111 safety/controller tests, including16 added deterministic collection regressions: transient non-listener FD closure, repeated failure, listener disappearance, PID replacement, unauthorized sockets, identity/invocation changes, permission denial and missing metadata. The runner exits nonzero after guard failure. Navigation is now limited to60–180 seconds, with270s lifetime and10s stop limits on owned disposable units; no long experiment is permitted.

Exactly one smoke was launched, requesting180 seconds of navigation on synthetic HTTPS fixtures with Node22.23.1,4096 MiB heap and6144 MiB MemoryMax. Parent270037 and worker270055 remained the only accepted serving identities. Worker start ticks `70591852`, executable `/usr/bin/node-22`, invocation `9b061897fb584d5b827b23bde2efc04a`, listener inode `39494069`, endpoint `https://127.0.0.1:53189`, disposable unit `nadi-fix06-disposable-candidate-e2f5a6.service`. The application archive remains63b61d09 (full SHA in numeric evidence), separate from the guard commit.

Two descriptor observations (23 and40) were marked incomplete and recovered on attempt2 with complete fresh evidence. All134 accepted samples report complete=true. This exercises the specific collection correction without turning the incomplete reads into verified observations. The descriptors' prior types were not recorded; the non-listener closure case is established by deterministic fixtures, not guessed from these descriptor numbers.

The **first terminal failure** occurred at140.185934 seconds: `UNREADABLE_PROCESS_EVIDENCE` for additional PID273851, identity stage, FileNotFoundError. Both approved processes were readable in the partial capture; PID273851's command, start identity and role were unavailable. It remains UNKNOWN and was not assumed to be a Jest helper. The application was not retried. Browser cancellation followed cleanup, not an independently established application crash. No worker replacement, memory leak or V8 crash is inferred from this failure.

Observed browser coverage: eight navigations,37 status requests, two DEV HMR cycles (both full reload), synthetic HTTPS login. The requested navigation interval and final responsive screenshots did not complete. Peak cgroup849.41 MiB, worker RSS808.68 MiB, worker heap503.37 MiB; CPU36.03s. Sampled OOM counters remained zero and the retained journal contains no V8 fatal error. These short measurements do not establish sustained stability or heap steady state.

Owned frontend/browser units and in-memory fixture were cleaned up; no disposable unit or listener remained. Twelve preserved-file hashes and four official process identities matched before/after. Official generated next-env.d.ts dirt remained unchanged; QA checkout remained clean. No official page/status request, database/session access, source GET, collector action, controller installation, restart, policy change or merge occurred. Private evidence remains `/tmp/nadi-fix06-private/pid-qual02-navigation-01` and `/tmp/nadi-pid-qual02-private`; earlier artifacts and worktrees are retained.

Exact-head CI is recorded in PR81 checks and delivery. Current next gate is review of the unreadable additional-process evidence; it must not be hidden by broader retries or role assumptions. No second smoke, sustained test or live cutover is scheduled.

## QUAL03 — process lifecycle qualification (2026-10-13)

**PARTIAL:124 deterministic/safety regressions PASS; single navigation smoke BLOCKED.** Base `34e7f5af489860f2a727de725152f73914aa34ba`; tested implementation `a1ff79722a181a3247c346c9b78e259d00186244`. [Numeric evidence and separate outcomes](evidence/nadi-fix06-pid-qual03/results.json).

The deterministic lifecycle cases model an auxiliary process disappearing after cgroup enumeration but before identity reads. Diagnostics distinguish `UNREADABLE_APPROVED_PROCESS`, `TRANSIENT_MEMBERSHIP_UNVERIFIED`, and `UNAUTHORIZED_OR_REPLACED_WORKER`. These are refusal categories, not claims that Next crashed or a replacement conclusively occurred. Original reason codes remain available. Permission errors and other unverified states also stay blocked. Parent/worker PID, start ticks, executable identity, cgroup, invocation, listener ownership, exact reviewed helper policy and source integrity remain mandatory.

A membership gap permits **one fresh diagnostic snapshot**, within250ms, against the existing pinned guard. A complete fresh view can describe the current primary only; it cannot verify a process that already vanished or close the historical gap. The original failure is always raised with acceptance=false. An unreadable approved PID does not enter this diagnostic retry. Second-pass identity reads now preserve failure context. Tests cover disappearance, membership changes, fresh failure, PID reuse, foreign listener, invocation changes and exhausted budget; independent browser-failure tests prevent attestation errors from hiding actual browser assertions.

Exactly one disposable HTTPS smoke followed the passing tests. Requested navigation120s, Node22.23.1, heap4096 MiB, MemoryMax6144 MiB; owned units have160s runtime and5s stop limits. Parent319071, worker319089, worker start ticks `70828970`, listener inode `39686908`, endpoint `https://127.0.0.1:42563`, invocation `acbe61fa7dac474fb6fe95790bceab9a`, unit `nadi-fix06-disposable-candidate-9fbe4b.service`. All74 accepted samples used the same worker and complete evidence.

The first terminal failure at78.859085s was unavailable identity evidence for PID321420 (FileNotFoundError). Its role/lifetime are UNKNOWN. The fresh diagnostic itself encountered `CGROUP_CHANGED_DURING_READ` and remained UNVERIFIED; it did not produce an accepted observation. No fourth iterative smoke repair, application retry or additional test runtime was launched.

Process attestation: **BLOCKED / TRANSIENT_MEMBERSHIP_UNVERIFIED**. Browser-functional result: **INCOMPLETE_INTERRUPTED_BY_ATTESTATION**, with five completed navigations,21 status requests, one completed DEV HMR/full reload, no recorded page errors, and the next HMR interrupted by cleanup. Browser cancellation does not establish an application crash. Overall acceptance is BLOCKED even if a browser check passes independently. This distinction is saved in `outcome.json` after cleanup, including startup failures; it does not reinterpret incomplete coverage as PASS.

Peak sampled worker heap508.32 MiB, RSS840.46 MiB, cgroup845.32 MiB; CPU24.35s. Sampled OOM counters zero; no retained journal V8 fatal error. This short interval does not establish leak remediation or sustained stability. Historical PID95687 and273851 remain UNKNOWN; no current PID was used to infer either historical role.

All owned disposable frontend/browser/fixture processes stopped. Twelve file hashes and four official process identities matched before/after. Official runtime/controller, persistent QA database/session, collectors, policies, backups and other worktrees were not changed. No official HTTP request or database/session read occurred. Private evidence remains `/tmp/nadi-fix06-private/pid-qual03-navigation-01` and `/tmp/nadi-pid-qual03-private`. Exact-head CI is maintained in PR81 checks and delivery.

### Proposed different collection architecture — not implemented or authorized

Further adjustments to polling/retry timing cannot reconstruct a short-lived, reaped process's identity. A pidfd provides a task reference and pollable lifecycle information, but opening one after a process disappears can fail; it does not recover past executable/role evidence. Reaping conditions matter. [Linux pidfd_open manual](https://man7.org/linux/man-pages/man2/pidfd_open.2.html).

Proposed next design: arm a bounded **fork/exec/exit event journal before starting a new disposable unit**, then correlate birth/exec identities with sampled listener ownership. Evaluate kernel tracepoint/eBPF capability for a single owned disposable cgroup, using a gated launch so early events cannot precede observer readiness. Actual event availability and required permissions need a separate capability review. Linux documents event tracing and an available-events interface; host support is not established by this report. [Kernel event tracing](https://docs.kernel.org/trace/events.html).

The proposed journal would identify processes by boot/process namespace, cgroup generation, PID and birth time; record parent linkage and executable/known-module identity at exec; and record exit before metadata disappears. Use pidfds for the approved parent/worker and eligible observed children while alive. A trusted source-reviewed spawn receipt could provide the expected helper module identity; an unknown module is not approved merely because it executes Node. Preserve exact listener inode/sole ownership, initial worker generation, source hashes and the4GB/6GB limits. No worker replacement is automatically reapproved.

The next collector must expose dropped events, startup gaps, overflow, cgroup/PID reuse, unknown exec/module and permission failures as incomplete attestation. Retain only bounded private metadata (no environments, credentials, session content or general operational argv). Filtering must cover only the owned experiment; do not enable global tracing, install a daemon, or attach to the primary service under this task.

Required qualification before any further application run: deterministic short-lived fork/exec/exit replay, lost-event/overflow tests, PID/cgroup reuse, unauthorized listener, approved-worker death/replacement, source/receipt mismatch and observer failure. Compare instrumentation overhead in matched disposable controls. Privileged event tracing, capability changes and another runtime experiment require a separately approved task. This is a reviewable proposal, not a scheduled execution or a claim that event collection is already safe on this host.
