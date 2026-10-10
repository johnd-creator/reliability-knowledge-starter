# Engineering QA evidence — 11 October 2026

Implementation source: `2a7678d82f6f0e8769a03ca09857c59f2f37f338`, based on main
`cc90fc73bea6ae399383d8538035c6454dc7e65a`. Delivery docs may advance the PR HEAD;
exact final CI and serving SHA must be checked independently. No PO acceptance.

| Evidence | Desktop 1440 | Tablet 768 | Mobile 390 |
| --- | --- | --- | --- |
| Case UI: actual persisted SYNTHETIC QA | [Case](case-1440.png) | [Case](case-768.png) | [Case](case-390.png) |
| Recipient UI: mocked DEMO, NOT persistent advisory acceptance | [Inbox](inbox-1440.png) | [Inbox](inbox-768.png) | [Inbox](inbox-390.png) |

The Case images show only isolated QA records. Advisory images use sanitized
browser response fixtures with DEMO/SYNTHETIC labels. They prove rendering and UI
interaction, not durable publication in the persistent preview store. That store
retains its original constraint; advisory/inbox APIs and write controls are gated.
Real HTTPS publication/receipt/audit acceptance runs only in disposable PostgreSQL.

- [Engineering browser report](engineering-browser.json): 31 assertions, including
  actual Case create/retry, preserved edits on 409, independent review, linked
  Recommendation and Action Board local planning. Advisory review/publish/receipt/
  withdrawal UI is explicitly mocked. Full provenance hashes wrap on narrow screens.
- [Bundle A regression](bundle-a-regression.json): 102 assertions on `0dc5268`.
- [Bundle B regression](bundle-b-regression.json): 129 assertions on `0dc5268`.
  Later presentation change only removes hash ellipsis and is covered by the final
  Engineering responsive checks. Neither report is mislabeled as final exact-head CI.
- [Rollback](rollback.json): exact PR #67 SHA, clean checkout, secure login, both
  backends available and new QA Case retained through the official launcher.
- [Preservation](preservation.json): 35 original containers/start times, 481 original
  non-account rows and 39 original session rows retained. Three original account
  identities/grants/credentials match the backup; two `updated_at` sign-in timestamps
  changed normally. Persistent advisory schema remains unchanged. Five PNGs/workbook
  retain their original hashes. Private row hashes/backups are not committed.

Meaningful failed attempts are retained: a browser selector matched a hidden
status option, and an acknowledgement assertion ran before refreshed receipt state.
The selectors/waits were corrected and all 31 assertions passed. Synthetic records
from those runs remain in QA; no cleanup deletes audit/history. The local PG18
client/PG16 restore mismatch was corrected using matching PG16 test-container tools;
the complete 161-test suite then passed with zero skips.
