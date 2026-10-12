# NADI-DEV-UX-STATUS-01-FIX-02 — frontend runtime alignment

> FINAL HANDOFF: BLOCKED after a late Next memory-threshold worker restart. Known-good source/runtime restored; hold merge. See final handoff below.

2026-10-12 WIB. Pre-cutover investigation/implementation checkpoint only. Sustained live acceptance is **PENDING** and must not be inferred from this report or CI. PR #75 frontend candidate remains `5e961b1bfe8ce3c34092613922c3b556de3d74a1`; existing HTTPS3000 remains `f06abce76f8ef9b967ee5b1c2e0802112d77b056`. Backend remains `b348235ce6f82c84873a65344ad2ef5fe276987d`. Main baseline `2e190c2b51fde50e0467d6d5165ebb1060902867`.

## Confirmed evidence and remaining hypotheses

The retained 10:50:21 WIB core identifies SIGTRAP from the Next worker, not a database or Python failure. Journal contains `abort: Lazy deopt after a fast API call with return value is unsupported`. Stack begins at Buffer.byteLength, called by webpack serialization. The installed Node is 25.6.1, V8 14.1.146.11-node.19, Next 15.5.9 and bundled webpack 5.98.0. Worker memory peak was approximately 1.1 GB against MemoryMax=2500M, NODE_OPTIONS heap max=2048 MB; no OOM-kill message appears in retained journal. The destroyed transient cgroup's historical memory.events and exact parent exit status were not retained, so their values are UNKNOWN. Core signal and explicit engine abort support a V8 bailout rather than memory-limit exhaustion.

