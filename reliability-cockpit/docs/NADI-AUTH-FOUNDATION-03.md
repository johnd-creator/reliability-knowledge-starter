# NADI-AUTH-FOUNDATION-03

18 October 2026 WIB. Implementation checkpoint; final activation evidence follows.
This task implements the Product Owner's explicit BSR/IP factual-read authorization,
login-aware readiness and trusted self username. It preserves the
[AUTH-02 boundary](NADI-AUTH-FOUNDATION-02.md) and earlier Phase2 UI changes.

## Authorization

Only the verified retained directory subject
`local:c759c2d1-19a4-4291-9b66-9218dbd12dea`, with current ADMIN, receives the code-only
`BSR_IP_FACTUAL_PORTFOLIO_READ` capability in the approved primary local-development
runtime. A username, browser header, generic ADMIN role, synthetic asset grant or query
parameter cannot confer this capability. No directory grant or SQL permission changes.

Approved canonical portfolio aggregates and Registry lists remain BSR/IP; exact detail
and asset-ref requests require a server-side Registry lookup with matching canonical ID,
siteBSR and organizationIP. Scoped AUTHOR/REVIEWER do not inherit portfolio totals via
asset context/integration responses. Existing Engineering permissions, review independence,
canonical audit subject, CSRF, Origin, revisions and persistence remain authoritative.

Legacy `/equipment`, `/work-orders`, `/kpis` are deliberately not newly authorized:
their published DTO/query contracts do not prove BSR/IP/Registry scoping. Export, unknown
routes and writes remain denied. This is not a blanket access grant to every backend route.
RCFA asset relationships remain unresolved; approved global BSR/IP RCFA reads do not
create such relationships or permit cross-inspection diagnosis/scoring.

## Self identity

The current-session route adds only the actor's `username`, read from the existing local
directory inside the valid session lease. It does not accept a target username/subject,
expose another account, return security metadata, or replace immutable subject/roles/assets.
The header shows the recognized username, canonical subject as audit tooltip, role labels
and existing Logout. Missing username falls back to the canonical subject.

## Controller readiness design

Full development diagnostics remain ADMIN-only. New local-only
`/api/development/health` exposes a narrow transport contract: source/launch SHA, dirty
state, expected origin and guard identity; no DB/account/session data or full diagnostics.
QA `/health/ready` reports the initialized local SessionAuthority capability plus DB
connectivity. The launcher combines these with existing process/socket/start-time/Node,
source, bootstrap, QA database identity, factual health and compatibility checks.

Anonymous root must give the exact known login redirect with no-store; anonymous factual
health must give the exact401 contract; a fake session must be rejected through the actual
Engineering session route. An optional owner-only current session file additionally tests
real session verification and authenticated factual health. Absence of that proof is reported
NOT_PROBED_NO_SESSION, never falsely labeled a positive session test; an explicitly supplied
expired/revoked proof fails closed. No arbitrary302/401 alone establishes authentication health.

The source controller preserves existing lifecycle, backup, clean-initial/dirty-active,
checkpoint, schema compatibility and recovery checks. A focused metadata-only installer uses
the existing immutable four-file release/manifest/wrapper model, exact Git source blobs and
the already established ROOT-path binding. It validates candidate readiness independently
before changing pointers, retains the old release/configuration, locks against concurrent
updates, and recovers metadata only on failure. No source handover, service restart, database
restore/migration or lifecycle command is part of installing this readiness update.

Application bootstrap SHA and installed controller implementation SHA are separate provenance
fields. Updating the readiness implementation never relabels the already running QA bootstrap.

## Pre-activation evidence

- Active HEAD remains `7daab3a62866f19b30fb45462a94bafff8795dc5`, dirty ModeA;
  AUTH-02 review parent `d17450d4811d8978d01f919032e7d319c523a4c1` retained.
- Existing controller/bootstrap release `106a4dc08b149576b2e84bbf8c70694288c7e9a7` retained.
- Frontend parent21538/worker728443 unchanged. QA parent21536 unchanged; source reloader
  replaced child21549 with834916 after the three reviewed auth files changed. No unit restart.
- Cockpit API remains127.0.0.1:8000, all35 baseline containers retained without recreation.
- Staged frontend21 groups PASS; TypeScript/lint/build PASS (one pre-existing hook warning).
  Backend210 PASS/0 SKIP on disposable PostgreSQL. Launcher/update/lifecycle119 PASS/0 SKIP.
- Actual trusted HTTPS browser checks passed for ADMIN factual dashboard, Registry/detail,
  scoped canonical modules, username refresh, restricted AUTHOR, review denial and logout.
  Register response matches direct factual API exactly. Executive DTO stable fields match;
  query-time as_of/window_start differ naturally between requests with identical window basis.
- Six responsive light/dark dashboard captures plus Registry capture retain real UI and redact
  sensitive asset rows only during screenshot capture; no intercepted data or fixtures.

Final installed-controller acceptance, source hashes, preservation, rollback and delivery flags
will be recorded after the pinned update is validated. Product Owner acceptance remains pending.
