# FIX-05 disposable retainer diagnostics

This controller never invokes the official NADI launcher. It archives the exact
FIX-04 commit into a **new** private `/tmp/nadi-fix05-private/` directory, uses
in-memory synthetic backends, and serves a bounded temporary HTTP loopback worker.
It must not be pointed at HTTPS3000, real sessions, an operational API or database.
The fake approval/worker identities are explicitly disposable, not release evidence.

Requirements: verified `/usr/bin/node-22` 22.23.1, locked Next 15.5.9/React 19.2.8
dependencies, existing Playwright, systemd user scope and `g++`. No installation,
system-wide Node replacement, application patch or operational permission is implied.

```sh
python3 deploy/development/retainers/run.py \
  --repo /absolute/repository \
  --deps /absolute/existing/locked/node_modules \
  --output /tmp/nadi-fix05-private/new-unique-trial \
  --mode minimal --capture gc
```

Every final matched trial performs 6 navigations, 18 explicit status reads at 5s
cadence, 2 change/restore HMR cycles and 1 fictional session read. Automatic widget
polling is disabled equally in all copies. The browser closes before the checkpoint.
Modes: minimal; allocation sampled (512KiB, 120s); sampled plus hash-guarded
read-only Flight ancestry exposure; Node native source maps disabled; Next's
`EvalSourceMapDevToolPlugin` removed; memory-only Webpack cache with maxGenerations=1; eval maps retained with noSources; vendor-only map exclusion.
The last five are **experimental controls**, not approved remediation settings.
Next normalizes `devtool=false` while separately installing its eval-source-map
plugin: setting devtool false alone does not establish that maps were disabled.
Effective plugin/cache and native-source-map state must be checked in each result.

`--capture gc` uses Node's experimental `v8.queryObjects(Object,{format:'count'})`
for a full-GC checkpoint; the count belongs to the current realm, not all objects.
It returns no object values. Its warning is retained, not suppressed. An attempted
Inspector collectGarbage checkpoint timed out and was abandoned; its cause is
unconfirmed. `--capture snapshot` writes a private snapshot only if heap <=550MiB,
cgroup <=1300MiB, host available >=3000MiB. It never relaxes those checks. Earlier
12/24-navigation protocols are calibration/history, not silently pooled with the
final 6-navigation comparison. Read the report before interpreting measurements.

Limits: Node old space 2048MiB, Next cgroup 2500MiB, CPU 200%, no restart; browser
cgroup 768MiB with its own cleanup group. Fail-stop at cgroup peak >2400MiB,
host available <1200MiB, OOM, worker/parent/start-tick change or source mismatch.
Only exact declared HMR text is allowed during the copy's source check. No .env is
loaded. Unexpected source/worker changes must not be accepted or retried.
Snapshots: <=384MiB each and 60s watchdog; allocation profiles <=64MiB/process.
Use sequential trials. Retain raw files privately with 0700 directories/0600 files.
Do not commit snapshots, profile files, private-detail output or raw journals.

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  deploy/development/retainers/analyze.cpp -o /tmp/nadi-fix05-private/analyze
```

Run analysis only in a disposable 1500MiB/180s/200% CPU scope. It accepts only private
absolute snapshot paths, <=384MiB, <=4M nodes, <=20M edges, <=2M strings and the
verified V8 schema. Public output contains numbers and allowlisted labels. Optional
`--private-details` is solely for local private investigation; never publish it.
The analyzer excludes weak and non-root shortcut edges but **does not simulate
WeakMap ephemeron conditionality**. Dominators describe that projection, not exact
GC deletion effects. Generic reachability must not be mistaken for retained-byte
ownership. V8 elides large string names to 1024 characters in these snapshots;
absence of inline-map text does not establish absence of map payloads.
