# FIX-01 — actual persistent synthetic QA evidence

Executed 2026-10-11, Asia/Jakarta, on application/serving source
`01434fb26a29ba726fe59f663ca96d95bfd43c01`, main baseline
`cc90fc73bea6ae399383d8538035c6454dc7e65a`. This evidence/test-only delivery
advances PR #68 without changing application source or the serving checkout.
Exact delivery-head CI is independently verified in PR checks at handoff.

These screenshots show **actual isolated PostgreSQL QA records**, not mocked
Advisory/Inbox responses. They contain no login form, credential, cookie, DSN or
real personnel/plant advisory. Source identities are synthetic QA identifiers.

| Actual persisted QA page | Desktop 1440 | Tablet 768 | Mobile 390 |
| --- | --- | --- | --- |
| Case | [Case](case-1440.png) | [Case](case-768.png) | [Case](case-390.png) |
| Approved published Advisory | [Advisory](advisory-1440.png) | [Advisory](advisory-768.png) | [Advisory](advisory-390.png) |
| Authorized recipient / durable ACK | [Inbox](inbox-1440.png) | [Inbox](inbox-768.png) | [Inbox](inbox-390.png) |

Screenshots precede the deliberate withdrawal test. The tested publication is now
WITHDRAWN; its immutable publication, acknowledgement and full history remain in
QA. This demonstrates preservation, not current delivery to Operations personnel.
The fixed OPERATIONS_QA category belongs only to the existing reviewer exercise
identity. Actual organization roles, recipients and delivery are not enabled.

- [Preflight / private backup verification](preflight.json): exact loopback QA
  identity, application ownership, 98 grant rows, counts, sessions, known CHECKs,
  no risky active transaction/table lock; restore into a temporary PostgreSQL16.
- [Transactional migration](migration.json): only the kind CHECK changed; 919
  existing rows, ledger, privilege and revision CHECK exactly preserved. Lock
  timeout 3 seconds, statement timeout 10 seconds; helper from original PR HEAD.
- [Persistent browser acceptance](persistent-browser.json): 51 assertions,
  real Case → independent review → Recommendation → Advisory review/publication
  → authorized receipt, reload/reconnect, audit, forbidden requests and withdrawal.
  Case save retry uses an explicit 503 fault injection; CAS uses a real concurrent
  note. Neither Advisory nor Inbox has mocked responses.
- [Preservation](preservation.json): 864 immutable existing rows and all 51 original
  session rows unchanged; three original accepted records and account invariants
  intact. Normal login account timestamps only; 35 original container/start times,
  workbook and five reference PNG hashes preserved.
- [Rollback readiness](rollback.json): post-workflow backup restored into a clone,
  old `8658c2f` application readers/migration status compatible with expanded schema;
  all Advisory/ACK/audit/session data retained. No active DB restore or live cutover.
- [Local validation/review](validation.json): disposable backend tests, frontend
  assertions, lint/TypeScript/safety and relative documentation links.
- [Runtime](runtime.json): 18 HTTPS routes, both backends available, trusted local
  certificate, accurate clean source/backend/launch SHA, original frontend PID.

Private dumps and row/session/account comparison material remain outside Git.
Raw session hashes, passwords and original private fixture payloads are not copied.

Meaningful failures: an overly strict preflight script initially assumed the kind
CHECK was the only CHECK, then correctly verified the existing revision CHECK too.
Dump/restore rendered equivalent kind-array casts differently; only the two
explicitly verified equivalent expressions were normalized, with all other schema
and row comparisons still strict. No DDL ran before complete preflight PASS.
The first browser run timed out on an exact label containing select-option text;
the locator was changed to the combobox accessible-name prefix, then all checks
passed. Its new Case/Recommendation rows were retained. Frontend checks initially
hit sandbox subprocess EPERM and passed when rerun with the required permission.
No failed attempt was repaired by deleting records or loosening authentication.
