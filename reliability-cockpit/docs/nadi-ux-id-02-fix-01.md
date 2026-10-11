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


## Actual controlled activation — 2026-10-11, 16:31 WIB

F0/F1/F2/F3/F4 implementation and initial actual activation PASS on
`b6a4981ab9bbfd8c1bf6dca51ced4e1ed2b7c881`. Backend/source API remains
`b348235ce6f82c84873a65344ad2ef5fe276987d` at PID1664250 since07:53:34WIB;
all API cgroup process IDs unchanged. Only frontend PID changed to2018220.
Frontend/backend are AVAILABLE, source clean, stale=false and compatibility explicitly
VERIFIED_SOURCE_EQUIVALENT. Installed launcher source is b6a4981; SHA256
`48f8a2ef5c56dfde699ebd117bb1d0a0dcb3e21c7b972628a2983caa7631fa99`.
Contract equality digest `d5478750aeba179ff4affd5f6c425f7f76cd1e16eae71e882cf7dab40d9b8368`.

[Exact-head initial CI](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38128497987)
backend/frontend PASS:184backend tests/zero skips,14canonical contracts, all frontend
assertions/lint/type/build and370network-isolated browser checks. Actual live browser
separately PASS106checks/30screenshots, zero page exceptions and no horizontal page
overflow at1440/768/390. Overview, Asset Health, PdM, Cases, Advisory, Inbox, glossary,
Recommendations, login and dark mode verified. Glossary search works in the actual
preview; approved QA Inbox retains receipt-only ACK. Invalid CSRF rejects logout and
the original trusted session remains valid. No business commands submitted.

Snapshots immediately before/after cutover prove byte-exact database preservation.
After authenticated UI review: all82original session rows retained exactly; all accepted
Case/Inspection/Recommendation/Advisory/ACK rows, revisions/receipts/history, migrations,
grants and constraints exact. Three account identities/roles/scopes/password hashes/
grant versions/policies compared against private backup COPY output and remain exact.
Only normal login updated_at advances; sessions and security audits append normally,
login budget advances. The inspection initially flagged expected audit/account activity;
comparison was narrowed only after verifying the exact authorization invariants against
the original backup. No privilege/credential or business-record changes were accepted.

All35original container IDs/start times, unrelated35worktrees, fivePNG/workbook hashes,
private wrapper and original backups remain unchanged. New implementation/release
worktrees are additional and retained. Private backup `backup-20261011-162612.dump`,
SHA256 `78cf4dc6c8ee723aaa876b74e8935a4b34d669f816209b8f5e8679f71927e2d4`,
passes owner/mode/freshness/archive-list checks. No active restore or DDL performed.
Official rollback preflight to b348235 PASS; initial recovery record
`frontend-recovery-6a888b1c1b624ae8b956acdd167b5398.json` is retained privately.
Hermetic recovery/rollback tests PASS; actual rollback is intentionally not run against
the successful preview. Expanded Advisory/ACK schema remains on application rollback.

Actual screenshots/reports remain private under state/ux-id-02-fix-01/live; final
release screenshots under live-final. They are LIVE, not intercepted/synthetic.
Screenshots cover overview, asset-health, pdm, cases, advisories, inbox, glossary,
recommendations and login at all3widths, plus3dark overview images. Fixture screenshots
are separate under /tmp/nadi-fix01-fixture-evidence. No credentials or cookie/token values
appear in screenshots/reports. Factual screenshots stay private rather than publishing
operational data to GitHub. Final documentation-only release source is selected through
the same official controller after independent exact-head CI; its exact SHA and status
are verified in PR71/final handoff, not inferred from this earlier screenshot checkpoint.

Outstanding UX: the full provenance banner occupies substantial space on mobile; retain
full hashes for truthful review. Some original QA record titles and raw vendor/contract
codes remain English by ownership design; translating stored values is outside scope.
Global enforcement, real recipients/channels, operational PdM and engineer UAT are still
gated. Phase1 review/PO checkpoint/hard expiry unchanged and require their own operator
review; runtime availability does not certify source freshness.
