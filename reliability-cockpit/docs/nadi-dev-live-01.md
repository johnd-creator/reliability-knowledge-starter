# NADI-DEV-LIVE-01 — Persistent laptop development

Candidate foundation based on reviewed main `f54643f3510bf505628a1400024784faab46e496`.
No operational deployment or Engineering API activation. The original workspace,
its untracked spreadsheet, operational services and accepted Phase-1 evidence are preserved.

## Boundaries and URLs

| Surface | Mode | Data / persistence |
|---|---|---|
| `https://localhost:13035/` | Next.js development / Fast Refresh | Existing local factual Cockpit API; reads only |
| `/login`, `/engineering/local` | Real local authentication + bounded QA proxy | Persistent isolated PostgreSQL application records, synthetic asset context |
| `/engineering`, `/engineering/workflow`, `/engineering/lab` | Explicit synthetic/browser-local concept demos | Demo fixtures, not operational evidence or the persisted application |
| `http://127.0.0.1:13036/health/ready` | Dedicated QA factory | Application connectivity only |
| `/development/status` on the backend | Safe aggregate development metadata | No credentials / connection strings |
| Frontend `/api/development/status` | Development opt-in only | Branch, full SHA, dirty state, backend and test DB readiness |

The development sidebar links to `/engineering/local`. The banner links separately
to local login and synthetic demo screens. Inspection, cases, recommendations and
Action Board currently share the bounded JSON-command QA interface; polished
concept screens are demonstrations and do not become real operational workflows.
Main factual pages read the existing local operational API. Those reads do not
start collectors, acquire new source data, or give Engineering an operational writer.

## Private layout and process ownership

Use a separate worktree under an ignored local `.nadi-dev/worktree` directory.
Private state lives in sibling `.nadi-dev/state` (0700), outside Git and outside
Next.js public assets. A pinned private controller/wrapper remains usable when the
preview worktree changes refs. Configuration and generated test passwords are 0600;
admin, engineer and reviewer accounts are fixture identities, not plant users.
No password is committed or printed by setup/status/log commands.

The PostgreSQL container is uniquely named/labeled, loopback-published on 15443,
limited to one CPU / 512 MiB, and has its own retained data directory. Database:
`nadi_live_dev_test`; dedicated fixture owner: `nadi_dev_fixture`. The server rejects
any other host, port, owner, database or URL query override. The canonical
ApplicationStore additionally rejects Mart schema anchors.

User transient units `nadi-live-api` and `nadi-live-web` own the processes. Each has
CPU, memory and task limits, private umask, explicit working directory and bounded
restart-on-process-failure. No unit is enabled at boot; no linger is enabled. They
survive the terminal/task ending while the user session remains alive. PostgreSQL
also has no automatic boot/restart policy. On logout/reboot run `start` again; data
remains on disk. Runtime stdout goes to the user journal, without access logging.

Both processes use an explicit `env -i` allowlist. No source credentials or
operational DB/admin DSNs are inherited. Backend config is a dedicated private JSON
file. Frontend startup rejects dotenv files that could silently override the reviewed
configuration. Dependencies are copied into isolated local directories, preserving
existing dependency runtimes. Dependencies need separate review/update if a selected
branch changes package requirements.

## Operator commands

From the original workspace, use the stable private wrapper:

```sh
./.nadi-dev/nadi-dev status
./.nadi-dev/nadi-dev logs
./.nadi-dev/nadi-dev stop
./.nadi-dev/nadi-dev start
./.nadi-dev/nadi-dev reload
./.nadi-dev/nadi-dev backup
```

`stop` retains PostgreSQL files and records. `reload` replaces only development
processes and resumes the same database. Source edits under `src/` or `tests/qa/`
trigger Uvicorn reload; frontend component edits trigger Next Fast Refresh. The
persistent launcher never drops/reinitializes schema on ordinary reload, never
recreates accounts, and uses live clocks for session expiry. Source context is
synthetic and rebuilt in memory; human/application records persist in PostgreSQL.

Open `state/accounts.json` locally to obtain the random passwords for
`fixture-admin`, `fixture-engineer`, and `fixture-reviewer`. Do not paste them into
chat or public reports. Local login uses Secure/HttpOnly cookies, trusted HTTPS
Origin, session revocation and CSRF checks. Independent reviews use the separate
reviewer account; browser fields never supply authorization.