The exact message is an [upstream V8 bailout reason](https://chromium.googlesource.com/v8/v8/+/ae67ffb8a7543d2d5dc0e5ab0ba491512b3f6362/src/codegen/bailout-reason.h). It does not establish a specific fixed Node issue. Locked Next's next-dev child exit handler returns on a signaled child; this is a plausible reason the parent did not trigger Restart=on-failure, but the original parent exit status is UNKNOWN. Current and candidate used identical runtime/dependency versions and limits; the candidate introduced presentation changes and cold source/cache state. Node25/V8 native-path behavior, cache/workload/JIT timing and their interaction remain hypotheses. Do not label Node25 incompatibility proven.

## Comparative and isolated validation

| Evidence | Node25 | Node22 |
|---|---|---|
| Exact Node | 25.6.1 | 22.23.1 |
| V8 | 14.1.146.11-node.19 | 12.4.254.21-node.56 |
| Next / webpack | 15.5.9 / 5.98.0 | 15.5.9 / 5.98.0 |
| Locked candidate source/dependencies | identical | identical |
| Temporary same-limit navigation/probe duration | 360.4s | 360.5s |
| Successful HTTP requests / initial readiness refusal | 109 / 1 | 109 / 1 |
| Peak sampled cgroup MemoryCurrent | 1131.2 MiB | 1124.3 MiB |
| Sampled CPU usage | 31.2s | 34.2s |
| Abort during comparative probe | none | none |
| Buffer serializer stress | 20,000 iterations PASS | 20,000 iterations PASS |
| Serialized bytes | 918,594,768 | 918,594,768 |
| Stress final process RSS | 197,562,368 bytes | 121,831,424 bytes |

Temporary source copies and loopback probes were automatically stopped; no permanent additional frontend. Application backend bases were non-serving port9; the initial comparison's unchanged development status route still performed existing local factual /health reads. No source system requests, database writes or service mutation. A second isolated Node22 browser/HMR test also replaced that health URL in the **temporary copy only**, making all backend access non-serving. Three fresh Node22 processes and actual HMR marker appearance/restoration without manual reload PASS. Disk cache was initially cold, then reused across process cold starts; these are isolated checks, not the required three official live cold starts.

Meaningful harness failures: git archive exceeded Node's default maxBuffer, repaired with an explicit bounded 64 MiB limit; HMR restoration was attempted immediately during compilation and timed out, repaired by waiting for watcher compilation before restoring. Original source bytes restored; three retests PASS. Neither failure changed production code or runtime.

The original abort was not reproduced in either limited probe. Node22 is therefore an evidence-backed alignment/mitigation proposal, not a proven causal fix. Live sustained testing remains mandatory.

## Focused launcher change

Only frontend-only helper behavior changes. `runtime()` requires a private `frontend-runtime.json`, an absolute canonical non-writable executable, exact SHA256, exact reviewed Node22 patch and V8 versions, and matching shared libnode identity/hash when dynamically linked. A private frontend-node-bin/node symlink binds child node commands to that same binary. Missing/changed pins, Node25, mismatched patch/V8/library, unsafe permissions or alternate child aliases fail before stopping services. There is no system install, PATH discovery or fallback to Homebrew Node25. Frontend start uses the verified absolute binary and a frontend-only PATH; Python/API/collectors are untouched.

Approval provenance records flat node/V8/path/hash/runtime-digest fields alongside the unchanged source/backup/controller compatibility checks. Flat fields preserve the existing approval canonicalization contract; no frontend status or UI source change. Startup/recovery revalidates the pin immediately before starting. Existing shared-source lifecycle remains refused when separate frontend selection is active.

The host already provides `/usr/bin/node-22`, version22.23.1. Its executable SHA256 is `9d9f55f1f4497fe069d681020b728f77221c43b9a4e9576a89ff7cc537caf5cf`; V8 is dynamically linked through `/lib64/libnode.so.127` and is separately hashed. Staged private configuration was verified with the actual binary, but **not installed into the active controller**. CI/Dockerfile use Node22 major; no claim they use this identical patch. Review package/runtime updates explicitly rather than bypassing changed-hash refusal.

35 hermetic lifecycle/pin tests PASS, including failed preflight preserving services, missing pin, Node25/wrong patch/V8, binary/library changes, child fallback, private permissions, startup/recovery and source mismatch. Node22 build and exact-head linked runtime-fix CI are independently recorded after completion. Existing PR75 CI remains PASS; no DEV dropdown redesign or application dependency changes.

## Approval and live acceptance plan

Do not install or cut over until Product Owner explicitly approves the concrete runtime-fix release. Retain the original controller/companion/release metadata and runtime source, private crash/core evidence, QA snapshot and a fresh official backup. After approval, install only the reviewed companion/hash metadata and private pin, leaving the API controller code bytes and system Node unchanged. Run official preflight, then select the exact PR75 SHA through frontend-only controller.

Required live gates still PENDING: three official process cold starts; at least30 minutes continuous stability with repeated factual/Engineering navigation; real HMR with exact-byte restoration and expected transient dirty warning; HTTPS existing QA login/session persistence; 1440/768/390/light/dark/DEV interaction; sampled PID/start count/CPU/RSS/cgroup memory and no abort/unscheduled restart; final clean provenance; official rollback and return-to-candidate check. Normal authentication/security audit additions are recorded and retained; no cleanup of old sessions/QA records. No source GET, operational restart, migration, freshness change or global Node replacement.

A failed live gate must restore the known-good frontend through the existing reviewed recovery procedure and report BLOCKED. Hold merge until sustained acceptance and Product Owner review; no automatic merge. Generated-file reconciliation and late-death recovery CLI improvements remain separate review items, not silently added here.


## Controlled live acceptance — 2026-10-12 final checkpoint

**Runtime acceptance PASS; Product Owner visual review/merge decision remains pending.** This section supersedes the pre-cutover pending state above; historical comparison/hypotheses remain unchanged. Explicit Owner approval authorized only Node22 frontend lifecycle and testing. No automatic merge of PR75 or PR76.

- Serving frontend: `5e961b1bfe8ce3c34092613922c3b556de3d74a1` (PR75 unchanged).
- Installed reviewed helper: `7fd3bdac22788ae1ac31cb8306f283c69384972d` (runtime source; later evidence-only commit does not alter installed helper bytes).
- Backend: `b348235ce6f82c84873a65344ad2ef5fe276987d`; API PID1664250/start unchanged.
- Frontend Node22.23.1, V8 12.4.254.21-node.56, absolute /usr/bin/node-22 and pinned shared library; system-wide Node/Homebrew unchanged.
- Fresh private backup backup-20261012-114549.dump passed ownership/age/archive validation. Original controller/companion/release records preserved before installation. Official preflight PASS.

Three official candidate process cold starts reached readiness at 11:47:23, 11:49:54 and 11:50:34 WIB, server PIDs2798211/2801189/2802093. Actual official rollback to known-good source f06abce76f8ef9b967ee5b1c2e0802112d77b056 reached readiness11:49:19(serverPID2800364), followed by official return-to-candidate. No API/DB/collector start/restart. Disk cache retained; no cleanup to manufacture cold-start success.

Full strict observation: **2026-10-12 11:55:58 WIB → 2026-10-12 12:26:12 WIB**, **1813.65 seconds (120 samples)**, after the last cold start. Main PID2802076 and server PID2802093 stayed unchanged; NRestarts0, no V8 abort/core/OOM or unexpected release warning. Both backends AVAILABLE, exact clean frontend/backend pair explicitly approved throughout. Actual browser navigation soak separately PASS: **1802 seconds, 106 navigations across 14 factual/Engineering routes**, same persistent session, no browser error.

Resource evidence: maximum sampled summed process RSS2342.7MiB; maximum sampled cgroup MemoryCurrent2318.7MiB; kernel MemoryPeak inside the strict window2370.4MiB against2500MiB limit. CPU cumulative at endpoint560.94s; observation delta465.49s (~25.7% of one CPU). Memory events low/high/max/oom/oom_kill/oom_group_kill all0; socket-throttle count46 did not cause observed availability failures. Post-navigation final kernel peak was2407.5MiB, leaving thin resource headroom. This validates the requested bounded interval; it does not prove a leak, constant memory or indefinite stability. Longer memory observation is a recorded follow-up, without raising limits or bypassing safeguards.

Actual live browser regression PASS95 checks: responsive1440/768/390/light/dark, keyboard/outside/Escape/viewport, compact DEV/no banner/full SHAs/helper provenance,21 main routes/fullscreen login, authorized Engineering navigation. Canonical Asset detail followed a real registry link and passed; Engineering QA technical route passed. A case-detail link was not available to the tested subject/UI context; no record ID/scope was invented and that detail is not claimed live-covered. Existing authorized fixture CI covers broader workflows. QA readiness remains separate from engineer UAT/production acceptance.

Actual HMR changed exactly one DEV label and appeared without reload; real dirty state became visibly amber, then exact original bytes were restored and green approved provenance returned. This planned warning is retained in evidence, not suppressed. No HMR source edit remains. Valid HTTPS login used one existing synthetic Engineer account, Secure/HttpOnly cookie and trusted backend subject. Same session survived rollback/return, final cold start and reconnect/30min navigation. No business command/WO mutation/advisory distribution.

Preservation: all93 old sessions intact, one normal login session added (94 total). All1826 pre-existing security activity events and99 local security events preserved;151 normal authorized-read activity events and one successful local login event appended, never erased. Account identities/password hashes/roles/scopes unchanged; only successful-login updated_at and rate-limit attempts/window_start changed through the existing auth flow. Other business records, audit/revision/history, schema/migration ledger unchanged. Exact14-table backup-copy verification,35 container IDs/start/restart counts, API ownership and five original PNG/workbook hashes PASS. No direct database writes/DDL/migration/session cleanup, source acquisition, freshness change or global Node replacement.

Meaningful instrumentation failures retained: the first monitor mistook the existing provenance endpoint's transient /usr/bin/git subprocess for a different Node runtime. Read-only process capture proved only Node22 + git; classification was corrected and the full30min window restarted without frontend retry/restart. A COPY parser misread an empty attachment block; anchored empty-block parsing and aggregate/row retest proved preservation. These were harness findings, not discarded runtime failures. Raw attempts and corrected evidence remain private.

Actual operational/screenshots/session evidence remains private in the existing state archive, with a SHA256/dimension index; it is not committed or replaced by fixtures. Includes nine overview screenshots, three Engineering viewport captures, login, actual HMR warning, registry Asset detail and session/stability/preservation summaries. Existing committed synthetic screenshots keep their original provenance. Final read-only official rollback preflight PASS after sustained observation; retained first recovery record targets known-good source with fresh backup, without disrupting the successful final candidate.

Root-cause calibration: the original Node25/V8 failure location is confirmed, but the exact trigger was not reproduced or proven. Stock Node22 alignment **mitigated the observed preview failure within all requested live gates**. Node25-specific causality remains a hypothesis. Review PR75+PR76 as a coordinated pair; hold production/global-auth activation and engineer UAT separate; no auto-merge.


## Final handoff — late gate FAILED; known-good restored

**FINAL STATUS: BLOCKED. HOLD MERGE of PR75 and PR76.** The bounded30min results above remain valid historical evidence, but they are **not final acceptance**. During final handoff verification, after that window, the required clean/current lifecycle gate failed. Do not describe the candidate as stably accepted or currently serving.

At2026-10-12 12:33:13.471928 WIB, original server PID2802093 logged `Server is approaching the used memory threshold, restarting...`. The Next supervisor retained main PID2802076 and systemd NRestarts0, but the worker changed to PID2847354. Thus systemd restart count alone does not prove worker continuity. This was a framework memory-threshold restart, not an observed Node22 V8 abort or cgroup OOM. The late worker startup rewrote the tracked next-env.d.ts reference to .next-primary-dev, causing real dirty=true/stale=true/UNVERIFIED provenance. Both backends remained AVAILABLE. Final official readiness correctly refused FRONTEND_ONLY_READINESS_FAILED.

No candidate retry or safeguard suppression. Exact late diff/source/process/journal evidence was retained privately. To permit the approved rollback, the entire sole generated-file difference was checked against committed bytes and the known transformation, then restored via the existing narrowly guarded official helper. All other dirty files would refuse. The preserved **pre-test controller companion/release** was explicitly restored; unchanged controller code, Node22 pin/evidence and source worktrees were retained. This intentionally restores the known-good runtime; it is not an automatic missing-pin fallback.

Official frontend-rollback succeeded using the retained first recovery record and fresh backup. **Final serving frontend: f06abce76f8ef9b967ee5b1c2e0802112d77b056, Node25.6.1**, main PID2850832/start12:36:53 WIB. Backend remains b348235ce6f82c84873a65344ad2ef5fe276987d / PID1664250 unchanged. HTTPS3000 operational, both backends AVAILABLE, dirty=false/stale=false/approved pair. No second permanent frontend or global Node replacement. Normal test session and audit additions retained; all pre-existing records/sessions/audit/assets/containers preserved, no cleanup or source/operational/policy changes.

Node22 aligned with CI and avoided the original V8 abort in the observed window, but did **not** complete final runtime/lifecycle acceptance. The new failure mode is confirmed: dev memory threshold → internal worker restart → generated-source dirt → honest provenance refusal. The original Node25 native deopt trigger is still not isolated. Future work must investigate memory/cache/workload behavior with stock safeguards and make worker-generation/generated-file reconciliation auditable; do not merely raise limits, ignore dirty state or disable the memory restart. That follow-up requires a separate controlled plan; this acceptance run stopped after rollback as directed.

Actual Node22 screenshots represent the briefly validated candidate before its late gate failure, not the final serving release. CI may remain green despite BLOCKED runtime readiness. Evidence-only final HEAD is recorded in PR handoff; installed runtime-fix source7fd3bda was rolled back explicitly, candidate source5e961b1 remains preserved. Product Owner review may inspect source/evidence; merge recommendation is HOLD / NEEDS_FIX until sustained handoff remains healthy without unplanned worker restart or integrity drift.
