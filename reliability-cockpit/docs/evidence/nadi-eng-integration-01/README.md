# Engineering Integration 01 — QA evidence

Executed 11 October 2026, Asia/Jakarta. Browser functional source:
`e4be4d0543b48e730b9f5695573cb2bf4fd6f14f`; main base:
`cc90fc73bea6ae399383d8538035c6454dc7e65a`.
Release/evidence commit and exact-head CI are independently verified in PR checks
and task handoff. These are development QA results, not PO/UAT/production approval.

| Page | Desktop 1440 | Tablet 768 | Mobile 390 |
| --- | --- | --- | --- |
| Login | [Desktop](login-default-1440.png) | [Tablet](login-default-768.png) | [Mobile](login-default-390.png) |
| Engineering Case | [Desktop](case-1440.png) | [Tablet](case-768.png) | [Mobile](case-390.png) |
| Reviewed Advisory | [Desktop](advisory-1440.png) | [Tablet](advisory-768.png) | [Mobile](advisory-390.png) |
| Authorized Inbox / ACK | [Desktop](inbox-1440.png) | [Tablet](inbox-768.png) | [Mobile](inbox-390.png) |

Case/Advisory/Inbox screenshots show **actual isolated persistent synthetic QA**,
without mocked Advisory/Inbox responses. Screenshots precede deliberate withdrawal;
the publication, ACK and audit remain stored and the tested Advisory is now WITHDRAWN.
The reused FIX-01 harness labels its synthetic statement FIX-01; it is a new
Integration-01 exercise, not a replacement of historical evidence.
Login screenshots are explicitly labeled synthetic UI states; no real credential
is entered in a screenshot. Loading/error/expired, password-change and dark-state
images from the same Login run are also retained here.

- [Persistent workflow](persistent-browser.json): 51 assertions, Case → independent
  review → Recommendation → Advisory review/publication → recipient ACK, reload,
  reconnect, security denials, withdrawal. Only Case save intentionally injects a
  retry503; stale Case revision is a real concurrent note.
- [Integrated product login](integration-browser.json): anonymous data denial,
  inline sign-in retains intended Cases/Advisories/Inbox page, clears credentials,
  keeps Secure/HttpOnly/Strict session and reloads authorized records.
- [Login UX](login-browser.json): 96 assertions, contrast, labels, focus, touch
  controls, bounded errors and real QA sign-in; original three records exact.
- [Bundle A regression](bundle-a-regression.json): 102 assertions, actual local
  factual routes plus isolated synthetic responsive/error-state fixtures.
- [Bundle B regression](bundle-b-regression.json): 129 assertions, actual asset
  deep links and authorized records plus labeled synthetic presentation fixtures.
- [Preservation](preservation.json) and [sessions](sessions.json): 1,206 immutable
  baseline rows exact, all 58 original sessions retained, three account invariants,
  five migration ledger entries, schema and 35 original container start times.
  Only monotonic last_seen_at changed for the session exercised across cutovers;
  normal sign-in updated_at and new synthetic records/session/audit rows are expected.
- [Rollback](rollback.json): full private backup clone restore and actual source
  rollback through launcher, retaining expanded Advisory/ACK constraint and data.

Private dumps, storageState, session/account hashes and original payloads are kept
outside Git. No source credentials, operational/personal advisories or raw attachments
are included. Final exact SHA/runtime/CI evidence is recorded in PR checks and handoff.
