# NADI-ENG-BUNDLE-A — Engineering Case Management & Advisory Distribution

Scope: authenticated **SYNTHETIC QA only**. Operational distribution, engineer UAT,
plant instructions and external notification remain pending. Phase 2 and Phase 4
remain PARTIAL. PR #67 login polish is independent and is not included or merged.

## Architecture decision

One integrated PR keeps the case UX, existing recommendation controls, advisory
contracts and recipient experience reviewable together. It uses the existing
application-owned `nadi_human_record`, revision and receipt tables; no competing
store, action tracker or transport is introduced. Operational `create_app` does
not mount the new routers. The dedicated QA factory supplies the existing trusted
session dependency; its HTTPS cookie, CSRF, Origin, revocation and asset grants
remain authoritative. Frontend development and QA opt-ins are both required.

An advisory requires BOTH an approved Case and an approved Recommendation for the
same canonical asset. It freezes exact source revisions and SHA256 values. Submit,
review, publish and receipt transactions recheck upstream eligibility. Publication
locks the advisory and then Case/Recommendation rows in the existing workflow
order. Independent advisory review/publication excludes its author/contributors
AND upstream case/recommendation contributors, assignee and responsible person.

Recommendation follow-up revisions may advance without changing the approved
statement. The frozen source revision is retained in immutable history, its digest
is verified, and current approved content must still match. A case revision,
review/content change or reopened upstream makes availability `STALE_UPSTREAM` and
blocks acknowledgement. It never rewrites the publication snapshot.

Publication creates an allowlisted snapshot with references, reviewed statement,
evidence limits, attribution and recommendation text. Private attachment contents
and download URLs are excluded. `IN_APP_QA_AVAILABLE` does not mean sent/delivered.
`VIEWED` remains `NOT_RECORDED`. A durable, identity-bound `ADVISORY_ACK` revision
means receipt only; it is not review, work authorization or physical completion.
The Action Board reuses Recommendation's local follow-up and independent
completion-verification states. No Maximo command is introduced.

QA exercise membership is a fixed server policy: AUTHOR gets MAINTENANCE_QA and
ENGINEERING_QA; REVIEWER gets OPERATIONS_QA and ENGINEERING_QA; ADMIN alone gets no
recipient membership. These mappings exercise existing trusted identities and
asset grants; they make NO claim about actual departmental membership. Browser
parameters cannot grant an audience. Real operator identity/scope provisioning
requires a separate approved task before ADV-04.

WITHDRAW retains publication content and attribution. A replacement is a new
advisory referencing a withdrawn same-asset predecessor, with a fresh independent
review/publication cycle. It does not silently republish or edit old versions.
Recipient views retain withdrawn/stale notices; acknowledgement is disabled.
Author/reviewer history is separately authorized and server paginated. Recipients
receive the publication snapshot and only their own receipt, not private drafts.

## QA schema prerequisite and rollback

The original SQL constraint permits only INSPECTION/RECOMMENDATION even though the
JSON store is generic. `src/repositories/qa_advisory_schema.py` provides an explicit,
transactional QA-only constraint expansion to ADVISORY/ADVISORY_ACK. It is NOT in
the operational migration list and is NOT executed at startup. It requires a
loopback PostgreSQL `*_test` URL, exact expected database, application-store/Mart
boundary checks and acknowledgement `isolated-advisory-qa-only`. It preserves all
rows, original migrations/checksums, privileges and identities. Unexpected
constraints fail closed. Disposable PostgreSQL tests exercise expansion, retry,
rollback and refusal to discard new QA records.

Constraint expansion was executed only in disposable PostgreSQL tests. Automatic
approval review rejected applying it to the persistent `nadi_live_dev_test` store,
because the task limits migration execution to disposable QA. No persistent DDL
was performed. The authenticated capability endpoint reports
`BLOCKED_SCHEMA_PREREQUISITE`; advisory and inbox routers remain unmounted and
write controls remain disabled in that preview. A separate explicit approval is
required before changing that store. Original row hashes and an official private
backup are retained. Operational DDL is forbidden. Schema rollback refuses while advisory records exist; do not delete
records to force it. Frontend/API rollback to the retained previous SHA remains
compatible with the expanded constraint because old services select their own
record kinds. Keep the new QA records and the original private backup.

