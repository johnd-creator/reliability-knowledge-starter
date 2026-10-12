# NADI-DEV-UX-STATUS-01-FIX-05 — retainer attribution and assessment

**PARTIAL — NEEDS FURTHER INVESTIGATION.** Module-source retention and contributing
mechanisms are measured. A single owning retainer and a sustained safe remedy are
not established. No application fix, deployment or runtime acceptance is claimed.

## Baseline and boundary

- Exact FIX-04 base: `ef70aa6f2dc21866bbbd6de73f1db30ad4ab286a`, verified remote
  branch `codex/nadi-dev-status-runtime-fix-04`; [PR78](https://github.com/johnd-creator/reliability-knowledge-starter/pull/78)
  remains OPEN/DRAFT. Its exact-head backend/frontend CI passed historically.
- Verified main: `2e190c2b51fde50e0467d6d5165ebb1060902867`.
- Isolated branch: `codex/nadi-dev-status-runtime-fix-05`. Final immutable HEAD,
  draft PR and exact-head CI are recorded at delivery. This is a stack on FIX-04,
  not a merge into main and not a live frontend candidate.
- Official configured frontend source: `f06abce76f8ef9b967ee5b1c2e0802112d77b056`;
  QA API source: `b348235ce6f82c84873a65344ad2ef5fe276987d`.
- Preflight already observed primary parent3078556/worker3744151 (different from
  FIX-04 historical worker3078570), and existing `next-env.d.ts` dirt. QA API
  PID1664250/source were clean. This is pre-existing drift, not repaired or
  explained by FIX-05. No live HTTP/browser request, login or integrity acceptance
  was performed. A configured SHA is not a new browser serving-SHA validation.

Official controller, frontend/backend worktrees, backups and original assets were
not modified. No DB/session/schema/migration-ledger comparison, container inventory,
source GET, collector retry, restart, cutover or Phase1 policy action was attempted.
Postflight [host file/process attestation](evidence/nadi-dev-status-runtime-fix-05/preservation.json) confirms all12 asset/controller/backup hashes match, primary parent3078556/worker3744151 and QA parent1664250/start times/restart counts unchanged, and both source SHAs intact. The primary generated-file dirt remains. A sandbox-only /proc visibility failure was corrected through host metadata; no API drift was established.

Persistent QA preservation is by non-interaction; fresh DB contents/35-container
health are **NOT VERIFIED**, explicitly outside this scope.

## Method and privacy

Node22.23.1 (`/usr/bin/node-22`, SHA256
`9d9f55f1f4497fe069d681020b728f77221c43b9a4e9576a89ff7cc537caf5cf`),
V8 `12.4.254.21-node.56`, Next15.5.9, Webpack5.98.0, root React19.2.8 and Next bundled
React19.2.0-canary-0bdb9206-20250818. Locked Flight bundle fingerprint:
`f5642afec1b380029730444582c0af19300709dcb586f91c96cb002fc8bffddb`.

Fresh archived copies of ef70 use in-memory fictional backends and sessions, clean
environments, explicit fake Git/compatibility identities and bounded temporary HTTP
loopback workers. Fake approval receipts are not official release approvals.
[Tooling](../../deploy/development/retainers/README.md) records reproducible commands.
No shared dependency files were patched. Experimental changes exist only in copies
or disposable process memory. No original PNG/workbook/operational .env was changed.

Next old-space2048MiB/cgroup2500MiB/CPU200%/Restart=no remain. Fail-stop monitors
worker, parent, start ticks, source, OOM, peak>2400MiB and host headroom<1200MiB.
The browser has a separate768MiB scope and cleanup. Snapshot preflight requires
heap<=550MiB, cgroup<=1300MiB, host available>=3000MiB; file<=384MiB/60s.
Analysis has1500MiB/180s/200% CPU bounds, <=4M nodes/20M edges/2M strings and strict
V8 schema checks. Raw evidence is private (0700/0600); output is numeric/allowlisted.

The final analyzer uses tested dominators and shortest paths on edges excluding
weak/non-root shortcut edges. **It does not simulate WeakMap ephemeron key/value
conditionality.** Projected dominance cannot prove deletion effects on the actual
GC. A console→WeakMap→Viewport path is conditional, unlike the direct global.fetch
or style closure paths. Largest string names are elided by V8 to1024 characters:
absence of an inline-map marker is not absence of payload. Self bytes remain
measured. Native buffers are included in snapshot self bytes; those differ from
V8 heap, RSS and cgroup memory. Nested dominator rows must not be summed.

## Retainer evidence

The successful terminal12-navigation baseline snapshot is282,114,191 bytes,
SHA256 `e768ee526b618c32a4bc975e8f67cc44ae0158a790886121e8f3b10860d6acc6`.
Capture7287ms, pre-heap391,882,976/post-heap387,707,712 bytes; cgroup rose to roughly
2205MiB. This sizable observer cost is not an application growth slope.
The analyzer processed3,114,843 nodes/11,816,313 edges in a bounded~7s run,
peak~591MiB. [Numeric paths/dominators](evidence/nadi-dev-status-runtime-fix-05/retainers.json).

| Mechanism | Measured result | Interpretation |
|---|---|---|
| Large module/source-content strings | 133,729,208 self bytes; >=64KiB selection | Actual allocations; not total heap or all small source strings |
| `Webpack.vendor.next` Script generations | 4 distinct sources,59,193,248 bytes | Multiple compiled generations survive at checkpoint |
| Source-map URL strings | 8 large strings,2,116,632 bytes | Separate URLs; embedded payload portions cannot be split from elided source text |
| Flight pendingOperations Map | 34,441,872 projected dominated bytes;0 exclusively dominated source/URL bytes | Owns substantial metadata; zero projected exclusivity does not exonerate it under ephemeron semantics |
| Own-property previous/awaited chains | 86 entry candidates;186,271 ancestry objects | Distinct from V8 lexical Context.previous; restricted non-prototype traversal reaches source strings |
| Node source-map-cache candidates | 7,599,552 projected dominated bytes, including3,242,760 source bytes | Lower-bound exclusive graph accounting, not all module-owned map payload |
| Webpack Compiler/Compilation/ModuleGraph/GC-cache objects | 4,911,344 projected dominated bytes;0 exclusive source bytes | Material but not the majority of checkpoint bytes |

Direct strong shortest paths include:

```text
GC root → global.fetch → shared function → Script → vendor Script → source
GC root → global._N_E_STYLE_LOAD → shared function → Script → source
GC root → console.dirxml → wrapper context → lexical previous context
        → jsxPropsParents WeakMap → conditional value → Viewport → Script → source
GC stack root → require.cache → Module/exports/functions → Script → source
```

The fetch/style paths independently support retention of two large source versions.
The WeakMap path needs key attribution before assigning ownership. Flight ancestry
can reach allocations through real own-property chains, even after filtering
prototype/constructor/native-context/object-shape traversal. That is stronger than
an allocation-stack observation, but still not exclusive retained-byte dominance.
Multiple roots and conditional edges prevent naming one deletable owning root.

## Controlled comparisons

All final full-GC trials: **6 navigations,18 status reads at5s cadence,2 HMR
change/restore cycles,1 fictional session read**, same fixture data/Node/limits.
Automatic widget polling is disabled equally; browser closes before checkpoint.
Node's experimental `v8.queryObjects(Object,{format:'count'})` forces full GC and
returns only a current-realm count. Warnings remain recorded. This does not provide
retainer graphs for controls and does not replace a75-minute stability trial.
Wall time~122–127s reflects natural compilation variation. One run/mode: exploratory,
no confidence interval or long-run instrumentation bound.

| Control | Post-GC heap MiB | External MiB | Heap change |
|---|---:|---:|---:|
| Minimal baseline |326.33|102.14|—|
| Sampling512KiB/120s |327.52|102.15|+0.37%|
| Sampling + read-only Flight graph |327.69|102.12|+0.42%|
| Node source maps OFF, disposable only |306.98|102.35|-5.93%|
| Eval/map plugin removed, disposable only |223.50|54.50|-31.51%|
| Webpack memory cache maxGenerations1 |441.68|107.43|+35.35%|
| Eval/mappings kept, noSources=true |286.20|70.53|-12.30%|
| Vendor-only source-map exclusion |255.37|65.74|-21.75%|

All eight completed with one original worker, OOM-kill0, no V8 abort, provenance
failure or browser exception. HMR markers and fictional session reads passed.
[Exact settings/CPU/RSS/peaks](evidence/nadi-dev-status-runtime-fix-05/comparison.json),
[timelines](evidence/nadi-dev-status-runtime-fix-05/timelines.csv),
[figure](evidence/nadi-dev-status-runtime-fix-05/comparison.png).

Node maps contribute to retention but most heap remains. Instrumentation added
<1% at this short matched checkpoint; impact on the prior75-minute experiment is
UNKNOWN. Removing the eval/map plugin changes execution as well as maps: its31.5%
reduction cannot be attributed to payload alone. The noSources control retains
337 vendor map comments/338 eval text occurrences, removes embedded content and
reduces heap/external bytes. It establishes a payload contribution without removing
the eval pipeline, though debugging content is degraded.

Vendor exclusion removes vendor maps (337→0) while all eight emitted application
page files retain their map/comment/embedded-content counts. The Executive page
retains28 maps with embedded content/29 eval text occurrences. Node native maps
remain enabled. [Artifact shapes](evidence/nadi-dev-status-runtime-fix-05/artifact-shapes.json)
are counts, not proof of original-frame/debugger resolution or functional UAT.

## Failed attempts and limitations retained

1. Initial12+24 snapshot calibration produced a valid12-step267MiB snapshot, then
   crossed the2400MiB observer budget (~2455MiB). Immediate disposable stop; no OOM
   or retry of that protocol. Not a sustained baseline PASS.
2. A24-step terminal capture was refused with host available below3000MiB. A later
   uninstrumented12-step capture succeeded; both captures and the calibration
   snapshot have hashes in the [private inventory](evidence/nadi-dev-status-runtime-fix-05/private-evidence-inventory.json).
3. Sampled12-step captures were refused at the unchanged headroom threshold,
   including after browser release. Serial controls stopped automatically. No
   matched retainer-snapshot matrix is claimed.
4. Inspector collectGarbage checkpoint timed out. A strong-session-reference
   hypothesis did not resolve a tiny qualification; cause is unconfirmed and the
   API was abandoned. Supported full-GC/count qualification passed before the new
   cohort. This is a harness failure, not a proven Next/V8 application cause.
5. Initial known-answer fixture schema was accidentally shared between tests;
   deep copying corrected the test contamination. Random set-oracle/cycle/weak-edge,
   privacy, URL and ancestry tests now pass. No application change was involved.

## Ranked remediation assessment / FIX-06 proposal

1. **Guarded vendor-only map exclusion: best isolated implementation candidate.**
   A documented Webpack option, supported by the exact Next15.5.9 fork, measured
   -21.75% heap while retaining application map contents. Use the existing public
   Next webpack hook, exact-version/plugin-shape fingerprint guards, preserve Node
   maps/eval and application maps. Selecting the Next fork is version-sensitive;
   debugging/vendor stack quality and sustained slope remain unverified. This is
   mitigation evidence, not proof of the root leak being fixed.
2. **Upstream framework correction:** prefer an official reviewed Next/React fix
   for retained debug ancestry/module lifecycle. React [draft37134](https://github.com/react/react/pull/37134)
   is not a released compatible change to this locked bundle. RSC/Flight/HMR,
   original frames and session behavior require isolated migration/regression.
3. **noSources everywhere:** measured payload benefit, but app source contents
   disappear. Reject as a default without a debugging compatibility strategy.
4. **Node maps OFF / whole eval plugin OFF:** useful controls; reject as unreviewed
   global remediation because diagnostics are degraded and root retention remains.
5. **Memory-only cache:** reject this tested maxGenerations1 variant; heap+35% and
   current-realm objects nearly doubled. It is not an evidence-backed fix.

Reject higher limits, weaker fail-stop guards, accepted worker replacements,
unregistering globals/async hooks, manual require-cache surgery and speculative
private React previous/awaited weak-link patches. FIX-04's failed weak-link evidence
is preserved. No option was applied to the official runtime.

A specific **FIX-06 isolated implementation proposal** is supported for option1:
create a separate opt-in/version-guarded development adapter for vendor-only mapping
exclusion; add emitted app-map/original-frame and RSC/Flight/HMR/session/provenance
regression; repeat matched baseline/candidate >=75min with identical counts and
bounded ephemeron-key/retainer evidence. Require no worker replacement and declining
or bounded post-major-GC retention before recommending a live test. Keep it disabled
by default; any official activation needs separate Product Owner authority. If app
frames/debugging or long-run retention fail, reject the candidate. Do not treat this
proposal as safe runtime acceptance or claim that all owning roots are resolved.

## Validation and governance

66 controller/confinement/analyzer checks PASS, including40 seeded random graphs
against a set-dominator oracle, cycles, shared/weak alternatives, strict schema,
private output, exact HMR/source validation, URL/privacy and ancestry checks.
C++17 `-Wall -Wextra -Werror`, JS syntax and git diff --check PASS. Exact-head
backend/frontend CI (TypeScript, lint, build, contracts/security/browser regression)
is mandatory and recorded in the final PR delivery. CI cannot override PARTIAL.

Graph generation2026-08-24 is stale; deploy is excluded and new tests missing.
Coverage checked, exact source used; no graph-completeness claim or reindex.
Only diagnostic tools, tests, CI syntax/test inclusion, this report/evidence and an
append-only DEV-LOG entry change. Application/backend/collector/operational configs
and dependency locks remain identical to ef70.

Technical basis: [Node22 V8 snapshot/GC APIs](https://nodejs.org/download/release/v22.23.1/docs/api/v8.html)
(snapshots block and require substantial extra memory), [Webpack eval-map options](https://webpack.js.org/plugins/eval-source-map-dev-tool-plugin/)
(noSources/exclude and eval semantics), [Webpack cache](https://webpack.js.org/configuration/cache/),
and [Next memory guidance](https://nextjs.org/docs/app/guides/memory-usage).
These documents guide compatibility assessment; local locked-source checks and
measurements establish this report's evidence. No policy extension or merge.
