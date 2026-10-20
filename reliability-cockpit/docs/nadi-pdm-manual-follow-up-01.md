# NADI-PDM-MANUAL-FOLLOW-UP-01 — asal, analisis manual dan referensi SR

## Scope and requirement trace

FR-03/FR-04, UI-04, NFR-01/04/05. Package baseline is verified main
`44bc1def5ba18802838bc5d40e04165685197696` (merged PR108). Item1 copies the
previous reviewed local work-origin candidate; its original worktree is preserved.
The PO subsequently authorized items2–3, fixes/review, then branch push and a
**draft** PR if GO. No merge, deploy, preview activation, real DB migration,
security/trust change, source write or F03/PR107 integration is authorized.
Implemented, locally tested, published, CI passed, merged, visible and operationally
accepted remain separate. Exact publication SHA/PR/terminal CI belong to handoff.

## Product semantics

1. Work origin remains department request or PdM PM52-week finding; requesting
   department is conditional. Unknown historical origin stays absent/unknown.
   Existing authorized canonical asset identity and unverified source labels
   remain separate. No operator approval/contact requirement is introduced.
2. Actual measurement values stay in native measurements or provisional workbook
   capture; original findings remain observations and hypotheses remain separate.
   Optional `engineering_analysis.notes` is a manual narrative summary, not a new
   automatically generated diagnosis, threshold or interpretation. Optional
   `recommended_follow_up` is human text, not a Recommendation entity or approval.
   Provenance is fixed `HUMAN_ENTERED_ENGINEER_NOTES`. Technical correctness,
   equipment condition, method/threshold approval and engineer qualification are
   not certified by recording or independently reviewing the inspection.
3. Up to10 `sr_references` contain the exact reported `sr_number` and optional
   `follow_up_note`. `system=MAXIMO`, `verification=REPORTED_UNVERIFIED` are fixed,
   including after an inspection becomes APPROVED. Existence/status/asset linkage
   are not checked. Numbers retain leading zeros, whitespace and original text;
   no fuzzy/canonical binding or automatic URL is created. Duplicate exact numbers
   within one inspection are rejected. SR is distinct from Work Order. No Maximo
   request, SR creation, status lookup, or external write occurs.

Notes are bounded strict nonblank strings (analysis/follow-up≤6000; SRnumber≤100;
SRnote≤2000). Optional empty controls map
to null/absence; whitespace-only supplied notes are invalid. A follow-up requires
an analysis note. Nothing is backfilled into historical records.

## Contract and owning workflow

Optional typed fields extend `InspectionDraft`/`ManualInspection`, not arbitrary
method extensions or a new database. Contract1.4 is used if analysis or nonempty
SR references exist, independently of origin/native/capture. Origin-only1.3,
capture1.2 and native1.0/1.1 remain readable; absent new fields are excluded from
serialization, preserving exact old JSON/evidence hashes.

The owning Inspection service explicitly replaces optional origin/analysis/SR
fields on UPDATE, including None/empty values. Otherwise merging a serializer
that omits cleared fields could retain stale notes, SRs or origin. The final
record serializer omits absent values; previous immutable revisions remain intact.
The regression covers each individual clear while1.4 remains and all-clear→1.1.

Existing session-derived AUTHOR permission and server-owned inspector attribution,
asset scope/Registry, CSRF/Origin, CAS expected_revision, request receipts,
contributors, independent review, immutable snapshots and audit actors apply.
Personas do not create new roles or an engineer-self-certification input. Revisions
remain draft-only; returned/rejected records use the existing revise lifecycle.
UI/detail/each history snapshot display their own manual context. Original legacy
snapshots explicitly show no recorded analysis/SR, not assumed empty work.

Entry fields reuse existing in-memory draft protection and command intents. Focus,
transient auth failures, navigation interruption and lostACK retain the same-session
draft/receipt. Subject/role/asset-scope changes and revocation clear private context.
No new browser persistent storage or guarantee across browser closure is added.
Capture with manual notes/SR stays provisional, excluded from canonical measurement
history/plots and Case evidence. Native Case evidence keeps existing exact-version
binding; this package does not expand the Case snapshot or automate recommendations.

## Tests and CI

- `test_pdm_work_origin` and `test_pdm_manual_follow_up`: strict types/version matrix,
  legacy1.0–1.3 byte witnesses, native/capture × origin combinations, exact text,
  create/replay/review/revise/history/CAS, clearing, sanitized422, role/CSRF/scope/
  attribution/revocation. PG-only classes explicitly skip without disposable DSN.
- `npm run check:pdm-input`: existing native/workbook/capture checks plus manual
  analysis/SR roundtrip, limits, legacy absence, conditional notes and exact labels.
- `pdm-auth-browser-check.py`:13 actual-component scenarios carrying all3 items,
  recovered textarea names/values, lostACK, navigation, same/changed session.
- `pdm-origin-api-browser-check.py`:4 actual UI→trusted-session FastAPI TestClient→
  disposablePostgreSQL scenarios: create/lostACK same-intent once, readback/PM52/
  analysis/SR revision, exact immutable history,390px reopen, and explicit clearing.
  Bootstrap identity is synthetic; it does not test actual user login/wireHTTP/
  Nextproxy. All browser traffic is fulfilled before network at `.invalid`; no TLS
  bypass or existing browser profile is used. `--chromium` is optional: CI uses the
  installed Playwright default fresh headless browser, local QA can pass a cached
  test executable. Bundle via `node scripts/pdm-follow-up-browser-bundle.mjs OUT`.
- Engineering CI retains existing gates and adds both modules plus actual13/4
  browser scenarios on disposable CI PostgreSQL, pinned test-only Playwright1.63.0
  and Node22. Existing frontend browser suites still run. Local logs/final results
  and immutable manifest are in task handoff; remote exact-head CI is separate.

Independent review found the optional-field clear bug and real UI tests found
reopened textarea accessible-name instability. Both have explicit fixes and
regressions. No passing baseline was used to dismiss them.

## Activation and limits

The active paired preview remains main44bc with its reviewed local controller.
Package1.4 is not visible there. Old44bc code cannot read1.3/1.4 records; future
paired activation needs separately authorized source selection and exact-target
compatibility/controller review. Rollback must refuse unreadable data rather than
removing it. This package changes no launcher/controller or operational stores.
Real Chrome certificate warning/login and engineer/PO UAT remain pending user
handoff; no trust bypass is permitted. F03, Phase1 mapping/approval, operational
engineering policy and Maximo write authority are not qualified by this package.
