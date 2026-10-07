# AGENTS.md — Reliability Cockpit

## Mission

Build reliability applications by consuming verified organizational knowledge rather than rediscovering production systems.

## Source of Truth

Before introducing a Maximo field, PI tag, endpoint, WebId, or parameter:

1. Search the relevant knowledge repository.
2. Prefer entries with `status: verified`.
3. If knowledge is missing, create a discovery task in the appropriate source-knowledge repository.
4. Do not guess production identifiers.

## Architecture Rule

Application domain models must prefer `reliability-data-contracts`.

Vendor-specific fields belong in source adapters.

## Safety

Production source systems remain read-only unless a separate explicit authorization exists.

## Existing Mart runtime boundary

`DATABASE_URL` addresses legacy Cockpit only. `RELIABILITY_MART_DATABASE_URL`
is the explicit SELECT-only existing Mart reader. Local governance/mapping
commands require `RELIABILITY_MART_ADMIN_DATABASE_URL` and explicit expected DB;
never fall back between them. Canonical governance 002/003 uses `mart-migrate`
status by default and deliberate `--apply` after backup. `init-db` must not
initialize governance in legacy Cockpit. See `docs/mart-runtime.md`.
No new operational DB, source discovery, inferred mapping or source credential.
