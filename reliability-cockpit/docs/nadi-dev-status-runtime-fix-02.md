# NADI-DEV-UX-STATUS-01-FIX-02 — frontend runtime alignment

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
