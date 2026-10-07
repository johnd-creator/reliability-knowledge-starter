# Agent bootstrap — Power Plant Data Platform

Read `AGENTS.md` and `plans/README.md` before choosing work. This repository is
an existing platform, not a templates-only discovery starter.

## First actions

1. Read Git status, branch and current main baseline; preserve local changes.
2. Read `plans/PLATFORM-VISION.md`, the relevant product roadmap, engineering
   roadmap and `plans/REPOSITORY-STATUS.md`.
3. Read the owning component's scoped `AGENTS.md` / `CONTEXT.md` and domain docs.
4. Verify proposed work against actual Git/PR/source evidence; distinguish
   merged, unmerged, partial and planned work. Old graph/doc snapshots are not
   proof of current completeness.
5. Work in a task branch/worktree from the requested baseline. Use source graph
   discovery with coverage checks, then exact source fallback where stale.

## Current product direction

NADI is the main quest: factual Phase 0 accepted, Phase 1 Evidence Expansion
current/partial. Next technical PR is NADI-PI-001, whose scope/acceptance is in
`plans/NADI-ROADMAP.md`. NK is an intentional child application, with branch-only
code and separate mapping/model validation acceptance in `plans/NK-ROADMAP.md`.

Do not start an implementation merely because it is listed as next; execute the
actual user task. Do not bulk merge old branches or copy their data/models.

## Boundaries

Reuse existing DBs/volumes and shared collectors. NK needs no DB. Mart lives in
Maximo Collector DB; NADI legacy store and canonical Mart read paths differ.
No source credentials or independent production discovery in consumer apps.
Preserve read-only guards, semantic unknowns, units/identity/quality/time rules.
No runtime restart, source probe or model retraining as an implicit docs task.
PI credential investigation remains deferred until the user requests resumption.

## Handoff

Report changes, evidence, checks and limitations; update the owning roadmap
when accepted scope changes. Prefer focused PRs with task ID and acceptance.
Never describe tests, runtime freshness, mappings or analytics as verified from
branch existence or a conversation alone. Never publish secrets or raw source
exports. Documentation-only tasks must remain Markdown-only.
