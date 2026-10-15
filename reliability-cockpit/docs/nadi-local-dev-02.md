# NADI-LOCAL-DEV-02 — Reusable single-laptop development

15 October 2026. Qualification scope: local tooling, deterministic tests, CI and GitHub integration. **No live branch selection, controller installation, application restart/reload, database access or external QA deployment is performed by this task.**

## Baseline and continuity

Verified main `8397b53df29280082d1382dfa3e40a5e4e2a97af`; PR #82 merged with backend/frontend post-merge CI PASS ([run 38682201507](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38682201507)). PR #83 began OPEN/DRAFT at `2b0b504fa6c2e4af6d4dd0b7e06f57735e9c95c1`. A normal merge of main reconciled its history without rewriting commits. [Issue #84](https://github.com/johnd-creator/reliability-knowledge-starter/issues/84) defines the two reusable-workflow blockers.

The active laptop pair remains PR #82 `9895890a045a221998856a175d80c17270cd0d38`, `.nadi-dev/local-dev-pr82`, Node22.23.1, HTTPS localhost:3000, fixture `nadi_local_dev_01_test`. Frontend parent1348659/invocation `3a93caa4e3a34eb3906c719a82778e10`; API reload parent1348657/invocation `63d9ca99b6de4cda83444469c4110443`. Source dirty state remains its existing generated `next-env.d.ts` cache-path difference. The historical [LOCAL-DEV-01 report](nadi-local-dev-01.md) remains an immutable record of its one-time activation, not current GitHub PR state.

## Explicit source selection

The updated companion requires a managed existing worktree **and** explicit reviewed ref. The ref resolves to an exact commit and must equal that worktree HEAD. Repository common-directory and GitHub origin are verified. No command performs checkout, merge, reset, pull or dirty-file cleanup.

Future authorized use after the reviewed controller is installed and pinned:

```sh
.nadi-dev/nadi-dev local-preflight /absolute/managed/worktree --preview-ref codex/reviewed-feature
.nadi-dev/nadi-dev local-select /absolute/managed/worktree --preview-ref codex/reviewed-feature
.nadi-dev/nadi-dev local-status
# Separately authorized recovery, taking a fresh private fixture backup:
.nadi-dev/nadi-dev local-rollback
```

These are future lifecycle commands, **not instructions to run them during this checkpoint**. The installed controller is deliberately unchanged. Its next upgrade/selection needs separate narrow authorization. The reviewed local release manifest must pin the exact bytes of `nadi-dev.py`, `local_development.py`, `local_fixture.py`, and `frontend_preview.py` plus its source commit. Existing historical controller releases, journals and recovery resources must be retained, never overwritten to bypass validation.

Frontend and backend start from the **same selected commit**. Independent runtime frontend/backend/launch/current-source SHA and bootstrap provenance are checked; equality alone does not approve schema compatibility. The existing contract comparator checks required source objects. A conservative fixture gate compares migrations, persistence repositories, authentication/identity and QA adapters, dependency specification and synthetic fixture wiring against the previously accepted source. Changed store/bootstrap/auth contracts require separately reviewed fixture preparation, not automatic migration. Dependency-install fingerprints must match the prior reviewed install; changing dependencies also needs preparation/review.

Initial candidate selection requires a clean tree. The outgoing recovery source may contain only the exact known Next generated type-reference transformation; its entire bytes are checked and retained without rewriting it. Other outgoing edits must be preserved/reconciled explicitly before switching. Changing HEAD in a serving worktree invalidates its recorded provenance and remains blocked; the controller never repairs that mismatch by checkout or reset. Use a separate reviewed candidate worktree and retain a verifiable outgoing recovery source. During normal active development, edits are allowed and dirty state remains visible. Existing Next Fast Refresh and Uvicorn source reload remain enabled; the parent API identity must remain stable while intentional reload children may change. No GitHub promotion is needed for each file edit in that selected worktree.

## Transition history and recovery

The existing `nadi-dev` frontend lifecycle lock still serializes CLI operations with legacy commands. A bounded nonblocking companion lock additionally protects direct selection/recovery calls. Every selection request gets a unique UUID and immutable private event files (`requested`, `prepared`, `stopping`, `accepted` or `failed`); rollback has its own identity. Records link the before/after source and recovery snapshot. Unresolved candidate identity stays explicitly UNRESOLVED on rejected requests. Failure codes are sanitized and evidence retained. The old `transition.json`, original backups and previous active records are not deleted.

Each attempt repeats preflight, creates a unique fresh private backup of **the existing local fixture only**, validates archive TOC and full SQL decode without restoring it, and revalidates recovery source/config/account hashes, DB container identity, catalog/ledger evidence and current process/listener ownership before stopping either unit. Backup age is bounded to one hour. Explicit rollback takes a new backup; it does not depend on deleting records or restoring an old dump. Both current unit/listener owners are validated before either is stopped during recovery.

