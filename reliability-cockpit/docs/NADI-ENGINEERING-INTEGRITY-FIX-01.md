# NADI-ENGINEERING-INTEGRITY-FIX-01 — local candidate

20 October2026. Requirements FR-04/FR-05, UI-05/UI-06/UI-07. Baseline and HEAD remain
`35f3c101129241745e1795edd78a34c3617dccd7`; all changes are uncommitted in the
isolated `engineering-workspace-fix` worktree. No push/PR/merge/deploy, operational
source/data/grants/auth configuration, F03 activation or PdM/domain decision.

## Finding disposition

| Audit finding | Local fix and verification |
|---|---|
| EW-01 stale Recommendation submission | Dirty fields block Submit in both affordance and handler; explicit Save sends all edited fields with original CAS revision. Actual UI Save→Submit uses intended content. |
| EW-02 focus loses Recommendation edits | Layout-owned memory cache binds subject, authority fingerprint, record and original base revision. Focus/remount,503 retry, conflict and changed-authority scenarios pass. |
| EW-03 Case draft lost on503/Back | Durable workspace recovery, transient-vs-auth distinction, explicit resume of another draft and per-command retry slots. Actual lost-ACK→list503→retry and lost-ACK A→B note→retry A preserve request ID and one persisted A. |
| EW-04 frozen CONDITION omitted | FrozenCaseEvidence shows original value/type/unit/source+collection times, quality flags, freshness/policy and identity/link provenance. Null/zero/false/digital/escaped content and live-reference distinction are covered. Actual independent reviewer sees12.5A and original trust context. |
| EW-05 detail401 leaves private register | Exact detail/history/mutation401 uses synchronous invalidation and async generation fencing. Real revoked fixture session clears register/ready state without needing window focus. |
| EW-06 PostgreSQL deadlock | Uniform Case→sorted Inspection→Recommendation order, completion union lock and early Case mutation lock. Real PG barrier regressions cover submit/review, reversed completion sets and CaseLINK/CAS. |
| EW-07 same-timestamp correction undetected | Versioned factual identity/content digest with bounded-memory string hashing. Actual Mart content changes at fixed timestamp block new actions; ingest-only changes do not. Legacy pins fail closed with history unchanged. |

The original audit reproduced each finding on this same baseline; its185 passing
baseline tests did not disprove those failures. The implementation adds13 backend
regressions. Initial new-test enum mistakes were corrected in the tests; they
were not product fixes disguised as passing baseline checks.

## Independent review

A fresh reviewer inspected the full local runtime diff. Review identified and
closed three additional P2 issues before the final candidate:

1. A pending Case command without form recovery was not fenced on subject changes.
   Global authority fingerprints and captured request IDs now invalidate all old
   pending slots; late200/401 responses cannot affect the new subject.
2. The first digest implementation rejected long but contract-valid strings.
   Incremental typed field hashes replace arbitrary length limits. Contract-valid
   12,001ASCII/60,000Unicode strings pass; same-length and same-byte-length tail
   corrections change the digest.
3. Another Case's successful command could overwrite a lost-create retry ID.
   Slots are now separate per subject/method/path; successful saved-draft cleanup
   preserves unrelated receipts. Actual DB commitA/ACK503→B note200→retryA creates
   exactly one A and retains the original request ID.

## Tests

- Backend: **198/198 PASS,0 skips** on private native PostgreSQL16.14, including
  **13/13 new integrity regressions**. No application/collector DB was used.
- Existing frontend `check:eng-product`:16checks; new
  `check:engineering-fixes`:8component/contract groups.
- Focused browser:13Recommendation and14Case provider/command scenarios, with
  every HTTP request intercepted at a synthetic `.invalid` origin. These are
  component regressions, not claims of actual backend persistence.
- Separate real Chromium→Next→HTTP→PostgreSQL fixture covers inspection approval,
  Case UI validation/evidence/review, linked Recommendation explicit Save/Submit,
  local follow-up/independent verification, permissions/CSRF/self-review/CAS,
  repeated submission, acknowledgement loss, Back/Forward, cross-record recovery,
  frozen CONDITION reviewer display and revoked-session cleanup.
- Full TypeScript and lint checked locally. Lint retains one pre-existing
  exhaustive-deps warning at EngineeringWorkspace.tsx:32. Production build PASS is a
  local compilation only; its terminal result is recorded in the delivery
  evidence. No hosted exact-head CI exists for an uncommitted local diff.

Commands from `reliability-cockpit/` with disposable DSNs only:

```text
python -m unittest test_engineering test_bundle_c_integration.BundleCPostgresIntegrationTest test_engineering_qa.QaFactoryTest test_engineering_integrity test_recommendation_workflow test_manual_inspection test_application_identity test_local_authentication -v
```

Set `PYTHONPATH=.:tests`, `NADI_APPLICATION_TEST_DSN` and
`NADI_ENGINEERING_TEST_DSN` to an explicitly owned loopback `*_test` DB first.
Fixtures deliberately reset that test schema. Never substitute a persistent,
operational or primary-development DSN.

From `web/`: `npm run check:eng-product`, `npm run check:engineering-fixes`,
`node node_modules/typescript/bin/tsc --noEmit --incremental false`, `npm run lint`,
and `npm run build`. Focused browser bundles reuse repository helper
`browserBundle` from `scripts/localization-browser-build.mjs` with entries
`scripts/recommendation/entry.tsx` and `scripts/recommendation/case-command-entry.tsx`.
Pass the generated candidate.js and an explicit Chromium executable to the
corresponding Python scripts `recommendation-browser-check.py` and
`case-command-browser-check.py`. All browser HTTP is intercepted; no port is opened.

## Limits and acceptance

IMPLEMENTED/TESTED locally only. Not committed, merged, activated, visible on the
main preview or engineer/PO accepted. The actual preview remains on its original
source/controller;35containers and original local dirty files are protected.
Fixtures are separately owned, synthetic, private and shut down after verification.
Source and application stores do not become one atomic cross-store transaction.
Digest provenance is a content pin, not a signature or proof of source correctness.

Old factual pins may require deliberate revision/reselection/new proposal; no
silent upgrade or history rewrite is performed. Owner recovery of progressed
legacy records remains an explicit decision. Full reload loses unsaved memory
after its unload warning; no private content is put in browser storage. Real
engineer/domain UAT, PdM/M02 signoff, operating freshness/mapping and F03 gates
remain separate. Review the local patch before authorizing any publication.
