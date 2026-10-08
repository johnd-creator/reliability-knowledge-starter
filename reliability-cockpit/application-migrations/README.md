# Application-owned candidate migrations

This namespace is separate from canonical Mart migrations. Engineering records
belong only to the existing Cockpit application store. These files are not wired
into init-db, mart-migrate, Compose or runtime startup. No operational DDL occurs.

`002_engineering_workspace.sql` is a reviewed-candidate additive PostgreSQL
migration after the existing application schema. Validate using disposable
fixtures only. A future deployment must prove DATABASE_URL refers to the
application owner, not RELIABILITY_MART_DATABASE_URL, and provision an explicit
least-privilege application writer. No administrative DSN fallback is permitted.
Tables use an independent metadata registry; the application never creates them
implicitly. A future migration ledger/ownership preflight is an activation
prerequisite, not implemented production tooling in this bundle.


Bundle B adds candidate `003_application_identity.sql` and `004_human_records.sql` after 002. Disposable PostgreSQL acceptance validates all three in order while retaining an existing factual application relation. The files are deliberately not idempotent raw scripts: a future reviewed checksum/ledger runner is required before operational use. No runtime migration runner/initializer mounts these tables. Proposed runtime grants: session and current human record SELECT/INSERT/UPDATE; security activity, revisions and receipts SELECT/INSERT only. Roles must not own schema/relations or gain source/Mart writer privileges. Disable/revoke candidate capabilities for rollback, preserving audit history. This is a proposal, not executed provisioning.