HTTPS uses a local self-signed certificate. Normal browsers may show a certificate
warning and the Codex in-app browser may refuse it. Automated acceptance uses an
isolated browser test context for this known localhost certificate. System/browser
trust stores are unchanged. Operator approval is needed for any later trust-store
installation; no global certificate-validation bypass is installed.

## Safe branch/merged-main update

1. Record `status`; commit or deliberately preserve changes. **Never reset dirty files.**
2. Stop the development processes.
3. Fetch only when explicitly updating a reviewed release; review the exact chosen ref.
4. Run `./.nadi-dev/nadi-dev switch <reviewed-ref>`; it rejects running services or dirty files.
5. Inspect dependencies and application migration compatibility before `start`.
6. Start; confirm banner/worktree/backend SHA agreement and test DB readiness.
7. Stop and switch back to the recorded commit or branch with the same procedure.

Switching is detached and explicit. There is no automatic pull/reset/rebase,
branch combination or promotion to main. A branch must include the reviewed live
preview foundation; startup fails closed if launcher/status files are missing.
Main at this task's baseline lacks this candidate infrastructure. Do not overlay
candidate files on an unrelated branch silently. New checksum/schema drift fails
closed; never repair drift by deleting migration history. A SHA mismatch in the
banner requires explicit reconciliation/reload, not silent promotion. Dirty state
is shown separately; ordinary UI edits are expected and immediately hot-reloaded.
Next may regenerate `next-env.d.ts`; inspect generated-only differences separately.

## Backup, reset and recovery — explicit only

`backup` creates a private custom-format dump of the dedicated development DB.
Before resetting, stop web/API, record fixture identity and take a validated backup.
Reset/recovery requires a separate explicit operator request naming this development
database. It is intentionally not an automatic command and was not executed here.
A recovery may restore that dump into the same confirmed isolated fixture or
initialize a fresh explicitly named development fixture with corresponding account
provenance. Never point these procedures at the operational Cockpit/Maximo/PI stores.
Do not delete state/accounts or data as routine troubleshooting.

Attachments have a reserved private 0700 directory. This QA factory supports current
attachment metadata/contracts, not a configured production upload/scanner service.
Actual attachment upload/storage/scanner integration remains separate future work.

## Acceptance evidence

Private acceptance screenshots/logs are retained outside Git. Browser workflow:
40 checks, including username/password login, scoped context, inspection/review,
case/evidence/review, recommendation/review/follow-up, session resume and responsive
390/768/1365 layouts. Additional acceptance: 12 checks covering eight rendered
screens, actual component HMR without document reload, restoration, and backend
reload with identical inspection/case/recommendation payloads and revisions.

All temporary HMR/backend probes were restored. Existing operational container
identities/start times are compared before/after. No production source GET,
operational DB writes/DDL, collector restart or Phase-1 governance mutation is part
of this workflow. Phase 1 remains CURRENT/PARTIAL; this is a laptop development
foundation, not QA/production acceptance.

## Regression and gate checks

Cockpit command (explicit isolated legacy SQLite fixture, no operational DSN):

```sh
COCKPIT_CONFIG_MODE=managed DATABASE_URL=sqlite:////tmp/nadi-dev-live-unit.sqlite \
  PYTHONPATH="$PWD:$PWD/tests" <private-python> -m unittest discover -s tests
```

697 run / 474 PASS / 223 SKIP / 0 FAIL. Optional PostgreSQL/managed-Compose suites
are not enabled against the active development database: some reset schemas.
Real PostgreSQL persistence was tested by the browser workflow and reload/restart
checks on the dedicated fixture instead. The initial no-DSN run had two legacy
pipeline smoke failures because those tests use the default database; the rerun
uses explicit isolated SQLite and resolves both without operational writes.

Frontend: `tsc --noEmit`, `npm run build`, and existing Engineering/Phase2/workflow,
local-login, HTTP QA, bounded HTTP/proxy checks: 143 assertions PASS. Product safety
checks cover 33 UI source files. The 10 added backend tests cover exact DB identity,
private configuration, credential environment isolation and dirty/running switch
rejection. Five isolated production-gate checks confirm disabled behavior even with
preview flags set: login and API paths return 404; Engineering pages render Next's
not-found view (streamed HTTP 200), with no Workspace form. No production API or
service is activated by that test.
