# Maximo Knowledge

Living knowledge base for Maximo API capabilities available to the organization.

> **Building an app on top of this data?** Read [`CONTEXT.md`](./CONTEXT.md)
> first — it is the entry point for humans and AI tools (Codex/GLM).

This repository is not an application. It is a source-intelligence layer that
records:

- API discovery results
- object structures
- fields
- relationships
- supported filters
- pagination behavior
- access limitations
- business meaning
- verified use cases
- unit-specific mappings

The first executable component is the read-only discovery CLI in
`scripts/discover.py`. It parses local OAS fixtures and, only with explicit
`--execute`, fetches an OAS document or minimal endpoint samples using
GET/HEAD/OPTIONS. It never submits the Maximo login form or performs data
mutation requests.

## Suggested Discovery Seed

If available in the authorized Maximo environment, start from the OpenAPI page:

```text
/maximo/oas3/api.html
```

Do not assume every documented endpoint is authorized for the current account.

## Discovery CLI

```bash
# Parse without network access
python scripts/discover.py --oas-file openapi.json --scope reliability-core

# Enumerate OSLC object structures (GET-only, requires --execute).
# Maximo exposes its real surface via /oslc/os, not the OAS paths object.
python scripts/discover.py --enumerate-oslc --execute --scope reliability-core
python scripts/discover.py --enumerate-oslc --execute --resource asset workorder

# Fetch from an authorized read-only environment
python scripts/discover.py --fetch-oas --execute --scope reliability-core
python scripts/discover.py --fetch-oas --execute --resource workorder

# Manual form login, then browser-session GET discovery
python scripts/session_discover.py run --scope reliability-core --verify-samples
```

Credential values belong only in local `.env`; `.env.example` contains
placeholders. Automated discovery uses an approved bearer token. The observed
form login flow is documented in `docs/authentication.md` but is not submitted
by the CLI because production POST requests are prohibited by `AGENTS.md`.
For Maximo form authentication, the session CLI opens a browser and waits for
the operator to log in manually. It keeps the authenticated browser context
only in memory and writes discovery results to a timestamped staging run.

## Folder Guide

- `CONTEXT.md` — **entry point** for AI tools and new contributors
- `docs/` — human-readable knowledge (incl. `etl-playbook.md` for building fetchers)
- `discovery/` — machine-readable catalogs (`object-structures.json`, `objects/`, `capabilities.json`, `endpoints.json`)
- `schemas/` — JSON Schema definitions (`object.schema.json`, `endpoint.schema.json`)
- `samples/` — sanitized response examples
- `scripts/` — safe discovery helpers
- `mappings/` — organization/unit-specific semantic mappings

## Status Vocabulary

- `unknown` — not tested
- `documented` — present in docs/OpenAPI but not verified
- `verified` — tested successfully with authorized read-only access
- `forbidden` — endpoint exists but current account cannot access it
- `deprecated` — known but should no longer be used
