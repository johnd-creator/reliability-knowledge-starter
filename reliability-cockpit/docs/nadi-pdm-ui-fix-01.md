# NADI-PDM-UI-FIX-01 — Keyboard focus containment

Date: 15 October 2026. Status: IMPLEMENTED / TESTED in hermetic Chromium;
not merged, not activated, Product Owner live visual acceptance pending.
Delivery: existing [PR #85](https://github.com/johnd-creator/reliability-knowledge-starter/pull/85), OPEN/DRAFT.
Source baseline: `f8d6334ce93f766b851a5d69577ff83c1b8563e1`.
Main verified unchanged: `106a4dc08b149576b2e84bbf8c70694288c7e9a7`.

## Verified cause and smallest correction

The 1100px minimum-width grid overflows its 1040px scroll region at 1440px.
Native Tab focuses the partly visible final Hapus button without scrolling:
region x=324–1364, button x=1337.75–1405, scrollLeft=0. Its 3px outline plus
2px offset also lies outside the region. The exact geometry reproduces the
retained LOCAL-REVIEW-01 live finding. This is focus visibility, not a failed
focus transition or page-level overflow.

Isolated CSS comparisons with scroll-padding/scroll-margin, then added container
padding, still left the control clipped. Reducing the minimum width worked at
1440px but does not reliably solve narrower desktop widths while retaining
readable columns. No CSS/grid width or design token change was retained.

`PdmMeasurementForm` now captures focus only inside `.pdm-grid-scroll`. It reads
the actual outline extent and container client bounds, then changes only this
container's horizontal scroll by the missing distance. It does not move focus,
change tabindex, intercept keys, scroll the global page, update form state or
alter submission. The same containment applies in reverse navigation to left
fields. Native vertical focus behavior is preserved; no animation or global
listener is added.

After correction at 1440px: scrollLeft=46, button x=1291.75–1359, outline
right=1364. All 5px of the focus indication fit in the region.

## Browser and static verification

All requests are intercepted at `https://pdm.synthetic.invalid`. These are real
Chromium interactions with the mounted application components and synthetic
responses; no listening server, persistent fixture/session, localhost request,
operational source or database is used.

| Check | Result |
|---|---|
| 1280, 1440, 1920 CSS-pixel desktop | PASS |
| Light/dark via actual theme toggle | PASS |
| 3/9/11/12 rows, first/last row | PASS |
| Tab, Shift+Tab, forward/reverse order | PASS |
| Entire control + computed outline inside scroll region | PASS — 320 geometry observations |
| Focused controls visible vertically; no page horizontal overflow | PASS |
| Pointer add/remove, unchanged values, cancelled discard, same-subject draft refresh | PASS |
| Focused assertions | 404/404 PASS |
| Existing PdM browser regression, all nine profiles and workflows | 169/169 PASS |
| Combined CI-included browser suite | 573/573 PASS; zero uncaught browser errors |
| Input/workbook safety assertions | 64/64 PASS |
| TypeScript, ESLint, production build, diff whitespace | PASS |

Actual browser chrome zoom is unavailable in the headless harness. An additional
1152 CSS-pixel viewport tests the effective width of 1440/1.25; it is explicitly a
proxy, **not actual 125% browser zoom acceptance**. Normal browser zoom remains
available for subsequent Product Owner live review.

ESLint reports two pre-existing warnings (ignored development-status route and
EngineeringWorkspace effect dependency); no errors or new warning suppression.
The first sandboxed assertion invocation hit child-process `EPERM`; rerunning
with the required process permission passed. No application failure was observed.
Backend source/contracts are unchanged; backend and canonical regression remain
covered by the existing exact-head GitHub workflow. Final CI URLs and exact
commit are recorded in the PR delivery update, independently of local results.

## Evidence

- Matched full-page 1440px screenshots, last Hapus focused:
  [before](evidence/nadi-pdm-ui-fix-01/before-hermetic-1440.png) /
  [after](evidence/nadi-pdm-ui-fix-01/after-hermetic-1440.png).
- Settled focused viewport: [1440](evidence/nadi-pdm-ui-fix-01/focused-hermetic-1440.png),
  [1920](evidence/nadi-pdm-ui-fix-01/focused-hermetic-1920.png),
  [1280](evidence/nadi-pdm-ui-fix-01/focused-hermetic-1280.png).
- [Geometry measurements](evidence/nadi-pdm-ui-fix-01/keyboard-results.json),
  [all browser assertions](evidence/nadi-pdm-ui-fix-01/pdm-browser-results.json),
  [screenshot hashes](evidence/nadi-pdm-ui-fix-01/sha256.json).

Every image above is **hermetic synthetic browser evidence**, not live-after
acceptance. Historical live evidence remains in its original private directory.

## Preservation and review disposition

Implementation uses a detached, non-serving worktree. A normal fast-forward push
updates PR #85's remote branch without moving its checked-out serving local
branch. No history rewrite or force push is used.

The active frontend remains at `f8d6334ce93f766b851a5d69577ff83c1b8563e1` in the
original `pdm-workbook-01` worktree. Its exact generated `next-env.d.ts` route-type
path difference is preserved. Frontend/API service invocation IDs and restart
counts are compared read-only before/after; neither controller nor runtime is
changed. No fixture or session access is performed.

All nine mappings/source labels/units, InspectionDraft v1.1, backend, database,
CSRF/auth/session, review and Engineering Case contracts remain untouched.
Original workbook/PNG assets, other worktrees, collector/Mart and freshness
policy are not modified. No broad environment/container audit is needed here.

Self-review found no remaining critical/high issue in this narrow correction.
The component-local handler is justified by the failed CSS-only experiments;
focused geometry tests are included automatically in the existing PdM CI browser
command. This report does not change engineer-validation or operational gates.

Next: separately controlled localhost source selection → Product Owner visual
review (including native 125% zoom) → PR #85 merge decision. Keep PR OPEN/DRAFT;
no live source transition or merge is authorized by this fix.
