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


## NADI UX Bundle C — Stage A / Bundle B development acceptance

- **Date:** 2026-10-10, Asia/Jakarta.
- **Task ID:** NADI-UX-BUNDLE-C / Stage A.
- **Objective:** Finalize Bundle B under explicit provisional PO approval and synchronize merged main safely.
- **Branch:** PR66 codex/nadi-ux-bundle-b; serving checkout detached.
- **Commit SHA:** Verified PR head `c840d88f360a24263550b665842b42edbded2e07`; merged main `cc90fc73bea6ae399383d8538035c6454dc7e65a`.
- **PR:** [#66](https://github.com/johnd-creator/reliability-knowledge-starter/pull/66).
- **Implementation Status:** Existing Bundle B implemented; merge metadata changes only, identical tree.
- **Test Status:** Exact-head backend/frontend CI rechecked SUCCESS; 21 main-synchronization checks PASS, including same Secure session, retained exact records and unchanged container identities/start times.
- **CI Status:** [38026443639](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38026443639) SUCCESS at PR head; merged tree equals that candidate.
- **Merge Status:** MERGED 2026-10-10T08:59:19Z; match-head controlled merge authorized by the Product Owner's Bundle C directive. Branch/worktrees preserved.
- **Development Visibility:** Merged main VISIBLE at https://localhost:3000 through official launcher before starting Bundle C; matching source/backend/launch SHA, clean and both backends AVAILABLE.
- **Product Owner Acceptance:** DEVELOPMENT ACCEPTED provisionally; final visual review Monday, 12 October 2026, with polish corrections allowed. No operational method/UAT acceptance inferred.
- **Remaining Blockers:** No merge/synchronization blocker; final visual decisions, Q01–Q10 and operational UAT remain separate pending gates.
- **Next Action:** Existing QA login presentation polish and UX-09 readiness; no global authentication or Phase 3 activation.

Evidence: [Bundle C readiness](reliability-cockpit/docs/nadi-ux-bundle-c.md).
Original logs above remain historical; this entry records the later PO decision and merge.

## NADI UX Bundle C — UX-08 implementation / UX-09 preparation

- **Date:** 2026-10-10, Asia/Jakarta.
- **Task ID:** NADI-UX-BUNDLE-C / Stages B–C.
- **Objective:** Polish the existing QA login with NADI identity, V1 tokens and accessible responsive states; prepare visual review evidence.
- **Branch:** codex/nadi-ux-bundle-c, isolated worktree from verified merged main.
- **Commit SHA:** Base `cc90fc73bea6ae399383d8538035c6454dc7e65a`; functional candidate `64eb1f73152267d454056abf798aed5bf89f9b27`. Final evidence HEAD/CI and serving SHA are in PR/task handoff.
- **PR:** New Bundle C PR against latest main; final URL/checks in handoff, no automatic merge.
- **Implementation Status:** IMPLEMENTED UX-08 presentation of existing QA login; UX-09 PREPARATION, not final PO visual acceptance. Backend/session policy and global access unchanged.
- **Test Status:** TESTED — local TypeScript/lint/build/safety, 195 frontend assertions and 96 login browser checks PASS; fourteen sanitized screenshots inspected. Bundle A browser 105 PASS and Bundle B 129 PASS (330 combined browser checks at exact functional SHA); final evidence-only release/CI independently verified in PR/task handoff.
- **CI Status:** Local validation and final exact-head CI remain independent; final release checks verified after push in PR/task handoff.
- **Merge Status:** Bundle C UNMERGED; PR66 independently MERGED.
- **Development Visibility:** Candidate explicitly selected on the single HTTPS3000 frontend via supported launcher; merged main, previous sources and private backups retained for rollback. Final exact source is in handoff.
- **Product Owner Acceptance:** Login visual approval PENDING; self-review is not PO acceptance. Monday, 12 October 2026 review remains scheduled.
- **Remaining Blockers:** No global enforcement is authorized. Brand copy/language, logo scale, narrow layout and final polish await PO decision; operational Q01–Q10 and UAT remain pending.
- **Next Action:** Senior/PO review of final PR, CI, screenshots and visible login candidate; no automatic Bundle C merge.

Evidence: [readiness report](reliability-cockpit/docs/nadi-ux-bundle-c.md),
[responsive/state screenshots](docs/design/ux-bundle-c/README.md),
[official roadmap](plans/NADI-ROADMAP.md).

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

## 2026-10-11 — NADI-ENG-BUNDLE-A-FIX-01 / persistent QA authorization

Date: 2026-10-11 (Asia/Jakarta)
Task ID: NADI-ENG-BUNDLE-A-FIX-01
Objective: execute PO-authorized existing QA CHECK expansion and prove persistent Advisory/recipient workflow.
Branch: codex/nadi-eng-bundle-a
Commit SHA: executed helper/runtime `01434fb26a29ba726fe59f663ca96d95bfd43c01`; introducing evidence/test commit advances PR HEAD without application-source changes.
PR: [#68](https://github.com/johnd-creator/reliability-knowledge-starter/pull/68)
Implementation Status: IMPLEMENTED — approved original QA helper replaces only kind CHECK; no operational migration or code change.
Test Status: TESTED — 51 actual persistent browser assertions, 18 HTTPS route checks, 161 disposable PostgreSQL backend tests/zero skips; frontend assertions/safety/lint/TypeScript/syntax; nine1440/768/390 screenshots; two private backup clone restores and previous-reader compatibility PASS.
CI Status: baseline01434fb backend/frontend PASS; final evidence-head backend/frontend/build/contracts are independently verified after push in PR checks and final handoff.
Merge Status: NOT MERGED; PR #67 independently OPEN and unchanged.
Development Visibility: VISIBLE at HTTPS3000, clean source/backend/launch01434fb; affected QA API only reloaded, original frontend process preserved. Advisory/inbox capability READY; actual publication/ACK retained after reload/reconnect and deliberate withdrawal.
Product Owner Acceptance: limited conditional schema/execution authority given by PO; Persistent QA Acceptance execution PASS. Actual engineer UAT, PO visual review and operational/production acceptance PENDING.
Remaining Blockers: no persistent-QA schema blocker remains. Organizational recipients/identity, real channels/custody/UAT and operational rollout still separately gated.
Next Action: senior/PO review of unmerged PR #68 and QA evidence; retain expanded CHECK and all records on application rollback. No merge or operational activation without further approval.
Evidence: [FIX-01 report](reliability-cockpit/docs/nadi-eng-bundle-a-fix-01.md), [actual persistent evidence](reliability-cockpit/docs/evidence/nadi-eng-bundle-a-fix-01/README.md). Immediately post-DDL919rows/51sessions unchanged; after E2E864immutable originals/51session rows/three accepted records and account invariants preserved. All35original containers/start times and five PNG/workbook hashes unchanged. Original blocked checkpoint is preserved above; the new explicit authorization resolves that earlier restriction. Phase1 policy/deadlines untouched.

## 2026-10-11 — NADI-ENG-INTEGRATION-01

Date: 2026-10-11 (Asia/Jakarta)
Task ID: NADI-ENG-INTEGRATION-01 / I0–I4
Objective: integrate unmerged Login67 and Engineering68 in one persistent QA candidate.
Branch: codex/nadi-eng-integration-01, new clean worktree from verified latest main.
Commit SHA: base cc90fc73bea6ae399383d8538035c6454dc7e65a; inputs8658c2f/e60ad786; functional browser e4be4d0543b48e730b9f5695573cb2bf4fd6f14f; final release hash in PR/task handoff.
PR: new integration PR against main; final URL in task handoff. PR67/68 independently OPEN.
Implementation Status: IMPLEMENTED — exact source merges and semantic conflicts, existing Login plus Case/Advisory/Inbox/ACK retained.
Test Status: TESTED —203frontend assertions, lint/TypeScript/build,161disposable PostgreSQL tests/zero skips,14contracts; Login96/persistent51/A102/B129 browser checks plus focused inline Login integration, responsive screenshot review and actual source rollback PASS.
CI Status: local PASS; exact release backend/frontend CI independently verified at new PR HEAD after push.
Merge Status: NOT MERGED; neither PR67 nor PR68 merged.
Development Visibility: VISIBLE on soleHTTPS3000 via official launcher. Final source/backend/launch SHA independently checked after release selection; pre-cutover Secure session survives actual rollback and original3QA records remain exact.
Product Owner Acceptance: QA integration/testing authorization; final visual, senior review and real engineer UAT PENDING. Self-review is not Product Owner acceptance.
Remaining Blockers: no QA schema prerequisite; operational identity/recipients/channels/UAT still gated; Phase1 review/checkpoint/expiry remain independent unchanged.
Next Action: senior/PO review integration PR and exact-head CI; no automatic merge or global authentication/Phase3 activation.
Evidence: [integration/self-review](reliability-cockpit/docs/nadi-eng-integration-01.md), [fresh screenshots/results](reliability-cockpit/docs/evidence/nadi-eng-integration-01/README.md). All58original sessions retained with policy-normal monotonic last_seen only,1206immutable baseline rows exact,3accounts,35containers/start times, expanded Advisory/ACK schema, ledger, workbook and five original PNGs preserved. Official private backup fully restored only into a disposable clone; source rollback01434fb demonstrated without DB restoration or deletion.

## 2026-10-11 — NADI-UX-ID-01

Date: 2026-10-11 (Asia/Jakarta)
Task ID: NADI-UX-ID-01 / L0–L5
Objective: Bahasa Indonesia utama tanpa perubahan perilaku/kontrak, plus panduan istilah.
Branch: codex/nadi-ux-id-01; worktree terisolasi `.nadi-dev/ux-id-01`.
Commit SHA: base 09b6d6308a6cc70818292eb71f79733255dcf823; implementation 2abbe61a0973d2cd8ce1d788e7fad525cb0173b6; final delivery HEAD pada PR handoff.
PR: PR baru lokalisasi terhadap main; final number/URL pada task handoff, tidak auto-merge. PR #69 MERGED terverifikasi terpisah.
Implementation Status: IMPLEMENTED L1/L2 — dictionary presentation, seluruh keluarga halaman NADI, status-code mapping, glosarium 41 entri dan contextual help. API/enum/URL/data tersimpan tetap asli.
Test Status: TESTED — TypeScript, lint seluruh presentation (0 errors; 1 existing intentional pinned-editor dependency warning), build, frontend/security assertions,14 contracts; browser komponen terisolasi 1440/768/390, Case→Recommendation→Advisory→Inbox/ACK dan retry/CAS. Local backend 150 tests: 94 pass / 56 PostgreSQL skips, tidak menggantikan PostgreSQL CI.
CI Status: exact-head backend/frontend termasuk PostgreSQL acceptance dan fixture browser diverifikasi setelah push pada PR handoff; tidak diartikan sebagai runtime deployment.
Merge Status: NOT MERGED.
Development Visibility: kandidat belum dipilih; HTTPS 3000 existing tetap bersih di b348235ce6f82c84873a65344ad2ef5fe276987d. Screenshot kandidat adalah QA SINTETIS network-isolated, bukan deployment atau persistence acceptance baru.
Product Owner Acceptance: arah bahasa disetujui dalam task; final wording/visual/senior review dan engineer UAT PENDING.
Remaining Blockers: official launcher switch memerlukan penghentian web+QA API; task ini melarang perubahan layanan/data/deployment QA. Definisi metode/threshold dan operational identity/channel/UAT tetap gated; Phase 1 deadlines unchanged.
Next Action: review PR/screenshot/istilah; source selection hanya melalui mekanisme resmi yang aman pada task runtime terpisah. Tidak merge atau aktivasi operasional otomatis.
Evidence: [implementation/self-review](reliability-cockpit/docs/nadi-ux-id-01.md), [matrix/screenshots](reliability-cockpit/docs/evidence/nadi-ux-id-01/README.md). Read-only before/after fingerprints membuktikan semua rekam/session/schema/grants tepat sama,82 sessions / 3 accounts, 35 container IDs/start times, 34 other worktrees plus this candidate, 5 PNG dan workbook. Existing private backup list readable; historical clone restore evidence referenced, no new restore/DDL.


## 2026-10-11 — NADI-UX-ID-02-FIX-01 — implementation checkpoint

Date: 2026-10-11 (Asia/Jakarta)
Task ID: NADI-UX-ID-02-FIX-01 / F0–F4
Objective: safely preview Indonesian frontend with the existing QA API untouched.
Branch: codex/nadi-ux-id-02-fix-01, separate clean worktree based on PR70 a08da00.
Commit SHA: reviewed functional/final release hashes in fix PR and final handoff; backend b348235 remains pinned.
PR: separate stacked fix PR; PR70 remains independently OPEN.
Implementation Status: IMPLEMENTED — official frontend-only lifecycle and explicit dual-source provenance.
Test Status: TESTED — 43 hermetic lifecycle tests; provenance/refusal assertions, static frontend checks and build PASS; final browser/CI evidence verified independently.
CI Status: PENDING exact-head fix PR checks at this checkpoint.
Merge Status: NOT MERGED.
Development Visibility: PENDING controlled activation and actual runtime evidence; build/CI are not visibility proof.
Product Owner Acceptance: technical activation authorized; visual review, actual engineer UAT and production acceptance PENDING.
Remaining Blockers: actual preflight/readiness gates must pass before frontend-only selection; no authority for API restart/DDL.
Next Action: exact-head CI, official frontend-only preflight/cutover, private live screenshots and preservation verification.
Evidence: [implementation/runbook and evidence boundaries](reliability-cockpit/docs/nadi-ux-id-02-fix-01.md).


## 2026-10-11 — NADI-UX-ID-02-FIX-01 — actual preview checkpoint

Date: 2026-10-11, 16:31–16:35 WIB
Task ID: NADI-UX-ID-02-FIX-01 / F0–F4
Objective: show Indonesian PR70 safely with the existing QA API preserved.
Branch: codex/nadi-ux-id-02-fix-01; final evidence sealed in isolated codex/nadi-ux-id-02-fix-01-release worktree, pushed to the same PR71 head.
Commit SHA: actual functional b6a4981ab9bbfd8c1bf6dca51ced4e1ed2b7c881; final documentation-only release SHA verified separately in PR71/task handoff; backend b348235ce6f82c84873a65344ad2ef5fe276987d.
PR: [71](https://github.com/johnd-creator/reliability-knowledge-starter/pull/71), stacked on independently OPEN unchangedPR70.
Implementation Status: IMPLEMENTED.
Test Status: TESTED —43hermetic lifecycle tests;370fixture browser checks;106actual live checks/30screenshots; rollback preflight PASS.
CI Status: b6a4981 exact-head backend/frontend PASS, run38128497987; final evidence commit CI verified independently after push.
Merge Status: NOT MERGED.
Development Visibility: VISIBLE —soleHTTPS3000, clean approved split source, both backends AVAILABLE; API PID and every cgroup process unchanged.
Product Owner Acceptance: preview activation authorized and technical QA PASS; PO visual/senior review and actual engineer UAT PENDING.
Remaining Blockers: no frontend-only activation blocker. Operational identity/Advisory distribution/global login/PdM remain separately gated.
Next Action: PO localization/visual review; do not merge automatically. Final release source and screenshots reverified through the official frontend-only controller.
Evidence: [actual activation/preservation report](reliability-cockpit/docs/nadi-ux-id-02-fix-01.md#actual-controlled-activation--2026-10-11-1631-wib). 82original sessions and all business records/schema/ledger/audit history/account privileges retained; normal login sessions/security activity append only;35containers/start times and original assets unchanged. No API restart, migration/DDL or business mutation.


## 2026-10-11 — NADI-UX-LOGIN-01 — implementation checkpoint

Date: 2026-10-11 (Asia/Jakarta)
Task ID: NADI-UX-LOGIN-01 / L0–L6
Objective: separate fullscreen QA authentication from Application Shell without activating global access policy.
Branch: codex/nadi-ux-login-01, isolated latest-main worktree.
Commit SHA: exact sealed implementation/release SHA in PR handoff; baseline f8f8f2c9bcf8fc64375c1203b4627ac634dcbe26; QA API b348235ce6f82c84873a65344ad2ef5fe276987d pinned.
PR: separate fullscreen-login candidate; no auto-merge.
Implementation Status: IMPLEMENTED — route groups, shared theme, Indonesian fullscreen form, existing local-session redirect behavior.
Test Status: TESTED — frontend assertions/TypeScript/lint/build, hermetic backend 204 tests (127 PASS / 77 optional SKIP), 14 contracts and responsive actual-component fixture browser; distinct review and corrections documented.
CI Status: exact-head PR CI verified separately after push; not runtime evidence.
Merge Status: NOT MERGED.
Development Visibility: prior clean HTTPS3000 preserved during implementation; controlled frontend-only activation and actual images are separate subsequent handoff gates.
Product Owner Acceptance: requested direction approved; final visual review, real engineer UAT and production acceptance PENDING.
Remaining Blockers: no implementation blocker identified; launcher preflight and exact-head CI must pass before preview; no authority for API restart or DDL.
Next Action: verify CI, official source compatibility/backup/rollback and actual HTTPS login; report exact source and preserve backend/data.
Evidence: [implementation/self-review](reliability-cockpit/docs/nadi-ux-login-01.md), [screenshot boundaries](reliability-cockpit/docs/evidence/nadi-ux-login-01/README.md).


## 2026-10-11 — NADI-UX-LOGIN-01 — actual preview checkpoint

Date: 2026-10-11, approximately 22:06–22:14 WIB
Task ID: NADI-UX-LOGIN-01 / L5–L6
Objective: verify standalone Indonesian login on the one official frontend.
Branch: codex/nadi-ux-login-01; evidence sealed in inactive codex/nadi-ux-login-01-release, pushed to the same PR.
Commit SHA: functional 79dda14ccee487f61452aa599f12d9cc3f0d4c09; final documentation-release SHA verified separately; backend b348235ce6f82c84873a65344ad2ef5fe276987d unchanged.
PR: [73](https://github.com/johnd-creator/reliability-knowledge-starter/pull/73).
Implementation Status: IMPLEMENTED.
Test Status: TESTED —395 network-isolated component checks;102 actual live checks/7 screenshots; invalid credentials separately PASS; original QA rows and old sessions/account privileges preserved; harness alert/async-layout/caption findings corrected and failed attempts retained privately.
CI Status: functional exact-head backend/frontend PASS, run38149741562; final documentation-release exact-head independently checked after push.
Merge Status: NOT MERGED.
Development Visibility: VISIBLE —sole HTTPS3000; standalone login; authorized workspace navigation/logout, factual dashboard access, theme/keyboard, both backends AVAILABLE and approved accurate split-source provenance.
Product Owner Acceptance: implementation direction approved; final visual/wording review and operational/engineer UAT PENDING.
Remaining Blockers: no functional preview blocker. Existing unrelated hook warning; global authentication/operational identity/distribution remain separately gated.
Next Action: seal/push evidence, verify final exact-head CI and select clean release source using the same frontend-only controller; await PO review without auto-merge.
Evidence: [actual screenshots and sanitized summary](reliability-cockpit/docs/evidence/nadi-ux-login-01/README.md#actual-https3000-beforeafter). API PID/cgroup and35containers unchanged;86old sessions, all business records, schema/ledger/grants and assets preserved. Normal login/security audit additions only.


## 2026-10-12 — NADI-P1-FRESH-REVIEW-72H — source-free independent review

Date:2026-10-12(Asia/Jakarta)
Task ID:NADI-P1-FRESH-REVIEW-72H
Objective:review actual72h completion histories and monitoring governance without source acquisition or policy changes.
Branch:codex/nadi-p1-fresh-review-72h, isolated from latest merged main.
Commit SHA:main3ad0da813db13c833ba513c0727becde1c73a081; exact documentation head at PR handoff.
PR:new documentation-only review; no automatic merge.
Implementation Status:documentation/audit only; no application implementation.
Test Status:read-only evidence verification,836WO/322PI log/run outcome crosschecks,857 paired Mart reports, pure9-gate evaluation; Markdown/secret-safety checks separately.
CI Status:documentation validation; GitHub status verified separately; CI never substituted for72h runtime evidence.
Merge Status:NOT MERGED at audit handoff.
Development Visibility:existing frontendf06abce76f8ef9b967ee5b1c2e0802112d77b056 clean/not stale and QA backendb348235 preserved; documentation branch not deployed.
Product Owner Acceptance:72h review authorized; threshold extension/rollback/engineering acceptance NOT GRANTED by this review.
Remaining Blockers:false-alert adjudication, exact historical cutoff/full nine-gate history, per-domain Mart commit clocks,24h review evidence and condition-use-age readiness UNKNOWN.
Next Action:Owner checkpoint12 Oktober20:00WIB; manual hard expiry13Oktober00:00WIB; separate approval required before any policy action.
Evidence:[72h audit](reliability-cockpit/docs/nadi-p1-fresh-review-72h.md). Verdict monitoringPARTIAL/productUNKNOWN, latest8 PASS/1 UNKNOWN; original evidence/pilot/35 containers/preview/assets preserved. Source GET, database mutation, migration, retry, restart and policy action all 0.


## 2026-10-12 — NADI-DEV-UX-STATUS-01 — compact diagnostics candidate

Date: 2026-10-12 (Asia/Jakarta)
Task ID: NADI-DEV-UX-STATUS-01
Objective: replace oversized development banner with a gated topbar disclosure while retaining all diagnostics and integrity checks.
Branch: codex/nadi-dev-ux-status-01, isolated from verified main.
Commit SHA: baseline 2e190c2b51fde50e0467d6d5165ebb1060902867; exact candidate HEAD recorded in PR handoff.
PR: focused compact-status candidate; no automatic merge.
Implementation Status: IMPLEMENTED — development-only slot, accessible dropdown, verified/warning/unavailable states.
Test Status: TESTED — TypeScript/lint/build/product safety, 12 status/gating assertions, existing frontend regression and 455 network-isolated browser checks PASS.
CI Status: exact-head backend/frontend checked separately after push; not substituted for runtime visibility.
Merge Status: NOT MERGED.
Development Visibility: candidate component screenshots only; actual HTTPS3000 retains f06abce76f8ef9b967ee5b1c2e0802112d77b056 and QA backend b348235ce6f82c84873a65344ad2ef5fe276987d. No service restarted.
Product Owner Acceptance: pending visual review.
Remaining Blockers: original running checkout is dirty from Next-generated next-env.d.ts cache reference. Official preflight denies dirty source; task prohibits overwrite/reset. Live candidate not activated.
Next Action: review focused PR and separately authorize safe original-source reconciliation before official frontend-only cutover; do not suppress integrity checks.
Evidence: [implementation/root cause/review](reliability-cockpit/docs/nadi-dev-ux-status-01.md), [synthetic screenshot index](reliability-cockpit/docs/evidence/nadi-dev-ux-status-01/README.md). Existing frontend/API, 35 containers, original PNG/workbook/worktrees/QA data preserved; no DB or policy changes.


## 2026-10-12 — NADI-DEV-UX-STATUS-01-FIX-02 — pre-cutover runtime investigation

Date: 2026-10-12 WIB
Task ID: NADI-DEV-UX-STATUS-01-FIX-02
Objective: investigate delayed V8 abort and prepare a strictly verified frontend-only Node22 pin.
Branch: codex/nadi-dev-status-runtime-fix-02, based on PR75 candidate.
Commit SHA: frontend candidate5e961b1bfe8ce3c34092613922c3b556de3d74a1; exact runtime-helper commit at linked PR handoff.
PR: focused linked runtime-fix; PR75 remains independent; no auto-merge.
Implementation Status: IMPLEMENTED — pin/preflight/start guard only; active controller not updated.
Test Status: TESTED —35 hermetic tests, both360s same-source/version comparison,20,000 serializer iterations each, three isolated Node22 process cold starts + actual HMR PASS. Original Node25 abort not reproduced; causal fix unproven.
CI Status: exact-head runtime-fix checks verified separately after push; existing PR75 checks PASS.
Merge Status: NOT MERGED.
Development Visibility: HTTPS3000 retains restored f06abce76f8ef9b967ee5b1c2e0802112d77b056 with backend b348235ce6f82c84873a65344ad2ef5fe276987d; no live Node22 activation yet.
Product Owner Acceptance: runtime proposal/cutover approval and sustained live acceptance PENDING.
Remaining Blockers: explicit authorization before live runtime cutover; three official cold starts/30min stability/HMR/session/rollback gates not yet fulfilled.
Next Action: review pin and CI, obtain explicit cutover approval, run official lifecycle and sustained acceptance; rollback if any live gate fails.
Evidence: [runtime investigation and gates](reliability-cockpit/docs/nadi-dev-status-runtime-fix-02.md). No application UI/backend/schema/collector/freshness changes or global Node replacement.


## 2026-10-12 — NADI-DEV-UX-STATUS-01-FIX-02 — actual sustained acceptance

Date:2026-10-12 WIB
Task ID:NADI-DEV-UX-STATUS-01-FIX-02
Objective:controlled verified Node22 preview acceptance after explicit Owner authorization.
Branch:codex/nadi-dev-status-runtime-fix-02 (evidence-only update after reviewed code).
Commit SHA:frontend5e961b1bfe8ce3c34092613922c3b556de3d74a1; installed helper7fd3bdac22788ae1ac31cb8306f283c69384972d; backendb348235ce6f82c84873a65344ad2ef5fe276987d. Final evidence HEAD at PR handoff.
PR:75+76 OPEN; no merge.
Implementation Status:IMPLEMENTED —frontend-only pin; system Node/API/collectors unchanged.
Test Status:TESTED —three official cold starts + actual rollback/return,95 live checks,HMR/session/reconnect; strict1813.65s/120samples and1802s/106browser navigations PASS; no abort/OOM/unscheduled restart.
CI Status:reviewed runtime code exact-head backend/frontend PASS; evidence-only exact-head checked separately after push.
Merge Status:NOT MERGED.
Development Visibility:VISIBLE —sole HTTPS3000 serves exact PR75 source on Node22.23.1; approved clean provenance and both backends AVAILABLE.
Product Owner Acceptance:controlled runtime acceptance authorized/PASS; final visual/merge decision PENDING; engineer UAT/production separate.
Remaining Blockers:no required live runtime gate outstanding; memory headroom/trend follow-up and unproven exact Node25 trigger disclosed; Case detail not available to tested subject, not claimed live-covered.
Next Action:Owner/senior review coordinated PR75+76; retain source/backup/rollback; no auto-merge.
Evidence:[final actual checkpoint](reliability-cockpit/docs/nadi-dev-status-runtime-fix-02.md#controlled-live-acceptance--2026-10-12-final-checkpoint). All old sessions/records/audit/assets/35containers preserved; normal login session/audit additions retained.


## 2026-10-12 — NADI-DEV-UX-STATUS-01-FIX-02 — late gate failure and rollback

Date:2026-10-12 WIB
Task ID:NADI-DEV-UX-STATUS-01-FIX-02
Objective:final handoff integrity after bounded30min observation.
Branch:codex/nadi-dev-status-runtime-fix-02, evidence-only final correction.
Commit SHA:candidate5e961b1bfe8ce3c34092613922c3b556de3d74a1 preserved; final servingf06abce76f8ef9b967ee5b1c2e0802112d77b056; backendb348235ce6f82c84873a65344ad2ef5fe276987d.
PR:75+76 remain OPEN; HOLD MERGE.
Implementation Status:Node22 pin proposal preserved but explicitly rolled back to reviewed pre-test companion/runtime for recovery.
Test Status:bounded30min120samples/106navigations PASS historically; FINAL GATE FAIL at12:33:13WIB —Next memory-threshold worker restart, PID2802093→2847354, regenerated next-env.d.ts dirt and provenance refusal. No observed Node22 V8 abort/OOM; NRestarts0 was insufficient to detect internal worker generation.
CI Status:source/evidence checks independently green/pending after push; cannot override runtime BLOCKED.
Merge Status:NOT MERGED.
Development Visibility:known-good HTTPS3000 restored with Node25.6.1; frontend main PID2850832/start12:36:53; backend PID1664250/start unchanged; both AVAILABLE, clean approved provenance.
Product Owner Acceptance:runtime acceptance NOT GRANTED; final BLOCKED despite earlier bounded-window success.
Remaining Blockers:memory/cache investigation and auditable worker-generation/generated-source lifecycle; original Node25 deopt trigger unproven.
Next Action:Owner review separate controlled follow-up; no forcing candidate retry or merge.
Evidence:[final failure/recovery](reliability-cockpit/docs/nadi-dev-status-runtime-fix-02.md#final-handoff--late-gate-failed-known-good-restored). Existing sessions/record/audit/35containers/assets retained; only normal test login/session/audit additions, no cleanup/API/collector/policy changes.

### 2026-10-12 — NADI-DEV-UX-STATUS-01-FIX-03 (isolated candidate)

- Date: 2026-10-12 WIB.
- Task ID: NADI-DEV-UX-STATUS-01-FIX-03.
- Objective: investigate Next memory restart; reduce measured dev-cache peak, track worker generations and audit exact generated-file restoration without touching live runtime.
- Branch: codex/nadi-dev-status-runtime-fix-03, latest verified main2e190c2b51fde50e0467d6d5165ebb1060902867 with independent PR75/76 ancestry retained.
- Commit SHA: lifecycle46fdf8a / byte-integrity98a2fb9 / memorya9cd743 / runtime status997fe23; final immutable HEAD recorded in linked PR delivery.
- PR: focused FIX-03 stack above PR76; neither dependency auto-merged.
- Implementation Status: IMPLEMENTED in isolated candidate.
- Test Status: TESTED, 44 controller checks, frontend/security assertions, TypeScript/lint/build, 900s A/B, three isolated cold starts with nine actual HMR changes. Backend local205 run/67 PostgreSQL-specific skipped; exact-head CI uses disposable PostgreSQL.
- CI Status: exact-head GitHub Actions required; result and immutable run attached to delivery PR.
- Merge Status: NOT MERGED.
- Development Visibility: isolated browser evidence only; official HTTPS3000 remains f06abce76f8ef9b967ee5b1c2e0802112d77b056, API b348235ce6f82c84873a65344ad2ef5fe276987d.
- Product Owner Acceptance: NOT ACCEPTED; separate authorization required before live changes.
- Remaining Blockers: 60-minute live acceptance not executed; Node25 V8 cause and precise retained-object allocation remain unproven.
- Next Action: Owner reviews candidate and authorizes official frontend-only preflight/backup/cutover and >=60-minute acceptance, with rollback on unexpected worker or integrity failure.
- Evidence: [FIX-03 report](reliability-cockpit/docs/nadi-dev-status-runtime-fix-03.md); [isolated metrics/screenshots](reliability-cockpit/docs/evidence/nadi-dev-status-runtime-fix-03/README.md). A/B peak2344.0→1836.7MiB, baseline internal restart1 versus candidate0. This bounded isolated result is not sustained live acceptance.


## 2026-10-12 — NADI-DEV-UX-STATUS-01-FIX-03 — late live failure and recovery

Date: 2026-10-12 WIB.
Task ID: NADI-DEV-UX-STATUS-01-FIX-03 (actual acceptance checkpoint).
Objective: observe the explicitly authorized exact candidate for 60 minutes plus 15-minute handoff.
Branch: codex/nadi-dev-status-runtime-fix-03.
Commit SHA: tested candidate 726ea1f1100c446112dcb71883d77839c5e5acfc; restored frontend f06abce76f8ef9b967ee5b1c2e0802112d77b056; QA API b348235ce6f82c84873a65344ad2ef5fe276987d.
PR: #75/#76/#77 OPEN; no merge.
Implementation Status: IMPLEMENTED candidate retained, not accepted for sustained live runtime.
Test Status: FINAL GATE FAILED at 16:38:25.260994 WIB after 3475.85s (57m55.85s). Next heap safeguard replaced worker 3010264 with 3078400; parent 3010238 and systemd restart count stayed unchanged. No observed V8 abort/OOM. Earlier browser/login/HMR checks do not override failure; 15-minute handoff NOT RUN.
CI Status: source CI PASS historically, independent of runtime failure.
Merge Status: NOT MERGED; HOLD runtime stack.
Development Visibility: official recovery restored known-good source and original Node25/controller; frontend parent3078556/worker3078570 started16:38:28, backend1664250 unchanged.
Product Owner Acceptance: controlled test authorized; sustained runtime acceptance FAILED; final visual/merge approval not granted.
Remaining Blockers: sustained retained heap growth; full allocation/retaining owner uncertain.
Next Action: isolated FIX-04 root-cause investigation, no automatic live retry.
Evidence: [FIX-04 checkpoint and investigation](reliability-cockpit/docs/nadi-dev-status-runtime-fix-04.md). Private actual acceptance journal/metrics/screens retained. Previous bounded isolated PASS remains historical; this append records the later failure without rewriting it.

## 2026-10-12 — NADI-DEV-UX-STATUS-01-FIX-04 — isolated heap investigation

Date: 2026-10-12 WIB.
Task ID: NADI-DEV-UX-STATUS-01-FIX-04.
Objective: measure sustained heap contributors while leaving HTTPS3000 untouched.
Branch: codex/nadi-dev-status-runtime-fix-04, clean isolated branch stacked on PR77.
Commit SHA: application baseline726ea1f1100c446112dcb71883d77839c5e5acfc; diagnostic runtime harness 9edac65bf3c87ff8cdf842a1b96a2fe45a16093f; exact final evidence HEAD at PR78 handoff. Main2e190c2b51fde50e0467d6d5165ebb1060902867.
PR: [#78](https://github.com/johnd-creator/reliability-knowledge-starter/pull/78), diagnostic DRAFT; #75/#76/#77 remain independent and unmerged.
Implementation Status: IMPLEMENTED disposable diagnostics; NO application remediation. PARTIAL — NEEDS FURTHER INVESTIGATION.
Test Status: three ≥75min baseline variants and a corrected HMR variant that reproduced Next threshold replacement after3911.8s (65m11.8s), with immediate fail-stop/no retry. Original worker3355751→3427089, parent3355725 unchanged, no V8/OOM. Read-only Flight ancestry/mechanism controls; 50 controller/confinement/privacy tests PASS. Rejected weak-link experiment not installed. No remediated-candidate75-minute PASS claimed.
CI Status: required backend/frontend exact-head CI verified at final PR handoff; CI does not prove live stability.
Merge Status: NOT MERGED; no live-cutover authority in this task.
Development Visibility: official frontend remainsf06abce76f8ef9b967ee5b1c2e0802112d77b056, APIb348235ce6f82c84873a65344ad2ef5fe276987d; screenshots are explicitly disposable fixture evidence.
Product Owner Acceptance: investigation authorized; live, visual, engineer UAT and production acceptance NOT GRANTED.
Remaining Blockers: full module-source retaining path, instrumentation-versus-live dominance and a framework-compatible remedy. Equivalent Next safeguard failure is reproduced; problem NOT FIXED. Fresh persistent database/schema/record/session/container comparison NOT VERIFIED after automatic approval review refused non-operational task access.
Next Action: bounded disposable retainer/module-generation analysis and reviewed framework compatibility work; separate new PO approval before any future live acceptance.
Evidence: [investigation](reliability-cockpit/docs/nadi-dev-status-runtime-fix-04.md), [sanitized timelines and fixture screens](reliability-cockpit/docs/evidence/nadi-dev-status-runtime-fix-04/README.md). Raw profiles private; active controller/source/backup/assets/workbook retained; no database, collector, policy or operational change.

## 2026-10-13 — NADI-DEV-UX-STATUS-01-FIX-05 — isolated retainer attribution

Date: 2026-10-13 WIB.
Task ID: NADI-DEV-UX-STATUS-01-FIX-05.
Objective: distinguish GC-root reachability, projected retained-byte dominance and diagnostic overhead; assess safe framework-compatible candidates.
Branch: codex/nadi-dev-status-runtime-fix-05, stacked on exact FIX-04 ef70aa6f2dc21866bbbd6de73f1db30ad4ab286a.
Commit SHA: final immutable diagnostic HEAD recorded in draft PR delivery; main2e190c2b51fde50e0467d6d5165ebb1060902867; official configured frontendf06abce76f8ef9b967ee5b1c2e0802112d77b056/APIb348235ce6f82c84873a65344ad2ef5fe276987d remain separate.
PR: new DRAFT above PR78; no merge or runtime cutover.
Implementation Status: IMPLEMENTED disposable diagnostics; PARTIAL — NEEDS FURTHER INVESTIGATION; no application remediation.
Test Status: TESTED —private bounded snapshots, eight matched synthetic6/18/2/1 full-GC controls,66 safety/graph tests and seeded oracle comparisons. Failed capture/resource/Inspector attempts retained. Source strings133.7MB; four vendor Script versions59.2MB; Flight ancestry186,271 nodes. Ephemeron ownership remains unproven. Memory cache+35% rejected; vendor-map exclusion-21.75% heap is an isolated candidate, not acceptance.
CI Status: exact-head backend/frontend required and reported at draft handoff; independent of sustained runtime acceptance.
Merge Status: NOT MERGED.
Development Visibility: NOT ACTIVATED; no live HTTP/browser/session interaction. Pre-existing primary worker drift and next-env.d.ts dirt disclosed and untouched.
Product Owner Acceptance: diagnostic scope authorized; visual/live/engineer UAT/production acceptance NOT GRANTED.
Remaining Blockers: complete conditional WeakMap/root ownership, long-run comparative slope, original-frame/debugging compatibility; no fresh persistent QA/session/container audit within this scope.
Next Action: review guarded vendor-only map exclusion proposal for isolated FIX-06; separate approval before any future official runtime action.
Evidence: [FIX-05 report](reliability-cockpit/docs/nadi-dev-status-runtime-fix-05.md), [sanitized evidence](reliability-cockpit/docs/evidence/nadi-dev-status-runtime-fix-05/README.md). Prior evidence, worktrees, assets, workbook, backup and operational settings preserved; no DB/schema/collector/source/freshness change.

## 2026-10-13 — NADI-DEV-UX-STATUS-01-FIX-06 implementation checkpoint

- Objective: default-disabled vendor-map adapter and sustained isolated assessment.
- Branch: `codex/nadi-dev-status-runtime-fix-06`; base `63b61d09c45630a76657cdb54991349fb0528e7b`.
- PR: [DRAFT #80](https://github.com/johnd-creator/reliability-knowledge-starter/pull/80), stacked on FIX-05/PR79.
- Implementation Status: IMPLEMENTED, experimental/disposable only; application/controller unchanged.
- Test Status:69 hermetic controller/analyzer/confinement tests,21 adapter cases,
  actual client/server source-frame and breakpoint qualification,3 state-preserving
  component HMR cycles,455 intercepted browser assertions, TypeScript/lint/build PASS.
- CI Status: backend/frontend PASS at guard correction milestone; final delivery
  exact HEAD remains a separate verification after sustained evidence.
- Merge Status: OPEN/DRAFT; not merged.
- Development Visibility: official preview not changed or queried by HTTP.
- Product Owner Acceptance: NOT REQUESTED; sustained assessment IN PROGRESS.
- Remaining Blockers: existing primary Node25 worker replaced by heap safeguard at
  03:31:52WIB and generated next-env dirt require OPERATIONAL REVIEW. Source/frontend
  status JSON does not prove current provenance. QA status would read DB and was not
  called. Baseline DEV-label HMR full reloads are recorded separately from successful
  component Fast Refresh. Initial CI fresh-root confinement failure corrected/tested.
- Next Action: complete baseline/candidate run, natural post-GC slope/threshold and
  allocation comparisons, append actual verdict and exact-head CI evidence.
- Source evidence: [FIX-06 report](reliability-cockpit/docs/nadi-dev-status-runtime-fix-06.md).

## 2026-10-13 — FIX-06 sustained baseline failure and candidate launch

Baseline failed at79.85min on Next used-heap threshold / worker generation loss.
Original4102290, unapproved33574; no receipt refresh, repair or retry.277 navigations,
1222 status requests,80 HMR cycles/80 reloads,27 in-memory session reads; heap
peak1648.9MiB, cgroup peak2343.2MiB, OOM0. Official frontend/backend were not acted on.
Final guarded-adapter debugger qualification passed actual client/server original
frames, breakpoint, vendor-error application callsite, RSC and3 state-preserving
component HMR cycles. Candidate95min started with15min additional headroom beyond
baseline failure. Candidate stability remains IN PROGRESS, no acceptance/merge.
Source: [FIX-06 report](reliability-cockpit/docs/nadi-dev-status-runtime-fix-06.md).
