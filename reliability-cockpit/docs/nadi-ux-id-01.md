# NADI-UX-ID-01 — Indonesian Localization & Glossary

11 October 2026 · `codex/nadi-ux-id-01` · implementation candidate for PO review.

**Implementation/test PASS; live preview visibility PARTIAL.** Bahasa Indonesia,
searchable glossary and regression evidence are delivered on an isolated branch.
The existing HTTPS 3000 runtime remains operational and unchanged. Final PR/HEAD and
exact-head CI are verified at delivery handoff, separately from this source checkpoint.

| Milestone | Result | Evidence / boundary |
|---|---|---|
| L0 — Audit | PASS | PR 69 MERGED; latest main 09b6d6308a6cc70818292eb71f79733255dcf823 verified twice; instructions/product docs read |
| L1 — Interface | PASS candidate | 1344 typed copy keys; UI labels/status/errors/ARIA across all NADI page families; no protocol enum/data changes |
| L2 — Glossary | PASS candidate | `/panduan/istilah`, 41 searchable EN/ID entries, navigation/contextual help; six engineering definitions explicitly pending |
| L3 — V1 | PASS tested | Same token bytes/logo, navy/green, light/dark and 1440/768/390; longer labels wrap; Data Trust table contained |
| L4 — Review | PASS local; exact-head CI at handoff |370 browser checks, TypeScript/build/assertions, whole-presentation lint, 14 contracts; actual backend security in isolated CI |
| L5 — Delivery | PR candidate / no merge | This report, selected screenshots, terminology matrix, official roadmap/PRD/design/UI-spec/log updated |

## Exact baseline and runtime

- Verified latest merged main: `09b6d6308a6cc70818292eb71f79733255dcf823`.
- PR 69 merged 11Oct 03:59:32Z; integrated source HEAD `b348235ce6f82c84873a65344ad2ef5fe276987d` is an ancestor of main.
- Implementation commit: `2abbe61a0973d2cd8ce1d788e7fad525cb0173b6`.
- Worktree: `.nadi-dev/ux-id-01`; original root branch/dirty workbook and all other checkouts untouched.
- Previous AND final serving frontend/source/backend/launch SHA: `b348235ce6f82c84873a65344ad2ef5fe276987d`; clean, stale=false.
- Only frontend: `https://localhost:3000`; `nadi-primary-web.service` and existing QA `nadi-live-api.service` active; legacy13035 frontend inactive. Factual API and Engineering backend AVAILABLE; DB identity `nadi_live_dev_test`.

Official launcher `switch` refuses a running preview; `stop/reload` stops both web
and QA API. QA startup applies migration readiness. This task forbids changing QA
services/data or starting QA deployment, so **no source switch, restart, new frontend,
port or server was performed**. A separate official frontend-only source-selection
solution/authorized runtime task is needed before claiming localized live visibility.
The implementation is reviewable through code and explicitly synthetic screenshots.

## Presentation decisions and compatibility

English source keys remain searchable in `web/lib/id-messages.json`; typed `idText`
validates known labels at compile time. `statusLabel` supplies Indonesian meaning
plus exact codes; unknown/vendor values remain verbatim. `errorLabel` maps known
errors/codes and hides arbitrary transport details. It is never used to modify
records, requests or authorization decisions. APIs, DTOs, security/transport helpers,
persistence logic and original fixtures are byte-identical to baseline and guarded
by fingerprint assertions. Authentication cookies/session/RBAC/CSRF policies stay
unchanged; all product development gates remain in place.

| Original presentation | Indonesian | Meaning retained |
|---|---|---|
| Executive Overview | Ringkasan Eksekutif | Factual dashboard; no new health metrics |
| Asset Health | Kondisi Aset | UNKNOWN / NOT ASSESSED remain explicit |
| Recommendations | Rekomendasi | NADI-owned; not a Maximo WO |
| Action Board | Papan Tindak Lanjut | Local follow-up, not execution authority |
| UNKNOWN | Belum diketahui (UNKNOWN) | Missing knowledge never zero/healthy |
| APPROVED | Rekam disetujui (APPROVED) | Record review, not work authorization |
| ACK | Konfirmasi penerimaan (ACK) | Receipt only |
| COMPLETED | Selesai secara lokal (COMPLETED) | Distinct from VERIFIED effectiveness |
| SYNTHETIC QA | QA SINTETIS with source code where relevant | Never plant operational evidence |

UI source/property labels are translated; user evidence, notes, rationales, names,
canonical identity, Work Order references, enums, URLs, units and timestamps are
retained. Translated select options explicitly submit original values. Legacy demo
screen keys and automatic history reasons remain their original values. The one new
route is public read-only help; no existing route changes and no global login gate.

## Validation and autonomous review

- TypeScript and production Next 15 build PASS with unavailable loopback backend;
  no running server used for build. Existing Next ESLint-plugin notice remains.
- Frontend engineering/phase2/workflow, bounded HTTP/proxy, login, product-safety,
  UX 43, login presentation 9, Engineering product 8 and new localization10 checks PASS.
