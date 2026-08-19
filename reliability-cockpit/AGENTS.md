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
