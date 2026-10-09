# NADI-DEV-RESET-01 — single development frontend

NADI review address: **https://localhost:3000/**. This updates PR #62's existing
launcher and isolated Engineering implementation; it does not create another app.
PR #62 remains an explicit feature preview until merged. PR #63 is unchanged.
The deployment's existing `cockpit-web` container is retained stopped for rollback.
Never run a broad Compose `up`, restart, or recreate while this frontend owns 3000.

## Baseline and comparison

Verified `origin/main`: `f54643f3510bf505628a1400024784faab46e496`.
Before consolidation, port 3000 was the production Next frontend image at
`c2fb0fc686396e79c19f42af46694673827493a9` (container
`eead1eadcfbe84eeee244cec46713c5ee88df3281d1e98c13c916561dd64ec54`).
Port 13035 was HTTPS `next dev` from clean PR #62 worktree at
`28197f41d044a55cf247ffdd916ac00486644437`, branch `codex/nadi-dev-live-01`.
The original workspace remains on `feature/pi-governed-source-adapter` at
`0c800dac1da6ef863afdb193021176fe7feac073`; its untracked `23496711.xls` is retained.

Both frontends returned HTTP 200 for `/`, `/assets`, `/maintenance`,
`/maintenance/investigation`, `/fmea`, `/rcfa`, `/asset-health`, `/overhauls`,
and `/data-quality`. The old 3000 frontend returned 404 for `/login`,
`/engineering/local`, and `/api/development/status`; PR #62 supplied all three.
The newer checkout retains equipment detail and work orders, plus the synthetic
Engineering concept routes. The operational proxy still reads the existing
Cockpit API at `http://127.0.0.1:8000`. No source credentials enter the frontend.

| Surface | Owner / behavior |
| --- | --- |
| 3000 | `nadi-primary-web.service`, Next development, HTTPS and Fast Refresh |
| 13035 | Retired `nadi-live-web.service`; checkout and data retained |
| 13036 | Existing `nadi-live-api.service`, isolated Engineering QA factory |
| 15443 | Existing `nadi-dev-live-postgres`, `nadi_live_dev_test`, owner `nadi_dev_fixture` |
| 8000–8003, 3001–3003 | Existing operational APIs and collector web services |

The primary frontend uses `.next-primary-dev`, distinct from the retired preview
cache and production `.next`. Development flags opt into login, persisted QA and
synthetic demo routes only in `NODE_ENV=development`. Production gates remain.
The exact trusted login Origin is `https://localhost:3000`; HTTP and the retired
13035 origin are rejected. Secure/HttpOnly/SameSite cookies and CSRF checks remain.
Existing cookies, accounts, audit, application migrations and records are not reset.

## Startup and source selection

The existing private wrapper `./.nadi-dev/nadi-dev` invokes the pinned controller
outside the mutable checkout. Install an updated reviewed launcher by copying
`deploy/development/nadi-dev.py` to the private controller and binding its `ROOT`
to the retained preview worktree; do not replace private configuration/accounts.
Startup requires the existing fixture container and certificate. It never creates,
starts, replaces, or migrates an operational store.

```sh
./.nadi-dev/nadi-dev status
./.nadi-dev/nadi-dev backup
# First migration from the retained production container; explicit candidate ref:
./.nadi-dev/nadi-dev cutover --preview-ref codex/nadi-dev-live-01
# After browser acceptance:
./.nadi-dev/nadi-dev retire-legacy
# Ordinary start after development processes are stopped:
./.nadi-dev/nadi-dev start --preview-ref codex/nadi-dev-live-01
./.nadi-dev/nadi-dev reload --preview-ref codex/nadi-dev-live-01
```

Default baseline is **origin/main**: `start`, `reload`, and `cutover` without
`--preview-ref` require that checkout's HEAD equal the locally verified main SHA.
A mismatch fails before stopping anything. Fetch and inspect main explicitly;
there is no hidden pull, merge, reset, or dirty-file discard. Until #62 is merged,
main lacks the launcher foundation, so the reviewed candidate must be explicit.
This does not authorize merging #62/#63 or overlaying candidate files onto main.

For a later merged-main refresh or another reviewed branch:

1. Record current SHA, take a fixture backup, inspect dependency/migration changes.
2. Stop development processes; preserve or commit edits first.
3. Fetch origin and review the selected exact commit.
4. `./.nadi-dev/nadi-dev switch` selects `origin/main` by default;
   `switch <reviewed-ref>` is explicit. Running/dirty switches are denied, and
   targets missing the foundation fail before checkout changes.
5. Start on main without extra flags, or on a matching explicit `--preview-ref`.
6. Verify the banner: full SHA, branch/detached state, dirty state, factual backend,
   Engineering backend and exact fixture DB. A source/backend SHA mismatch is an alert.

UI edits use Fast Refresh without rebuilds. Dirty edits are visible in the banner.
For commit-only SHA changes, reload the development API so its loaded release SHA
matches. Never use operational services to solve a development SHA mismatch.

## Controlled cutover and rollback

`cutover` requires a clean, explicitly selected checkout, an existing fixture,
private config/certificate, and the exact managed `cockpit-web` container identity.
It records that container's ID/image/revision in private `frontend-rollback.json`,
stops only that container, starts HTTPS Next on 3000, and verifies the aggregate
status endpoint. Failure restores the original frontend automatically. An unknown
owner or changed rollback identity fails closed. Keep 13035 until browser checks
pass; `retire-legacy` independently checks readiness before stopping only that unit.

```sh
./.nadi-dev/nadi-dev rollback
# Verify old factual UI at http://localhost:3000; no image build or DB restore.
./.nadi-dev/nadi-dev cutover --preview-ref codex/nadi-dev-live-01
# Verify development UI at https://localhost:3000 again.
```

Rollback retains the QA API and fixture DB. It restores the original factual UI;
that older image has no development login. Re-cutover restores development login
against the same persisted records. No worktree deletion or data restore is needed.
`stop` and `reload` now retain the running fixture database instead of stopping it.
No command touches operational APIs, collector workers, Mart, source configuration,
or operational data. There is no boot auto-start or trust-store installation.

## Acceptance and evidence

Run backend regression with an explicit temporary SQLite legacy DSN and no
`NADI_APPLICATION_TEST_DSN`. Optional database tests reset their hermetic schemas;
never aim them at the persistent fixture. CI runs them in its temporary PostgreSQL.
Frontend checks: TypeScript, production build, all existing Engineering, workflow,
HTTP/proxy/auth and product-safety checks. CI also runs launcher lifecycle tests.

Browser acceptance must render the nine factual routes above and `/login`,
`/engineering/local`, resume a Secure session, and execute the existing independent
inspection/case/recommendation QA workflow. New synthetic acceptance records have
unique request IDs; old records are never edited. Check rejected Origin/CSRF and
self-review, reload persistence, exact displayed SHA/dirty state, real component
Fast Refresh without document reload, rollback/re-cutover, and closed port 13035.
Compare operational container IDs/start times and original fixture row checksums.
Private screenshots, dumps, browser logs, row hashes and exact post-cutover SHA
remain under `.nadi-dev/state/reset-01/`; no credentials or DSNs belong in Git.

The localhost certificate is unchanged and self-signed. The browser must accept
this known local certificate; no global certificate bypass or trust change occurs.
Factual screens read stored operational data; HTTP success is not a freshness claim.
Engineering context and demos remain **SYNTHETIC**, assessment **NOT ASSESSED**.
This is development acceptance, not real QA activation, operational approval, or
new PdM functionality. Phase1 remains CURRENT/PARTIAL; real QA remains NO_GO.
