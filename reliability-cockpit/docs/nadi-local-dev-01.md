# NADI-LOCAL-DEV-01 — Single laptop development workflow

15 Oktober 2026. **PASS — local development acceptance.**

Open **https://localhost:3000/pdm**. PR #82 is visible without merging it. Both frontend and development API load the selected feature worktree. Normal file edits use Next Fast Refresh / Uvicorn reload. No additional frontend address was created and no PREVIEW-02/03 investigation was resumed.

## Actual source and runtime

| Item | Verified value |
|---|---|
| Reviewed main | `2e190c2b51fde50e0467d6d5165ebb1060902867`, fetched again |
| Feature PR | [#82](https://github.com/johnd-creator/reliability-knowledge-starter/pull/82), OPEN |
| Frontend feature SHA | `9895890a045a221998856a175d80c17270cd0d38` |
| Backend feature SHA | `9895890a045a221998856a175d80c17270cd0d38` |
| Active branch | `codex/nadi-local-dev-pr82` |
| Exclusive worktree | `.nadi-dev/local-dev-pr82` |
| Controller implementation | `45a9141116a329e399ce2074210e287c5248cf73`; dedicated `codex/nadi-local-dev-01` branch |
| Fixture bootstrap implementation | `f0f1a72a2e9c70a858a8d753d6cb4d72b69b898b`, unchanged by subsequent controller hardening |
| Next runtime | Node **22.23.1**, V8 `12.4.254.21-node.56`, binary `/usr/bin/node-22`; binary/shared library hashes match retained private pin |
| Frontend | `nadi-primary-web.service`, main1348659, listener worker1348677/start ticks88780062, inode45326042, loopback IPv6 port3000 |
| Development API | `nadi-live-api.service`, reload parent1348657, loopback port13036 |
| Fixture | **nadi_local_dev_01_test**, role `nadi_local_dev_01`, in existing laptop development PostgreSQL container on loopback15443 |
| Dirty state | TRUE, accurately displayed; only the normal generated `web/next-env.d.ts` cache-path change remains |
| Compatibility | SAME_SOURCE; frontend/backend/launch SHA agree, stale=false |
| Availability | Engineering backend and existing factual backend AVAILABLE |

The existing Next status endpoint and banner show branch, HEAD, dirty state, frontend/backend SHA, fixture identity and synthetic/read-only boundaries. Controller hashes are retained in private `local-development-release.json`; the QA status endpoint also identifies its separately reviewed bootstrap SHA. This does not pretend the bootstrap tooling itself is a PR #82 application file. Old frontend-only manifest launcher fields can remain null for a SAME_SOURCE pair.

## Why the features were absent and what changed

Before transition the frontend was `f06abce76f8ef9b967ee5b1c2e0802112d77b056` from `.nadi-dev/ux-login-01-release`, with Node25.6.1, main3078556 and listener933368/start ticks76079111. API source remained `b348235ce6f82c84873a65344ad2ef5fe276987d` from `.nadi-dev/worktree`, parent1664250 and worker1664262. An open GitHub PR had not changed either running source. The frontend's sole dirty file was the exact `.next` → `.next-primary-dev` generated reference; its bytes and original diff remain preserved.

Frontend-only contract equality correctly rejects a PdM frontend paired with an older API. The new workflow coordinates the two existing development units through the existing `nadi-dev` controller and lifecycle lock. It adds a command companion, not a second continuously running supervisor or helper attribution framework. Existing controller/helper releases were retained privately before installation.

The original PR #82 `live_server.py` hardcodes `nadi_live_dev_test` and invokes migrations on initialization. Instead of repurposing that historical store, the development bootstrap imports **the unchanged PR #82 QA services and PersistentFixture wiring**, with a new explicitly identified fixture. Preparation applies canonical migrations and the existing Advisory/ACK QA schema helper **only to the new empty fixture**. API startup/reload verifies an already-applied ledger and never runs a migration or account bootstrap.

The new DB role has no superuser, create-database, create-role, replication or bypass-RLS capability and no membership in operational roles. It owns only its new fixture. Configuration includes no collector/Mart DSN or source credentials. The application environment is explicitly constructed, not inherited from operational dotenv files. Mart context is generated in memory by the existing synthetic fixture; factual screens retain the existing read-only Cockpit proxy. The original PostgreSQL container, database and sessions were not moved or replaced.

## Practical development use

The working source is:

```text
/home/john-d/Music/reliability-knowledge-starter/.nadi-dev/local-dev-pr82
```

Edit frontend files there and review HTTPS3000 immediately. Backend files under its `reliability-cockpit/src` and `tests/qa` use the development reload watcher. Dirty source is an expected development state and remains visible. No promotion or new preview is needed for each edit. Do not edit another historical worktree expecting it to appear here.

```sh
# Inspect the actual selected pair and release-integrity status:
.nadi-dev/nadi-dev status
.nadi-dev/nadi-dev local-status
# Explicit recovery only if needed; this stops the selected pair:
.nadi-dev/nadi-dev local-rollback
```

Initial source selection requires a clean exact PR #82 checkout. There is no automatic pull, checkout, merge, reset or dirty-file cleanup. Branch/commit checkpoints or incompatible contract selection still require an explicitly coordinated source decision; normal file editing does not. The task's `local-select` journal permits only one transition and will not automatically deploy again after a failure. Do not delete that journal to bypass the limit.

Synthetic account credentials are in the private laptop file `.nadi-dev/state/local-dev-01/accounts.json` (engineer/reviewer/outsider/operator). They are not GitHub artifacts or default credentials. Previous QA account/session credentials remain in their original private state and are not reused in this fixture. The HTTPS certificate and Secure/HttpOnly/CSRF/Origin/role/scope controls are unchanged. Global login enforcement was not activated.

Frontend budget: heap4096MiB, MemoryMax6GiB, CPUQuota200%, TasksMax256. API budget: MemoryMax2GiB, CPUQuota200%, TasksMax256. Both use the existing named systemd units, explicit loopback listeners, KillMode=control-group and Restart=no. No system-wide Node replacement or boot autostart was performed.

## Acceptance evidence

[Evidence index](evidence/nadi-local-dev-01/README.md). Screenshots are actual live HTTPS3000 renders with synthetic records; responses were not intercepted/replaced.

| Gate | Actual result |
|---|---|
| Engineer and reviewer login | PASS |
| Unauthorized access / foreign asset scope | PASS:401 and403/404 as appropriate |
| Multi-point create and saved detail | PASS:4 original measurements, zero distinct from null, original units/timestamps retained |
| Draft revision | PASS:revision1→2 persisted through CAS |
| Server-side register/history filters | PASS:authorized-population contract, matching/nonmatching results reconcile |
| Original-sample scatter | PASS:3 original numeric samples, no interpolation; mixed/null context is explicitly non-comparable |
| Independent review | PASS:submit→review→approved revision5; self-review rejected; no health/diagnosis inferred |
| Engineering Case | PASS:exact approved inspection revision5 frozen into evidence; stale revision rejected |
| CSRF | PASS:invalid token rejected403 |
| Desktop1440 and1920 | PASS:input/register/history/review/Case accessible, no page overflow or uncaught application error |
| Fast Refresh | **PASS**:temporary visible text appeared/reverted without document reload or unit restart |
| Backend reload | **PASS**:temporary read-only `/health/live` probe appeared/reverted after code edits; parent unit unchanged |
| Session/persistence through reload | PASS:same subject/CSRF session and saved records remain readable after reconnect |
| Existing product routes | PASS:PdM, Cases, local Engineering, Recommendations, Action Board, Advisory and Inbox |
| Local focused regression | 72 tests PASS:17 new workflow safety,23 existing frontend-controller,20 existing launcher,12 PdM tests |
| PR #82 CI | Exact feature HEAD backend/frontend SUCCESS, [run38377278956](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38377278956) |

Both temporary frontend/backend probe files were restored byte-for-byte. Only the expected generated type reference remains dirty; it is not suppressed or reset. The Next listener PID/start ticks/inode remained unchanged across acceptance and HMR. Backend child reload was intentional; its parent, invocation and restart count remained unchanged.

Observed frontend memory current~856MiB, peak~1131MiB; API current~125MiB, peak~195MiB at the recorded sample. Both NRestarts=0, cgroup OOM/oom_kill/max events0; no matching V8 fatal/abort journal entry for the new invocations. These are bounded functional observations, **not sustained runtime certification**.

### Failed checks and corrections retained honestly

- A sandboxed hermetic PdM test did not complete and was stopped without touching NADI. The bounded component-interpreter run outside that restriction subsequently passed12/12. No operational DSN was configured.
- An initial existing-launcher test command used a Python without SQLAlchemy; it failed at import. It was rerun using the owning component runtime, not by installing or changing the app environment.
- Two browser runs timed out on an exact textarea label after it contained existing text. A focused DOM/screenshot showed the edit form working; the selector was corrected to match the label prefix. No application source was changed.
- Review approval correctly stayed disabled after beginning review because the refreshed form required a new rationale. The continuation filled that required rationale, then approved the same record. No bypass or replacement record was used.
- Private preservation verification initially had a Python import-path error after its comparisons; it was corrected and rerun read-only.

All partial browser results, failures and continuation checks are retained. The final gate combines those actual passed stages on the same inspection/Case, not a claim that the first automation script passed end-to-end unchanged. Self-review additionally hardened controller release checks and rollback-resource validation before stopping a candidate, with a negative regression proving a changed recovery source cannot stop it.

## Preservation and rollback

Fresh `original-qa.dump` is private, with a recorded SHA256, readable archive TOC and full SQL decode to `/dev/null`. No restore was directed at an active database. The original units, source refs, manifest, config/accounts, generated diff and controller releases are retained. Recovery verifies release hashes, original source/config, DB container identity and backup digest before stopping an owned candidate. It restores the original pair and its original store without restoring/deleting any rows.

Post-acceptance digests match for **all14 original public tables and all public constraints**, including10 Engineering Cases,17 human records,95 sessions and5 migration ledger entries. Original audit/revision/receipt/account tables are included in that comparison. All35 container IDs, status, start timestamps and restart counts match baseline. No collector, operational API, external QA server, Mart write, source GET, retry, watermark or freshness-policy action was performed.

Rollback is **VERIFIED READY** through fresh artifact/source/ownership checks and hermetic failure-path tests. An actual live rollback was not needed or run, avoiding a second transition. The preserved old frontend would return to its historical Node25 environment; this is recovery evidence, not endorsement of Node25 for new development.

The original workbook, PNGs, unrelated root worktree and prior 135-test offline guard evidence/worktree remain untouched. PR #75–#81 and PR #82 were not merged or rewritten.

## Final fields

| Field | Result |
|---|---|
| TASK | NADI-LOCAL-DEV-01 |
| STATUS | **PASS — local development** |
| ACTIVE_DEVELOPMENT_URL | **https://localhost:3000/pdm** |
| ACTIVE_BRANCH | `codex/nadi-local-dev-pr82` |
| FRONTEND_SHA | `9895890a045a221998856a175d80c17270cd0d38` |
| BACKEND_SHA | `9895890a045a221998856a175d80c17270cd0d38` |
| NODE_VERSION | **22.23.1** |
| DEVELOPMENT_DATABASE | **nadi_local_dev_01_test** |
| FAST_REFRESH | **PASS** |
| BACKEND_RELOAD | **PASS** |
| PDM_LOGIN | **PASS** |
| PDM_MEASUREMENT | **PASS** |
| PDM_HISTORY | **PASS** |
| ENGINEERING_CASE | **PASS** |
| DESKTOP_1440 | **PASS** |
| DESKTOP_1920 | **PASS** |
| BACKUP_ROLLBACK | **VERIFIED** readiness; live rollback not performed |
| COLLECTOR_CHANGED | **NO** |
| MART_CHANGED | **NO** |
| OFFICIAL_QA_SERVER_CHANGED | **NO** |
| PR82_MERGED | **NO** |
| NEXT_ACTION | Product Owner browser review; retain this serving pair |

PR #82 recommendation: technically ready for Product Owner desktop review based on its exact-head CI and this local workflow acceptance. Merge remains a separate decision; methods, field approvals Q01–Q10, operational PdM activation, mobile polish and production acceptance remain separate gates. The existing large status banner/design is unchanged by this workflow task. No broad runtime investigation or additional preview is proposed.
