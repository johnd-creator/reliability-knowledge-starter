# AGENTS.md — Reliability Data Contracts

## Mission

Maintain vendor-neutral semantic contracts for reliability applications.

## Rules

1. Do not copy vendor-specific payloads directly into core contracts.
2. Preserve source-system identifiers under `sources`.
3. Prefer stable organization-owned IDs where available.
4. Document units explicitly.
5. Use ISO-8601 timestamps.
6. Mark nullable/unknown fields intentionally.
7. Backward-compatible changes are preferred.
8. Breaking schema changes require a version bump.