## Product routes

- `/engineering/cases`: server-filtered Case register, structured create/edit,
  frozen evidence links, notes, review/revision controls and immutable history.
- `/recommendations` and `/action-board`: existing authorized records with
  structured draft/review/local follow-up/independent completion controls.
- `/engineering/advisories`: draft, independent review, publication, withdrawal,
  reviewed replacement linkage and immutable audit history.
- `/engineering/inbox`: trusted audience/asset-scoped publication and receipt.
- `/engineering/local`: retained diagnostic workbench and all prior capabilities.

Forms use canonical APIs, `expected_revision` and idempotency request IDs. Failed
retry preserves the same intent ID. Revision conflict preserves in-memory edits
and requires an explicit latest-version read/comparison. Identity changes unmount
scoped forms and records; nothing is saved to browser storage.

## Validation and remaining gates

Implementation/self-review evidence is recorded below after execution. CI alone
never proves runtime visibility or Product Owner acceptance. Browser evidence uses
1440/768/390 widths and visibly synthetic QA content. The five original PNGs and
`23496711.xls` remain unchanged. No collectors, operational APIs/stores, source
acquisition or freshness policy are changed.

Phase-1 independent review remains separate: 11 October 2026 21:45 WIB review,
12 October 20:00 decision checkpoint and 13 October 00:00 hard expiry. This bundle
does not extend/reset those gates. Actual departmental identity, real distribution,
engineer UAT and operational activation are **PENDING**.

### Delivery checkpoint

[PR #68](https://github.com/johnd-creator/reliability-knowledge-starter/pull/68)
contains the integrated implementation. B0/B1 PASS; B2/B3 implemented and tested in
disposable QA, persistent preview BLOCKED by schema prerequisite; B4 local workflow
PASS with recipient runtime handoff gated; B5 review/tests/PR PASS, full persistent
end-to-end preview PARTIAL. Overall delivery **PARTIAL**, not operational acceptance.

Local validation: 161 PostgreSQL backend/security/real-HTTPS tests, zero skips;
all existing frontend assertion scripts (37/25/38/10/8/9/16/43 assertions), eight
new Engineering assertions, product safety, TypeScript, lint and production build.
A separate initial SQLite run had 97 pass/58 skip; those skips were not counted as
passes. Exact-head GitHub backend/frontend CI passed on implementation `2a7678d`
([run](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/38072796251)); final delivery
checks are the PR's exact head, independently verified at handoff.

Browser: 31 Engineering assertions, 102 Bundle A and 129 Bundle B assertions.
Actual Case -> independently reviewed Recommendation -> existing Action Board
local planning works. Advisory UI has sanitized DEMO fixture evidence; actual
HTTPS persistence/receipt runs in the disposable tests. PR #67's unmerged login
presentation is not integrated or claimed as tested on this main-based branch;
its secure login was verified during exact-SHA rollback. No auth policy changed.

Review repairs: canonical product Case links retain diagnostics separately;
selection survives reload through the URL; new/edit forms cannot overlap; failed
intent IDs are retained; invalid blank lines reach backend validation; source
SHA256 values wrap fully instead of ellipsis. Backend revalidation, scope and
independent publication/acknowledgement tests pass. No critical/high finding is
left silently open. The persistent-schema prerequisite is explicit and fail-closed.

See [responsive screenshots, reports and preservation evidence](evidence/nadi-eng-bundle-a/README.md).
Original private backup: `backup-20261011-002620.dump`. Rollback to PR #67 source
`8658c2fbd00bb78f1d8ee2b4462ccece4200a30e` was demonstrated without DB restore,
collector/API restart or schema change; the Engineering candidate was reselected
through the same launcher. The exact delivery HEAD appears in the development
status banner; no permanent second frontend exists.

Next bounded task: explicitly authorize or decline the QA-only constraint change
for the preserved `nadi_live_dev_test` store, then perform persistent advisory
publication/receipt UAT there. Real organizational identity, external distribution,
engineer UAT and operational activation still require their own approvals.
