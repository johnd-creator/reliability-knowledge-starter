# NADI-ENG-BUNDLE-A-FIX-01 — Persistent QA Acceptance PASS

The Product Owner explicitly authorized the isolated QA CHECK expansion on
2026-10-11. Persistent QA acceptance now **PASS** for B2/B3/B4 within the existing
supported synthetic contracts. Production acceptance, actual engineer UAT,
organizational recipient authorization and operational rollout remain **PENDING**.
[PR #68](https://github.com/johnd-creator/reliability-knowledge-starter/pull/68)
remains unmerged; [PR #67](https://github.com/johnd-creator/reliability-knowledge-starter/pull/67)
remains independently OPEN and unchanged.

## Exact scope and source

Main: `cc90fc73bea6ae399383d8538035c6454dc7e65a`.
Previous PR/serving/helper HEAD: `01434fb26a29ba726fe59f663ca96d95bfd43c01`.
Branch: `codex/nadi-eng-bundle-a`. Only new test/evidence/documentation is committed
by FIX-01; application source and operational migration files are unchanged.
The single frontend continues serving that exact application SHA, clean/detached,
with identical backend and launch SHA. The later evidence commit is verified by
its own exact-head CI; it is not falsely labeled as the browser-serving commit.

Target verified: existing `nadi_live_dev_test`, `127.0.0.1:15443`, owner
`nadi_dev_fixture`, container `nadi-dev-live-postgres`. Every public table is
application-owned; no Mart/source anchors exist. No identity, credential, privilege,
operational environment or database was changed. The existing isolated QA bootstrap
owner has elevated PostgreSQL flags; they were inventoried and left unchanged.
This is not a production least-privilege writer readiness claim.

## Schema and transactional execution

Before: `nadi_human_record_kind_check` permits INSPECTION, RECOMMENDATION.
After: the tested helper replaces only that CHECK with
`nadi_qa_advisory_kind_check`, permitting INSPECTION, RECOMMENDATION, ADVISORY,
ADVISORY_ACK. Its new name is the existing PR #68 capability-probe contract, not a
second constraint or operational migration. `nadi_human_record_revision_check`,
all other constraints, original migration ledger/checksums and grants are intact.
No table DROP, TRUNCATE, schema reset, data deletion or standard migration edit.

The original tested `change_qa_advisory_schema` helper was executed with exact
expected database and `isolated-advisory-qa-only` acknowledgement. Caller-installed
SQLAlchemy transaction hooks applied `SET LOCAL lock_timeout='3s'`,
`statement_timeout='10s'`, and `idle_in_transaction_session_timeout='10s'`.
Preflight rejected any other active QA transaction or record-table lock. The helper
retains its transaction/advisory-lock and drift guards. No timeout/lock rejection
occurred. Immediately after DDL, all **919 existing rows**, including **51 sessions**,
matched the preflight snapshot exactly; all existing kinds satisfy the expanded rule.

Only the affected QA API was stopped/started through the pinned official
controller's `preflight`, `stop_unit('nadi-live-api.service')`, `api_start` functions.
Frontend MainPID **1370768** remained unchanged; QA API MainPID is **1557158**.
Next server PID **1370783** still owns loopback port3000; QA reload child **1557161**
owns loopback13036. No manual process replacement, second frontend or collector
restart. Port13035 remains retired. Authenticated capability now reports READY.

## Private backup and safe rollback

Official preflight backup: `backup-20261011-054012.dump`, mode0600,
SHA256 `d7bb0e58a672f92b7a9348202600f53de50d17e65a87c38d89233ff15b5477d3`.
Official post-workflow backup: `backup-20261011-054714.dump`, mode0600,
SHA256 `3768dc528782d367517c9458d263e31f076654e03d2c1a5e0bfcb4df8b0de029`.
Both restored successfully into temporary PostgreSQL16 clones; exact rows and
semantically identical constraints matched. Clones were removed after checks;
the active QA database was never overwritten.

After Advisory/ACK creation, **keep the expanded CHECK**. Do not invoke constraint
narrowing or remove records to force rollback. Supported application rollback may
select retained `8658c2fbd00bb78f1d8ee2b4462ccece4200a30e` through the official
backup → stop → switch → explicit start runbook when needed. Its old application
migration status (five APPLIED) and Case/Recommendation readers were verified
read-only against the restored expanded schema, with Advisory/ACK/history retained.
Prior live source rollback evidence remains available; FIX-01 does not repeat a
frontend cutover solely for documentation. See [the existing launcher runbook](nadi-dev-reset-01.md).

## Persistent acceptance and security

51 browser assertions PASS on real HTTPS3000 and the existing PostgreSQL store:
Case creation, frozen evidence, independent case review, approved linked
Recommendation and existing Action Board PLANNED workflow; Advisory draft,
independent review/publication, server-scoped recipient inbox, identity-bound ACK,
duplicate receipt stability, reload and new authenticated browser connection.
Database verification confirms Advisory CREATE/SUBMIT/REVIEW/PUBLISH/WITHDRAW
history, one ACKNOWLEDGE revision and one idempotency receipt for the durable ACK.
Withdrawal retains the immutable publication and ACK and blocks further receipt.

Anonymous access, unauthorized QA audience (including ADMIN-only), forged browser
role/audience headers, self-review/publication, stale revision, invalid CSRF and
untrusted Origin are rejected. Existing Secure/HttpOnly/SameSite=Strict cookie,
CSRF, RBAC and session policy remain unchanged. No global login enforcement,
account addition, organizational privilege change, email/push or external delivery.
18 factual/product/Engineering/login routes returned HTTPS200 with the existing
localhost certificate verified using its own CA file. HTTP200 is availability,
not a source-freshness or engineering-condition claim.

## Preservation and review

All **864 pre-existing immutable rows** remain exact after E2E, all **51 original
session rows** remain exact, and all **three original accepted QA records** remain
unchanged. Three original accounts retain identity, credential, roles, asset scope
and grant version; only normal sign-in `updated_at` changes occur. New records,
sessions and audit entries from successful/interrupted tests are retained.
All **35 original containers** retain ID/start time. Maximo/PI/CEMS, factual API,
Mart, operational stores, private source configuration and freshness policy are
untouched. `23496711.xls` and all five official PNG SHA256 values match originals.

Distinct review checked target guards, atomic CHECK replacement, before/after
hashes, migration identity, immutable source/publication/audit, trusted recipient
mapping, fail-closed write gates and rollback compatibility. No critical/high
finding remains within authorized QA scope. Corrected test/preflight failures are
recorded in [the evidence index](evidence/nadi-eng-bundle-a-fix-01/README.md).
Nine responsive screenshots were captured at 1440/768/390; layout/provenance
checks passed, desktop/mobile visual samples inspected. Visual PO approval remains
separate from execution/self-review.

Local backend: **161 tests PASS, zero skips**, exclusively disposable PostgreSQL.
194 existing frontend/UX/Engineering product assertions, safety, lint,
TypeScript and browser-script syntax PASS. Frontend build and fourteen contract
checks are required again by the delivery's exact-head GitHub workflow. Baseline
01434fb backend/frontend CI PASS; final evidence-head CI is independently checked
in PR rollup and the task handoff, not inferred from this runtime result.

| Milestone | Current gate |
| --- | --- |
| B2 — Advisory workflow | Persistent SYNTHETIC QA PASS |
| B3 — Recipient inbox / ACK | Persistent SYNTHETIC QA PASS |
| B4 — Local workflow / recipient handoff | PASS within existing QA contracts |
| Actual engineer UAT / PO visual review | PENDING |
| Organizational identity / external transport / ADV-04 | NOT AUTHORIZED; FUTURE GATED |
| Production / operational activation | NOT ACCEPTED |

Phase2/4 remain PARTIAL. Phase1 review **11Oct21:45 WIB**, PO checkpoint
**12Oct20:00**, hard expiry **13Oct00:00** remain independent and unchanged;
operator-review results UNKNOWN. No extension/reset/rollback policy action occurs.
Next action: senior/PO review of PR #68 and the retained QA records, then separately
approved real identity/custody/UAT/rollout tasks. No automatic merge or activation.