- ESLint now covers all presentation JSX:0 errors, one existing warning on deliberately
  pinned legacy demo editor effect. Adding current-record dependency would discard
  stale/unsaved edits; its existing behavior is preserved and documented as low debt.
- Canonical contracts 14 PASS. Local backend 150 tests:94 PASS/56 PostgreSQL-required skips;
  no persistent DSN used. Full PostgreSQL/HTTPS backend suite runs in isolated GitHub
  CI, not against `nadi_live_dev_test`; exact results at PR handoff.
- Browser 370 checks PASS: actual candidate components, total request interception,
  Case→reviewed Recommendation→Advisory→Inbox/ACK, typed raw enum payloads, CSRF
  forwarding, idempotent retry, 409 retained edits, denied access clears records,
  searchable glossary, navigation keyboard/deep link, named controls, 72 responsive
  scenes plus dark mode and explicit unavailable states. Fixture responses simulate
  authorization outcomes; they are **not new persistent E2E or engineer UAT evidence**.
- Contrasts remain unchanged and pass the V1 tests. Human inspection of Login desktop,
  Advisory mobile, Executive tablet and glossary verifies hierarchy and wrapping;
  PO wording/visual acceptance and full accessibility certification remain pending.

| Finding | Severity | Correction / disposition |
|---|---|---|
| Translated internal lab tab keys mismatched original comparisons | High regression, caught before delivery | Original keys/init restored; translate at render only; regression guard added |
| Automatic synthetic history reasons / quantity default translated | High data-integrity regression, caught before delivery | Original values restored; logic libraries byte-identical; fingerprint and reason checks |
| Labels could become implicit HTML option values | High workflow regression, caught before delivery | Explicit original value before display translation; payload/browser assertions |
| Data Trust table overflow at 768px | Medium UX | Reused keyboard-scrollable TableFrame;370 final checks include all widths |
| Known translated validation error remapped to generic feedback | Medium UX | Allowlisted known translated errors retained; unknown transport still sanitized; unit coverage |
| Harness subprocess permission, Next params/optimizer/UTF-8 assumptions | Test tooling | Correct permissions, typed route params, test-only Next adapters and charset; final captures regenerated |
| CSV export used CRLF and triggered full commit-range whitespace check | Low evidence formatting | Normalized to LF without changing any translation pair; full baseline-to-HEAD check repeated |
| Existing selected-only editor effect warning | Low maintainability | Kept intentional revision pin; no unsafe state-behavior refactor |

All high/critical implementation findings are resolved. No new runtime dependency
or competing design system was added. CI installs pinned Playwright only in an
isolated runner temporary directory. Screenshots never contain real credentials or
operational/personnel data.

## Preservation, backup and rollback

Read-only REPEATABLE READ snapshots verified the exact existing loopback application
QA target and compared full row hashes/schema/grants/session state before and after
hermetic tests. All existing rows are exact, including 82 sessions, 3 accounts, 10 cases,
55 caseevents/55 receipts, 17 humanrecords, 62 humanrevisions/62 receipts, 5 migrationentries,
1530 securityactivities and 86 localsecurityevents; no row/DDL/identity change. All 35
container IDs/start times, managed service PIDs/start times and all 34 other worktrees remain
identical; only this candidate branch advances. Original five PNGs and `23496711.xls` hashes are unchanged.

Existing private backup `backup-20261011-102702.dump` remains readable with valid
PostgreSQL archive listing, SHA 256 `045197097bd22a5c633449196c1c02836b6e01b47e5939713a8cf56915866986`.
Historical disposable-clone restore/source rollback evidence stays in the
[integration report](nadi-eng-integration-01.md). No restore into active DB or new
restore test was performed. [Read-only preservation results](evidence/nadi-ux-id-01/preservation-results.json) are retained. Source rollback readiness is unchanged: existing
b348235 runtime/checkpoint is retained; localization needs no database rollback.

Phase 1 independent 72 h review 11 Oct 21:45:26 WIB, PO checkpoint 12Oct 20:00 WIB and
hard expiry 13Oct 00:00 WIB remain unchanged. Operator review result UNKNOWN unless
separate accepted evidence exists. This UI task does not reset/extend monitoring.

## Coverage and remaining gates

[Evidence index, matrix, screenshots and checks](evidence/nadi-ux-id-01/README.md).
Structural discovery used graph Tier 2; generation 24Aug 2026 misses later frontend
symbols, so current source/AST reads were used. Static JSX/copy inventory and
whole-presentation lint were audited; retained English consists of industry terms,
raw contract/vendor codes, units, original source/user record values and English
source keys, not an attempt to translate operational evidence. Fixture-only unavailable
scenes do not prove backend/data unavailability. App runtime is explicitly unchanged.

Next: PO review Indonesian wording, navigation density and glossary, then a separate
safe official runtime selection task. Engineer method/threshold/comparability validation,
organizational recipient policy, real UAT, operational distribution and production
acceptance remain pending. No merge, Phase 3 intelligence or global enforcement.

Documentation validation: **239 relative targets across eight changed/new Markdown
documents PASS**, 37 screenshot hashes PASS, five original reference bytes PASS,
and 1344 terminology pairs match the dictionary exactly. `git diff --check` PASS.
