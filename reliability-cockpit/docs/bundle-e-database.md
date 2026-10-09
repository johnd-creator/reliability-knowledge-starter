# E3 — approved QA application store and privileges

Proposed dedicated DB: nadi_qa_application; separate nadi_qa_owner (NOLOGIN),
nadi_qa_writer (NOLOGIN capability), nadi_qa_runtime (LOGIN via private secret).
These labels are operator-authorized naming, not provisioned infrastructure.
No real DDL/role/database creation is executed.

Dedicated mode is explicit; legacy Cockpit anchors are not fabricated. Exact
expected_database is mandatory, public Mart anchors rejected in either mode,
no environment DSN fallback. Existing legacy behavior remains unchanged.

## Operator-gated procedure — NOT executed on real QA

Every numbered mutation requires approved environment/SHA/action/role names.
Use DBA tools with bound/quoted identifiers, never interpolate unreviewed names.
No credentials in CLI argv, examples, shell history or reports.

1. Approve/select dedicated DB and owners, private DSN references; inspect actual
   current_database and tables, deny Mart anchors/wrong identity.
2. Create/select DB, NOLOGIN owner/capability and LOGIN service under DBA approval.
   Revoke PUBLIC CONNECT/TEMP/CREATE as appropriate; grant runtime CONNECT/USAGE
   only. No role owns DB/schema/tables except reviewed migration owner.
3. Remove PUBLIC application table grants and PUBLIC/default function/table/
   sequence grants; revoke schema CREATE from PUBLIC/runtime/capability. Audit
   existing defaults and all inherited memberships before any writer grant.
   Default privileges must be configured FOR the actual migration owner, not DBA.
4. Pre-migration private pg_dump --format=custom; catalog/checksum/counts, private
   permissions. Restore into a separate loopback *_test database and compare
   ledger, current/revision/audit/receipt/file-manifest fingerprints.
5. Canonical ApplicationMigrator status; checksums/order/anchors must pass.
   Apply only reviewed pending002→003→004→005 using approved owner. No startup DDL.
6. Canonical grant_writer fails closed on unsafe PUBLIC/default/schema/DB/table
   ownership or inherited capabilities. Grant ledger SELECT separately to
   capability. Runtime membership exactly capability; no admin/owner membership.
7. audit_runtime_access checks exact DB, owner, ACLs, PUBLIC/default grants,
   membership, no CREATE/TEMP/ownership and immutable audit/revision tables.
   Validate negative writes with runtime credential in a rolled-back fixture.
8. Test independent-review/CAS/session guard and durable audit before activation.
   Connection pool has approved capacity/overflow/statement/lock/connect limits.

Migration rollback: turn off QA ingress/routes and revoke runtime grant, preserve
all immutable records. No destructive down migration or restore over newer data.
Restore only into approved disposable clone for reconciliation; any real restore
requires separate recovery approval. Application writer never points to Mart.
Existing public NADI reader stays SELECT-only; source credentials never enter QA.

Read-only audit does not silently repair grants. DBA must deliberately remove
unsafe grants/owners then rerun. No RLS claim: asset scopes are enforced in trusted
service authorization; runtime DB role can reach QA application rows. Direct DB
access is privileged and must not be exposed to users.
