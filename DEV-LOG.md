# NADI development log

Append-only milestone history, established 2026-10-10. Earlier events below are
retrospective entries citing their original reports; unknown outcomes remain UNKNOWN.
Append a correction/superseding event rather than changing an earlier result.

IMPLEMENTED = artifact exists at named revision; TESTED = specified checks ran;
MERGED = GitHub integration verified; VISIBLE = observed in named runtime;
ACCEPTED = named authority accepted a stated scope. These milestones are independent.
CI PASS alone does not prove runtime visibility, PO acceptance or operational UAT.
A developer acceptance report is not a Product Owner signature.

## NADI factual V1 / Phase0

- **Date:** 2026-08-22 (historical release; reconciled 2026-10-10)
- **Task ID:** NADI factual V1 / Phase0
- **Objective:** Freeze accepted factual scope
- **Branch:** task/nadi-002-asset-reliability-workspace
- **Commit SHA:** af1d9bde22dd37c96ec8156496d209532c0f601a
- **PR:** [1](https://github.com/johnd-creator/reliability-knowledge-starter/pull/1) (see evidence for multi-PR scope)
- **Implementation Status:** IMPLEMENTED — factual routes only
- **Test Status:** TESTED — historical backend/frontend/contracts and nine-route QA PASS
- **CI Status:** UNKNOWN for original exact head in this audit
- **Merge Status:** MERGED — PR1; v0.1.0-rc.1
- **Development Visibility:** VISIBLE in historical release QA; not a new browser test
- **Product Owner Acceptance:** Release QA ACCEPTED within factual scope; no separate PO signature established here
- **Remaining Blockers:** Gated health/risk/failure semantics; platform not globally complete
- **Next Action:** Preserve factual semantics; continue official roadmap

Evidence: [original report](reliability-cockpit/docs/nadi-v1-release-candidate.md). Current merge reconciliation: [audit](docs/NADI-DOC-FOUNDATION-01.md).

## NADI-IDN-002B-R1-FIX-01 / NADI-P1-FRESH-GOV-03

- **Date:** 2026-10-08 (historical pilot)
- **Task ID:** NADI-IDN-002B-R1-FIX-01 / NADI-P1-FRESH-GOV-03
- **Objective:** Record governed pilot and provisional activity monitoring
- **Branch:** codex/nadi-idn002b-r1-runtime-promotion; codex/nadi-p1-fresh-gov-03
- **Commit SHA:** 685a721d5c5510eee3ae904f798d2c65f98546e8; e67c641e23214bf8851a05d312e1426c1e471ec3
- **PR:** [23](https://github.com/johnd-creator/reliability-knowledge-starter/pull/23), [28](https://github.com/johnd-creator/reliability-knowledge-starter/pull/28) (see evidence for multi-PR scope)
- **Implementation Status:** IMPLEMENTED — bounded real pilot and activity policy
- **Test Status:** TESTED — recorded pilot preservation and GOV03 local checks; readiness remains UNKNOWN
- **CI Status:** UNKNOWN for original exact heads in this audit
- **Merge Status:** MERGED — PR23/28
- **Development Visibility:** VISIBLE in recorded stored-data API/browser acceptance; not re-certified now
- **Product Owner Acceptance:** Owner monitoring authorization recorded in GOV03; not final Phase1 acceptance
- **Remaining Blockers:** Condition freshness; review outcomes UNKNOWN; original checkpoint/expiry retained
- **Next Action:** Accountable operator records separate reviews; no policy execution in docs task

Evidence: [original report](reliability-cockpit/docs/nadi-p1-fresh-gov-03.md). Current merge reconciliation: [audit](docs/NADI-DOC-FOUNDATION-01.md).

## NADI-PH2-01 / Bundles B–E

- **Date:** 2026-10-09 (historical Engineering foundation)
- **Task ID:** NADI-PH2-01 / Bundles B–E
- **Objective:** Establish cases, inspections, independent review, audit and local recommendation foundation
- **Branch:** codex/nadi-phase2-overnight-bundle-01; later task branches in bundle reports
- **Commit SHA:** 02e887c56057611f112b7b652ba9a9aee8b382ea (PR29); f54643f3510bf505628a1400024784faab46e496 (through PR61)
- **PR:** [29–61](https://github.com/johnd-creator/reliability-knowledge-starter/pull/29) (see evidence for multi-PR scope)
- **Implementation Status:** IMPLEMENTED — merged foundations; operational writer activation OFF
- **Test Status:** TESTED — source-free/disposable acceptance in bundle reports
- **CI Status:** SUCCESS for final PR61/main run37921470470; not inferred for every historical PR
- **Merge Status:** MERGED — PR29–61 verified
- **Development Visibility:** VISIBLE development prototypes and isolated QA; no real engineer UAT claim
- **Product Owner Acceptance:** UNKNOWN — development acceptance is not actual engineer/PO UAT
- **Remaining Blockers:** Operational identity/custody, application writer/storage approvals, fields and UAT
- **Next Action:** Follow scoped activation gates and engineer validation

Evidence: [original report](reliability-cockpit/docs/nadi-e-integration-02.md). Current merge reconciliation: [audit](docs/NADI-DOC-FOUNDATION-01.md).

## NADI-E-INTEGRATION-02

- **Date:** 2026-10-09 (historical local login)
- **Task ID:** NADI-E-INTEGRATION-02
- **Objective:** Integrate secure local username/password and QA UI
- **Branch:** codex/nadi-ph2-e10-local-login-handoff
- **Commit SHA:** 1ec149de2d1acd4113987364e1f96c790bfaf63e (tested); f54643f3510bf505628a1400024784faab46e496 (merge)
- **PR:** [60](https://github.com/johnd-creator/reliability-knowledge-starter/pull/60), [61](https://github.com/johnd-creator/reliability-knowledge-starter/pull/61) (see evidence for multi-PR scope)
- **Implementation Status:** IMPLEMENTED — local accounts, versioned sessions and development login
- **Test Status:** TESTED — historical Cockpit687/Maximo181/PI191/contracts14, frontend143/browser40+legacy25 PASS
- **CI Status:** SUCCESS — PR61/main run37921470470
- **Merge Status:** MERGED — PR60/61
- **Development Visibility:** VISIBLE in HTTPS isolated acceptance; current primary preview retains login
- **Product Owner Acceptance:** UNKNOWN for actual engineer UAT; developer acceptance PASS
- **Remaining Blockers:** Real QA NO_GO; global enforcement not activated
- **Next Action:** Preserve QA security; global login design only under UX-08

Evidence: [original report](reliability-cockpit/docs/nadi-e-integration-02.md). Current merge reconciliation: [audit](docs/NADI-DOC-FOUNDATION-01.md).

## NADI-DEV-LIVE-01

- **Date:** 2026-10-09 (historical live development)
- **Task ID:** NADI-DEV-LIVE-01
- **Objective:** Persist isolated QA and support HMR without changing operational services
- **Branch:** codex/nadi-dev-live-01
- **Commit SHA:** 28197f41d044a55cf247ffdd916ac00486644437 (pre-consolidation checkpoint)
- **PR:** [62](https://github.com/johnd-creator/reliability-knowledge-starter/pull/62) (see evidence for multi-PR scope)
- **Implementation Status:** IMPLEMENTED — persistent development launcher/fixture
- **Test Status:** TESTED — historical 697 backend:474PASS/223SKIP; frontend143, browser40+12 checks
- **CI Status:** Earlier checkpoint not re-queried; successor exact head CI SUCCESS
- **Merge Status:** OPEN / UNMERGED — same PR62 updated by DEV-RESET
- **Development Visibility:** Historical13035 visible; address superseded by HTTPS3000
- **Product Owner Acceptance:** UNKNOWN; developer acceptance only
- **Remaining Blockers:** Operational activation remains separate; superseded startup must not restart13035
- **Next Action:** Use DEV-RESET runbook; retain data/history

Evidence: [original report](https://github.com/johnd-creator/reliability-knowledge-starter/blob/0bfea1273f97ce96a08ef147b44f804aecb428d1/reliability-cockpit/docs/nadi-dev-live-01.md). Current merge reconciliation: [audit](docs/NADI-DOC-FOUNDATION-01.md).

## NADI-DEV-RESET-01 / UX-01

- **Date:** 2026-10-09 (consolidation; re-observed 2026-10-10)
- **Task ID:** NADI-DEV-RESET-01 / UX-01
- **Objective:** One primary secure frontend with controlled preview and rollback
- **Branch:** codex/nadi-dev-live-01
- **Commit SHA:** 6197b4599c09626f17682d81d547f4b838909ec1 (implementation); 0bfea1273f97ce96a08ef147b44f804aecb428d1 (active head)
- **PR:** [62](https://github.com/johnd-creator/reliability-knowledge-starter/pull/62) (see evidence for multi-PR scope)
- **Implementation Status:** IMPLEMENTED — HTTPS3000; redundant13035 retired; retained records/worktree
- **Test Status:** TESTED — 707backend:484PASS/223SKIP; frontend143; published69 browser checks; historical private completion adds20 post-rollback checks
- **CI Status:** SUCCESS — exact PR62 head, run37940329956
- **Merge Status:** OPEN / UNMERGED — independently verified
- **Development Visibility:** VISIBLE — read-only status: exact head clean, factual/QA backends AVAILABLE; historical HMR/rollback PASS
- **Product Owner Acceptance:** Development acceptance PASS; actual PO/engineer UAT UNKNOWN
- **Remaining Blockers:** PR62 review/merge; real operational QA gates; self-signed local certificate
- **Next Action:** Review PR62 separately; do not switch active source during documentation

Evidence: [original report](https://github.com/johnd-creator/reliability-knowledge-starter/blob/0bfea1273f97ce96a08ef147b44f804aecb428d1/reliability-cockpit/docs/nadi-dev-reset-01.md). Current merge reconciliation: [audit](docs/NADI-DOC-FOUNDATION-01.md).

## NADI-PDM-REQ-01

- **Date:** 2026-10-09 (requirements; reconciled 2026-10-10)
- **Task ID:** NADI-PDM-REQ-01
- **Objective:** Capture engineer-reported needs and validation gates
- **Branch:** codex/nadi-pdm-req-01
- **Commit SHA:** 89cfa0e50dbdaa1fa158558c890cc512c049b60f
- **PR:** [63](https://github.com/johnd-creator/reliability-knowledge-starter/pull/63) (see evidence for multi-PR scope)
- **Implementation Status:** IMPLEMENTED documentation only; no new PdM functionality
- **Test Status:** TESTED documentation checks reported; engineering field validation pending
- **CI Status:** SUCCESS — exact PR63 head, run37932325576
- **Merge Status:** OPEN / UNMERGED
- **Development Visibility:** GitHub candidate documents visible; no runtime change
- **Product Owner Acceptance:** UNKNOWN; all Q01–Q10 remain PENDING_ENGINEER_VALIDATION
- **Remaining Blockers:** Samples, PD meaning, point/instrument/cadence/comparability/threshold and UAT approvals
- **Next Action:** Reconcile without dropping R/Q/M gates; no parser or source acquisition

Evidence: [original report](https://github.com/johnd-creator/reliability-knowledge-starter/blob/89cfa0e50dbdaa1fa158558c890cc512c049b60f/reliability-cockpit/docs/nadi-pdm-requirements-01.md). Current merge reconciliation: [audit](docs/NADI-DOC-FOUNDATION-01.md).

## NADI-DOC-FOUNDATION-01 — documentation delivery checkpoint

- **Date:** 2026-10-10, Asia/Jakarta.
- **Task ID:** NADI-DOC-FOUNDATION-01.
- **Objective:** Establish permanent product context, requirements, design specifications and development governance without runtime changes.
- **Branch:** codex/nadi-doc-foundation-01, separate documentation worktree.
- **Commit SHA:** `80bd3cb7e5aa2d4c1f817cb00b1bf39be0ebf7b4` implements the documentation foundation; this appended delivery record follows it. Base main: `f54643f3510bf505628a1400024784faab46e496`.
- **PR:** [#64](https://github.com/johnd-creator/reliability-knowledge-starter/pull/64).
- **Implementation Status:** IMPLEMENTED — 14 Markdown files; context, PRD, design system, 11 page specs, reference manifest, authority/audit, UX track and onboarding. No application implementation.
- **Test Status:** TESTED — relative links/page-section completeness, historical-content and AGENTS preservation, Markdown diff checks PASS; all 18 baseline NADI/fixture container IDs/start times, development PIDs/status and XLS hash retained. No new runtime/browser/DB mutation tests.
- **CI Status:** PENDING at this checkpoint; explicit existing source-free GitHub workflow dispatch follows the final documentation commit. Exact head/result remains visible in PR64 checks; prior main/PR62/PR63 SUCCESS is separate evidence.
- **Merge Status:** OPEN / UNMERGED; no automatic merge.
- **Development Visibility:** Documents visible on PR64; documentation branch is not the running frontend. HTTPS3000 remains clean PR62 head `0bfea1273f97ce96a08ef147b44f804aecb428d1` with factual and isolated QA backends AVAILABLE.
- **Product Owner Acceptance:** PENDING — no new PO visual sign-off or actual engineer UAT claimed.
- **Remaining Blockers:** Three original screenshots missing; detailed design/token/navigation acceptance; PR63 engineer validation; operational activation gates; Phase1 review outcomes UNKNOWN. Task continuation after truncated section12 unavailable.
- **Next Action:** Review PR64 and exact-head CI; obtain original reference files and record approvals; reconcile PR62/63 when separately authorized, following the preservation plan.

Evidence: [foundation audit and reconciliation](docs/NADI-DOC-FOUNDATION-01.md),
[reference manifest](docs/design/references/README.md),
[official roadmap](plans/NADI-ROADMAP.md). This is documentation delivery, not
completion of UX-02–09 implementation or operational deployment.


## NADI-DOC-FOUNDATION-01-FIX-02 — official reference reconciliation

- **Date:** 2026-10-10, Asia/Jakarta.
- **Task ID:** NADI-DOC-FOUNDATION-01-FIX-02.
- **Objective:** Use the PO-confirmed existing root PNGs as official references without duplication.
- **Branch:** codex/nadi-doc-foundation-01, existing clean documentation worktree.
- **Commit SHA:** Base `dc07ab9015b5b7214941a5739cc7765269f680e3`; this entry's introducing commit records FIX-02, with final exact HEAD in PR64.
- **PR:** [#64](https://github.com/johnd-creator/reliability-knowledge-starter/pull/64), same PR.
- **Implementation Status:** IMPLEMENTED documentation correction; all five reference mappings AVAILABLE, no image bytes changed or added.
- **Test Status:** Five visual mappings, PNG signatures/chunk CRCs/decompression, dimensions, byte sizes and SHA256 verified against tracked main; documentation link/diff checks recorded in PR64 handoff.
- **CI Status:** Previous exact-head run38006800506 SUCCESS; FIX-02 exact-head workflow is dispatched after push and linked in PR64 (workflow_dispatch may leave PR check rollup empty).
- **Merge Status:** PR64 OPEN / UNMERGED; PR62/63 independently rechecked OPEN at unchanged heads.
- **Development Visibility:** Documentation update only; no application/browser or runtime acceptance claimed or changed.
- **Product Owner Acceptance:** Explicit FIX-02 approval of existing PNG references and mapping; not acceptance of implemented UI, engineering semantics or UAT.
- **Remaining Blockers:** No image/ZIP blocker remains. Token/contrast review, implemented UI visual acceptance, engineer-validation and operational gates remain.
- **Next Action:** Review updated PR64 and exact-head CI; use existing PNG links for later UI tasks; no automatic merge.

Evidence: [official reference manifest](docs/design/references/README.md),
[page specifications](docs/design/NADI-UI-SPEC.md). The earlier missing-JPG and
FIX-01 ZIP requirement is superseded by the Product Owner's explicit FIX-02
instruction; earlier log checkpoints remain unchanged.


## NADI-DOC-FOUNDATION-FIX-03 — latest-main conflict reconciliation

- **Date:** 2026-10-10, Asia/Jakarta.
- **Task ID:** NADI-DOC-FOUNDATION-FIX-03.
- **Objective:** Resolve PR64 conflicts while preserving PR62/63 and product documentation.
- **Branch:** codex/nadi-doc-foundation-01; clean separate documentation worktree before merge.
- **Commit SHA:** Previous `403cad8cea1a4d1606484e71136f8843abd4ab96`; merged main `0cb26882c870185a54282df3af4a136f31702b67`; introducing merge commit recorded in PR64.
- **PR:** [#64](https://github.com/johnd-creator/reliability-knowledge-starter/pull/64).
- **Implementation Status:** Documentation reconciliation in three actual conflicting roadmap/status files, with current onboarding/PRD references updated. Main's application/runtime bytes preserved.
- **Test Status:** Conflict-marker, diff, relative-link, PNG integrity/provenance, eleven-page and phase/UX/PdM continuity checks in the PR handoff.
- **CI Status:** New exact-HEAD backend/frontend CI follows push; run/results linked in PR64. Prior runs remain historical.
- **Merge Status:** PR62/63 MERGED; main merged into PR64 branch; PR64 stays OPEN pending review.
- **Development Visibility:** No runtime source switch, configuration change, restart or database action.
- **Product Owner Acceptance:** Reconciliation authorized by FIX-03; no new UI/UAT or operational acceptance inferred.
- **Remaining Blockers:** PR64 review and CI/mergeability verification; existing engineering/visual activation gates unchanged.
- **Next Action:** Review exact-HEAD CI and mergeability; no automatic merge of PR64.

Evidence: [reconciliation audit](docs/NADI-DOC-FOUNDATION-01.md),
[official roadmap](plans/NADI-ROADMAP.md), [repository status](plans/REPOSITORY-STATUS.md).


## NADI UX Bundle A — DEV-SYNC / UX-02 / UX-03 / UX-04 / REVIEW-01

- **Date:** 2026-10-10, Asia/Jakarta.
- **Task ID:** NADI UX Bundle A.
- **Objective:** Implement one integrated frontend foundation, compatible navigation and factual Executive Overview, then self-review and correct regressions.
- **Branch:** codex/nadi-ux-bundle-a; isolated worktree from verified main.
- **Commit SHA:** Main `963e7a8bf0b2a7cf62b1ee8a5661c95d62df7108`; previous serving `0bfea1273f97ce96a08ef147b44f804aecb428d1`; functional candidate `ab089a88a2a4be6cffb58857fbf30e8b56b84d3e`. Final introducing documentation/test-harness HEAD is recorded in the PR/exact runtime handoff.
- **PR:** One integrated PR against main; final URL/checks in the task handoff.
- **Implementation Status:** IMPLEMENTED UX-02/03/04; existing frontend/contracts preserved. Review corrections include table containment, landmarks, breadcrumb, density, development-indicator overlap and honest legacy loading/identity behavior.
- **Test Status:** TESTED — TypeScript/scoped lint/build/safety,143 existing frontend assertions,33 new UX checks,707 backend discovered/484PASS/223 optional SKIP,105 browser checks and18 HMR/source-rollback checks. Exact public screenshots use synthetic browser fixtures.
- **CI Status:** PENDING at this introducing entry; final exact release HEAD results are maintained in the PR check rollup and task handoff, independently of local tests/runtime visibility.
- **Merge Status:** PR62/63/64 MERGED; Bundle A candidate remains UNMERGED pending review.
- **Development Visibility:** VISIBLE at https://localhost:3000 through the supported source-selection launcher; accurate detached source/full SHA/dirty/backend/fixture status. Source rollback to reviewed main and re-selection preserve HTTPS session and exact old QA records.
- **Product Owner Acceptance:** PENDING final visual, token and Engineering placement review; implementation authorization/reference selection is not UI acceptance.
- **Remaining Blockers:** No implementation-critical finding remains; PO review/merge decision, existing engineering validation/operational activation and UNKNOWN Phase1 operator-review outcomes remain separate gates.
- **Next Action:** Review exact-head PR/CI and visible candidate, record PO decision; no automatic merge or UX-05–09 expansion.

Evidence: [Bundle A implementation/review](reliability-cockpit/docs/nadi-ux-bundle-a.md),
[official roadmap](plans/NADI-ROADMAP.md), [development source/rollback runbook](reliability-cockpit/docs/nadi-dev-reset-01.md).
Original images/workbook, persistent records and all operational services remain preserved.


## NADI UX Bundle B — B0 / UX-05 / UX-06 / UX-07 / B4

- **Date:** 2026-10-10, Asia/Jakarta.
- **Task ID:** NADI UX Bundle B.
- **Objective:** Implement Asset Health, PdM Center, Recommendations and Action Board using existing contracts, then review, repair and prepare the single frontend preview.
- **Branch:** codex/nadi-ux-bundle-b, clean isolated implementation worktree.
- **Commit SHA:** Verified main `160737b3bfaeac94f4e8093b8566ca0e5d3585c9`; prior serving `23b6a413f6d4f9e91afbcc631d4ab7d3d10d1858`; functional candidate `0df4b47b951013aa03ae1bb97fad7e4167bb474e`. This introducing evidence commit follows it; final exact release HEAD is in the PR/task handoff.
- **PR:** One integrated Bundle B PR against main; URL/exact-head checks in final delivery handoff.
- **Implementation Status:** IMPLEMENTED UX-05/06/07 — six-section factual detail and authenticated synthetic QA product registers/detail/history/board, with existing gated commands reused.
- **Test Status:** TESTED — TypeScript/lint/build/safety,143 existing frontend +43 UX checks,707 backend discovered/484PASS/223 optional SKIP,14 contracts,105 Bundle A browser,129 Bundle B browser and18 HMR/rollback checks; fifteen sanitized screenshots inspected.
- **CI Status:** Local checks PASS; final exact release HEAD CI follows push and is verified independently in PR checks/task handoff. This entry does not infer CI from local/runtime checks.
- **Merge Status:** PR65 MERGED; Bundle B UNMERGED pending senior/PO review. No automatic merge.
- **Development Visibility:** VISIBLE at https://localhost:3000 through supported launcher, matching clean source/backend/launch SHA; rollback to main and candidate re-selection preserve existing Secure session and exact persisted records. Final release serving SHA is verified in handoff.
- **Product Owner Acceptance:** PENDING — self-review and implementation authorization do not establish visual approval or engineer UAT.
- **Remaining Blockers:** No known critical/high implementation finding remains within the scoped review. Q01–Q10, operational methods/writer/identity/custody/linkage, actual engineer UAT and PO review remain separate gates. Phase1 operator-review outcomes UNKNOWN; original deadlines unchanged.
- **Next Action:** Senior/PO review of PR/CI/preview; bounded engineer validation before operational PdM activation; no automatic global login or merge.

Evidence: [implementation/self-review](reliability-cockpit/docs/nadi-ux-bundle-b.md),
[responsive screenshots](docs/design/ux-bundle-b/README.md),
[official roadmap](plans/NADI-ROADMAP.md). Original images/workbook, records,
all operational services, prior worktrees and rollback resources remain preserved.

## NADI-ENG-BUNDLE-A — B0 governance/baseline — 2026-10-11

- **Date:** 2026-10-11, Asia/Jakarta.
- **Task ID:** NADI-ENG-BUNDLE-A / B0.
- **Objective:** PO-directed Case UX and Engineering Advisory/Distribution traceability before implementation.
- **Branch:** codex/nadi-eng-bundle-a; separate clean worktree.
- **Commit SHA:** Base main cc90fc73bea6ae399383d8538035c6454dc7e65a; introducing governance commit in Git history.
- **PR:** New integrated Engineering PR to be opened; PR67 remains independently OPEN.
- **Implementation Status:** PLANNED ENG-UX-01/02, ADV-01/02/03; ADV-04 FUTURE/GATED.
- **Test Status:** Baseline ownership/fixture/clean source verified; feature tests pending.
- **CI Status:** PR67 exact-head backend/frontend SUCCESS; Engineering CI pending, not inferred.
- **Merge Status:** Engineering UNMERGED.
- **Development Visibility:** Existing PR67 preview remains at 8658c2fbd00bb78f1d8ee2b4462ccece4200a30e, clean; new work not yet visible.
- **Product Owner Acceptance:** Binding requirement authorization from supplied NADI-ENG-BUNDLE-A task; implementation acceptance PENDING.
- **Remaining Blockers:** Inspect eligible upstream review, storage reuse and trusted recipient policy before delivery; operational channels/UAT remain gated.
- **Next Action:** Implement bounded authenticated SYNTHETIC QA flow and verify security/regression.

Phase 2/4 PARTIAL; freshness review/checkpoint/expiry remain separate unchanged tasks.

## 2026-10-11 — NADI-ENG-BUNDLE-A delivery / autonomous review

Date: 2026-10-11 (Asia/Jakarta)
Task ID: NADI-ENG-BUNDLE-A
Objective: structured Engineering Cases and governed QA advisory recipient experience.
Branch: codex/nadi-eng-bundle-a
Commit SHA: implementation `2a7678d82f6f0e8769a03ca09857c59f2f37f338`; delivery docs may advance PR HEAD.
PR: [#68](https://github.com/johnd-creator/reliability-knowledge-starter/pull/68)
Implementation Status: IMPLEMENTED — ENG-UX-01/02, ADV-01/02/03; ADV-04 PLANNED.
Test Status: TESTED — 161 disposable PostgreSQL backend/HTTPS tests, zero skips; frontend assertions, TypeScript/lint/build; 31 Engineering + 102 Bundle A + 129 Bundle B browser checks. Initial SQLite 97 pass/58 skip is distinct. Advisory browser fixtures are DEMO; durable backend acceptance is disposable-only.
CI Status: backend/frontend PASS on exact implementation `2a7678d82f6f0e8769a03ca09857c59f2f37f338` ([run](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38072796251)); final delivery-document PR exact-head status verified independently at handoff.
Merge Status: NOT MERGED; PR #67 remains independent OPEN.
Development Visibility: VISIBLE Case/Recommendation/Action Board QA on HTTPS 3000. Advisory persistence/inbox BLOCKED_SCHEMA_PREREQUISITE in unchanged persistent QA store. New APIs and controls fail closed; fixture screenshots are not runtime persistence proof.
Product Owner Acceptance: PENDING; engineer UAT/operational distribution PENDING.
Remaining Blockers: automatic approval review denied persistent QA constraint expansion; organizational recipient identity and real distribution remain future gated.
Next Action: explicit authorization decision for the existing QA constraint, followed by persistent advisory publication/receipt UAT; no operational activation.
Evidence: [implementation/self-review](reliability-cockpit/docs/nadi-eng-bundle-a.md), [responsive evidence](reliability-cockpit/docs/evidence/nadi-eng-bundle-a/README.md). Official backup and rollback to `8658c2fbd00bb78f1d8ee2b4462ccece4200a30e` verified. All 35 original container IDs/start times, 481 non-account rows, 39 original sessions, three account grants/credentials, workbook and PNG hashes preserved; normal login timestamp changes are documented.