Candidate configuration is a new private file referencing the **same existing DSN/accounts**, with the explicitly selected source root and reviewed bootstrap SHA. Original configuration is not overwritten. The active pointer changes atomically only after readiness/ownership verification. A failed start receives one verified recovery attempt and never retries candidate startup. If recovery cannot be validated, it fails closed and retains the previous pointer and all evidence; that pointer alone is not a claim that the old process is healthy. No restore, truncation, database recreation, session cleanup or account bootstrap occurs during selection/recovery.

Historical pre-reusable recovery artifacts remain available under their original reviewed controller. The new recovery path requires a reusable transition record and will not reinterpret the old one-time record or silently invent one.

## Fixture boundary

`local_fixture.py --check` is the only script CLI entry point and is read-only. It validates exact loopback15443/database/role, rejects privileged fixture roles, requires all canonical migration checksums APPLIED and the existing Advisory/ACK constraint, and returns catalog/ledger fingerprints. Startup retains its ledger checks without initialization. The historical explicit preparation function is not reachable from the selection or script startup path.

Operational DBs, collector/Mart DSNs, source credentials and dotenv files are excluded. The environment is constructed explicitly. Factual API availability is checked through its existing read-only health boundary only during a separately authorized future lifecycle operation. This task performs no runtime status HTTP requests or database probes.

## Deterministic acceptance

**94/94 focused tests PASS** using the owning component Python environment:17 preserved local workflow tests,34 reusable/fixture/preflight tests,23 existing frontend-controller tests and20 existing launcher tests. Commands are hermetic; lifecycle, sockets, HTTP and database operations are mocked. A temporary Git repository validates real ref resolution, common-directory/origin identity and dirty-tree refusal. No test uses the live fixture or application.

| Required scenario | Evidence |
|---|---|
| First, second and third selection | Distinct requested/prepared/accepted events, exact source chain and atomic active pointer |
| Normal frontend edits | Dirty=true is returned by readiness; clean initial source is separately required |
| Backend reload | API listener may be a new child; stable parent and selected SHA/bootstrap remain required |
| Incompatible frontend/backend | Independent SHA mismatch rejected; fixture-contract differences rejected |
| Unknown/mismatched source | Missing/options refs, HEAD mismatch, foreign repository/origin rejected |
| Dirty initial source | Real Git edit preserved and refused |
| Simultaneous selection | Nonblocking lock refusal recorded without process mutation |
| Stale/unreadable/replaced backup | Rejected before stop; archive decode is validation only |
| Failed transition/recovery | One candidate start, one recovery; failure evidence and old pointer retained |
| Verified rollback | Simulated readiness and previous pointer restoration, no data restore/deletion |
| Failed-attempt history | Subsequent successful simulation retains earlier failure and legacy journal |
| Unknown listener/process owner | Missing PID/inode, foreign cgroup, wildcard bind, PID/unit replacement rejected |
| No operational access | DSN negatives, isolated env and read-only SQL probe tests; no creation/migration path |

The workflow is included in exact-head backend CI; frontend CI also runs safety assertions, TypeScript, lint, production build and isolated browser regressions. See the [PR #83 check results](https://github.com/johnd-creator/reliability-knowledge-starter/pull/83/checks) for the final commit and run identities. Merge requires both jobs PASS on the final head, no blocking review, unchanged reviewed main and no out-of-scope diff. Post-merge CI is dispatched against the actual merge commit and checked independently. A failed gate blocks merge; CI is not evidence of a live source transition.

## Review findings and corrections

- Initial test adaptation exposed outdated signatures/missing simulated active metadata; fixtures were updated for the explicit ref and immutable-history contract. Failed logs remain private. Final94 tests pass.
- Independent source review found that the frontend status exposes `engineering_data`, not the backend `source` field. Provenance checks now use each actual contract; a focused regression covers the real field names.
- Recovery initially checked/stopped one unit before validating the other. Both are now inspected first; a negative test proves neither process stops on a foreign second unit.
- Exact controller helper hashes and runtime PID/start-time observations are checked; replaced identities fail closed. No broad warning/dirty-state bypass was added.
- Conservative compatibility refusals and future controller installation are explicit limitations, not claims that arbitrary schema-changing feature branches can be selected safely.

## Preservation and next action

Read-only local process/listener snapshots and protected-file hashes are retained privately in `/tmp/nadi-local-dev-02`. No runtime controller/configuration is installed or changed. No DB, session, collector, Mart, operational API, container, freshness-policy or external QA action is performed. Original PNGs, workbook, worktrees and backups are retained. Runtime proof is process/source/file preservation, not a new database-content audit or live-cutover claim.

PR #75–#81 are left unchanged. After PR #83 merge and post-merge CI verification, close issue #84 only with links to the final implementation and CI evidence. Stop this infrastructure task. **Next action: resume PdM product development.** The first future live source selection remains separately authorized.
