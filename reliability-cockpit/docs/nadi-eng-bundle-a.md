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
