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
