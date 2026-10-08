# ADR 006 — Engineering Workspace ownership and safe activation

Status: candidate; baseline e67c641e23214bf8851a05d312e1426c1e471ec3 / merged PR28.
Owner-authorized source-free Phase 2 work; no runtime acceptance implied.

## Assessment

The existing FastAPI factory exposes factual GET routes and no trusted user
principal dependency (`src/api/app.py`). Source authentication in `src/config.py`
is source-system authority, not application user authentication. `Database` /
`CockpitStore` own the separate application store; `MartDatabase` and canonical
Mart migrations are a different SELECT-only consumer boundary. Existing
`web/components/ui.tsx` supplies navigation, themes and factual UI primitives.
Tests use unittest, fake adapters and isolated SQLite/optional PostgreSQL.
There is no reviewed product RBAC, authenticated review workflow or append-only
engineering audit repository to reuse. Graph generation predates this main;
exact baseline source inspection is authoritative for these observations.

## Decisions

1. Human cases belong to the existing application-owned Cockpit store, never
   the collector-owned canonical Mart. No new operational database.
2. Hypotheses, priorities and decisions are human judgment, separate from facts.
3. Separate Engineering SQLAlchemy metadata and candidate application migration
   namespace. Neither legacy init-db nor mart-migrate imports/initializes it.
   Disposable tests only; production migration/writer grants need later review.
4. Trusted server principal adapter must establish authentication, asset scope,
   author/reviewer capability and CSRF/session protections appropriate to its
   transport. No identity headers, static production accounts or DSN fallback.
5. Server-resolved canonical evidence, exact asset binding, bounded allowlisted
   snapshots and local record IDs. Live references explicitly resolve again;
   frozen snapshots preserve their original time, quality and UNKNOWN state.
6. Atomic expected-revision compare-and-swap; stale edits return conflict.
7. Case update, immutable revision audit and scoped idempotency receipt share
   one database transaction. No audit mutation/delete API. Privileged database
   owner tampering remains a residual risk requiring deployment-level grants.
8. Backend feature defaults off. Router factory requires a trusted principal
   adapter and service injection. Production create_app does not mount it,
   even with an environment flag. UI defaults off; interactive synthetic demo
   is restricted to development mode, not operational API access.
9. Versioned /v1/engineering contract, extra fields forbidden, bounded paging,
   typed sanitized errors, idempotency key and expected revision required.
10. Phase 1 readers and readiness remain unchanged. Phase 3 may consume reviewed
    case/evidence versions offline; cannot promote hypotheses to source facts.

## Gate A disposition

PASS for disabled contracts, domain, isolated persistence/API and development
prototype. Production-addressable writes are BLOCKED on trusted application
identity integration, security review and explicit application writer provisioning.
This ADR is an implementation decision for review, not a claim of senior approval.
Independent architecture review is recorded in the accompanying threat model.

## Future activation checklist

Review identity provider/session revocation, request-origin/CSRF protection,
asset authorization, trusted directory, separate reviewer identity, least-privilege
application writer, migration ownership and audit retention. Verify flag off
in managed/external deployment. Operational rollout requires separate authority.
