# NADI-UX-ID-02-FIX-01 — frontend-only preview

## Scope and source

The fix is stacked on localization [PR70](https://github.com/johnd-creator/reliability-knowledge-starter/pull/70)
`a08da00fbbbbca960881d88c4dda69b18ada90d2`, on branch
`codex/nadi-ux-id-02-fix-01`. Main verified
`09b6d6308a6cc70818292eb71f79733255dcf823`; QA API remains pinned to
`b348235ce6f82c84873a65344ad2ef5fe276987d`. Neither PR is automatically merged.

The previous controller used one ROOT for Next.js and the reloading QA API; stop/reload
cycled both services. API factory startup invokes its migration helper even with no
pending migrations. This task never invokes that factory or changes that watched
checkout. Independent frontend selection removes that prerequisite without weakening
HTTPS, Secure cookies, CSRF, RBAC, independent review or session policy.

## F0/F1 — compatibility and lifecycle

The controller checks exact Git object equality for the entire backend source, QA
factory/routes, runtime-imported condition test fixtures, application migrations,
canonical contracts, Engineering proxy and DTO/transport/record hooks, and lockfile.
Dependency/engine/override sections must match. Any difference refuses selection;
this conservative proof supports presentation differences, not arbitrary backend
compatibility claims. The new lifecycle unit tests are deliberately outside the
runtime dependency comparison. No application API/backend contract changes occur.

Only the official wrapper/controller performs cutover. Immutable private approval and
recovery records are created before stopping the frontend. Ownership, certificate,
loopback QA DSN/container, clean trees, exact SHA, private validated backup, both
backend probes, API PID/start time and cgroup process IDs are checked. Failure recovers
only the previous frontend. No worktree is checked out, reset, overwritten or deleted.
The pre-existing original controller is retained privately before installation.
See [commands and rollback](nadi-dev-reset-01.md#frontend-only-reviewed-preview--nadi-ux-id-02-fix-01).

## F2 — provenance

The development-only status endpoint retains SHA/launch/dirty/stale fields and adds
independent frontend/backend SHA, source compatibility approval, reviewed launcher
SHA and digest. The localized banner displays those identities in full. A private,
owner-only approval binds both source roots and SHAs, compatibility and backup hashes.
The route verifies actual backend Git HEAD/dirty state separately from the running
backend status. Unapproved split SHA, forged approval, unknown/dirty/changed identity
remain stale. Production gating and all existing authentication proxies are unchanged.

## F3 — validation

Hermetic lifecycle coverage includes refusal before mutation, source/dependency
mismatch, stale/unapproved identity, dirty/unrelated worktree, private-state permissions,
HTTPS command/port ownership, failure recovery, API-change refusal, rollback re-preflight,
controller hashes and tightly bounded Next generated-type restoration. Provenance
checks cover missing/forged/stale/dirty/unknown identity plus wrong root/private mode/
symlink manifests. Frontend assertions, lint, TypeScript, production build and existing
network-isolated Indonesian browser workflow are rerun. Exact-head backend/frontend CI
must pass before actual activation. The pinned editor dependency warning predates this
fix; it is retained rather than changing unsaved-edit behavior.

## F4 — evidence separation and acceptance

Actual preview evidence is captured privately under
`.nadi-dev/state/ux-id-02-fix-01/` from the sole `https://localhost:3000`, with no browser
response interception. Actual screenshots can contain governed factual data and remain
local/private. Network-isolated fixture evidence is stored separately in `/tmp` and
explicitly SYNTHETIC; it cannot certify the runtime. Runtime activation/preservation
results and exact final release SHA are recorded in the final task/PR handoff after
verification. Until those checks complete, live visibility is PENDING, not PASS.

Authenticated QA inspection uses existing identities/records. No Case, Recommendation,
Advisory, ACK or source record is created or changed. Login/security probes can add normal
session/security audit activity; immutable business records, old sessions, schema,
grants, migration ledger, account privileges and original assets must remain intact.
Backup/archive validation is read-only; no restore into the active database is done.
Operational/collector container IDs/start times, all unrelated worktrees, original PNGs
and workbook are preserved. Phase1 checkpoints/expiry remain independently controlled.

Product Owner visual review, real engineer UAT and production activation remain separate
pending gates. This fix grants no real Advisory distribution or global login enforcement.
