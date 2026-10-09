# Application migration and recovery candidate

ApplicationMigrator is explicit/injected, status read-only, apply transactional
and advisory-locked. Canonical002→003→004 checksummed ledger refuses untracked
relations, checksum/order drift, missing tables and wrong database/Mart anchors.
Existing operational schemas without this ledger require reviewed reconciliation;
never auto-adopt them. It is not called by startup/init-db/mart-migrate.

Provisioning owner: separate schema owner controlled by platform administrator.
Existing NOLOGIN writer capability has SELECT/INSERT/UPDATE current records and
SELECT/INSERT revision/audit/receipts only. Application service LOGIN membership,
CONNECT, secrets, public-schema CREATE/default privileges and legacy-table grants
must be audited separately. Never give writer ownership, DDL, Mart write access
or source credentials. Grants only operate on explicit application relations.

Backup/restore procedure before future provisioning: private pg_dump custom
backup of existing owning application store; record checksum/catalog and schema/
record counts; restore into disposable isolated database with pg_restore; compare
records, revisions, receipts and ledger; validate read-only Mart credentials
separately. Restore drill and accountable platform review are activation gates.
Rollback disables routes/revokes runtime authority; preserve immutable records.
No destructive down migration or restore over newer evidence. This bundle only
executes fixtures. Existing source/Phase1 data and operational config untouched.
