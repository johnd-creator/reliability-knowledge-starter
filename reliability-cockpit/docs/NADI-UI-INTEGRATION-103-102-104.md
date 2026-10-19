# NADI-UI-INTEGRATION-103-102-104

Prepared 2026-10-19 for FR-01–FR-05 and FR-10. Consolidate the reviewed UI and
recovery source without changing laptop runtime or product behavior.

## Immutable inputs and ancestry

| Input | SHA | Dependency |
|---|---|---|
| Main baseline | `c7930694187b61ffa6dae90e6a14938e7564c3e7` | PR101 included |
| PR103 controller recovery | `1ec93d6f3507321617903d169451d77fdcc1216e` | Main baseline |
| PR102 Design System V2 | `260c4f9f5f9a17aea3b36476ca4a0e202069e19d` | Main baseline |
| PR104 Experience Rework | `fc33515a3cd0ec4bd9fad81c59e65babe397c2b3` | PR102 head |

Use a consolidation branch beginning at PR104 and merge PR103 into it. Resolve
only the DEV-LOG conflict, retaining both histories verbatim. PR102 is already an
ancestor of PR104; do not cherry-pick/squash its commits again. The GitHub PR to
main must use a merge commit so all three reviewed heads remain ancestors of
main. Preserve source branches; do not close old PRs before integration is verified.

## Reconciliations

- DEV-LOG retains the original PR102 and PR103 entries; a dated integration
  checkpoint records their historical status separately from current evidence.
- The [paired lifecycle runbook](NADI-UX-V2-PAIRED-UPGRADE-RUNBOOK.md) records observed
  controller103/application104 and removes the obsolete recipe from current use.
- Both frontend workflow additions survive: controller recovery tests and the
  Experience browser suite. Exact-head checkout/assertions, disposable PostgreSQL,
  auth/session/CAS/reviewer guards and all existing tests remain intact.
- Original application/controller code and screenshot evidence are preserved.
  This preparation adds no endpoint, migration, dependency or product feature.

## Validation gates

The prior isolated union of the same runtime code passed 530 backend tests
(395 pass / 135 local disposable-PostgreSQL skips), 14 canonical contracts,
15 frontend check groups, lint/types/build and 1,300 fixture browser assertions:
107 Experience, 575 PdM, 399 localization, 67 Integration, 96 Reports, 56 login/logout.
The pre-existing EngineeringWorkspace.tsx:32 effect-dependency warning remains.
The 20 compatibility surfaces and dependency sections match main at the inputs.

Before publication, rerun focused hermetic controller/contract tests and validate
the preserved histories, final diff, workflow guards and compatibility. Runtime
code must remain byte-identical to that tested union; documentation differences
must be scoped and reviewed. Do not represent PostgreSQL skips as passes.

Before merge, require terminal success of both NADI Engineering candidate jobs on
the exact integration head, including disposable PostgreSQL tests with no skips.
Review job logs, current main, PR mergeability, reviews and any required checks;
resolve new failures without weakening guards. If main changes materially, rebase
by ordinary ancestry-preserving integration and requalify the new exact head.

After normal merge, dispatch that same workflow on main, require terminal success
at the actual merge SHA, verify all original heads are ancestors, and reconcile
the source PR statuses. Capture final URLs/SHAs in the PR handoff. A source merge
is not a preview handover. Do not delete any branch, change protection or deploy.

## Runtime preservation and acceptance

Read-only baseline 2026-10-19 11:52 UTC: serving frontend/API PR104; installed
controller and bootstrap PR103; same existing development fixture; 35 container
identities/states preserved. Main control checkout's compose.dev.yaml and
23496711.xls changes and preview next-env.d.ts are unrelated and remain untouched.
Recompare their hashes, tracked serving source, PIDs/listeners and containers at
completion. Do not read/use session cookies, create credentials or mutate data.

The Product Owner accepted the existing development appearance and explicitly
authorized source candidate commit/push and merge after review/CI. The authority
excludes deploy, source replacement, service/collector restarts and auth/database/
session changes. F03 operational NO-GO, Phase1 mapping/freshness gates, engineer
method/threshold/UAT and operational activation remain unchanged.

At this preparation checkpoint integration is PENDING final exact-head CI and
normal merge. Final source status is established by GitHub PR/main and post-merge
CI evidence, not by this pre-merge document.
