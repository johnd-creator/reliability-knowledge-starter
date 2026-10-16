# Migration packaging, grants and writer compatibility

## Immutable package

[Machine-readable SHA256 manifest](../NADI-AUD-02B-B5-MIGRATIONS.json) fixes forward
001→002→003 prerequisites and candidate 004→005→006. No migration file is edited.
The deployed store's actual owner, applied checksums and schema are NOT_INSPECTED.
Do not confuse other components' migration numbers with these Maximo files.

004/005 contain explicit BEGIN/COMMIT. 006 has no transaction wrapper. Future
operator tooling must use error-stop and a whole-file transaction for 006 (e.g.
libpq single batch plus explicit commit/rollback, as tested), never apply individual
statements with autocommit. Do not wrap 004/005 in a larger transaction expecting
its outer rollback to undo their explicit commits. Record each successful step's
checksum and do not advance the operator ledger on failure. No new operational
migration ledger/helper is installed by B5.

Tests use both existing ORM fixture setup and clean SQL 001→006 installation.
Repeated 004/005/006 fail on the existing first table, followed by explicit rollback;
existing table inventory is unchanged. Out-of-order 005 without 004 is refused.
There is no idempotent auto-repair, down migration or evidence-table deletion.
Candidate schema checks include reviewed columns, types, PK/FK/check definitions,
indexes, trigger enabled state/body and immutable audit history. Actual SQL-created
canonical schema compatibility is tested separately from ORM fixtures.

B5-CATALOG-02 was corrected narrowly in the disabled reader: both complete reviewed
SQL and ORM catalog hashes are accepted. All five catalog groups stay in the hash;
no arbitrary index set is accepted. The actual SQL index-drift negative still blocks.
The SQL hash is45e77c7cc8b51de1d10d5e77d29a84607b0f5fbcbc657361e94559d65e25d6a2;
the original ORM hash remainsc36d02ad2f137456ee38d247c23c0d0ad0519a676f3098359c70e96c70a40afa.

PostgreSQL 16 is the documented Mart target. B4 qualified 16.15 in CI and 18.6
locally; B5 records its actual versions/results in the final CI evidence. This is
not a promise of all PostgreSQL major/minor versions or pre-existing schema layouts.

## Proposed privileges (not executable operational grants)

All application roles: LOGIN only if needed, NOSUPERUSER, NOCREATEDB, NOCREATEROLE,
NOREPLICATION, NOBYPASSRLS, no administrative memberships. No database CREATE/TEMP;
explicit schema USAGE. Credentials stay separate and outside repository/logs.

| Role | Objects / required actions | Prohibited / ownership / caveat |
| --- | --- | --- |
| Migration owner | Own dedicated schema; CREATE tables/indexes/functions/triggers, ALTER for reviewed migration package | No app credentials; no source acquisition; elevated DDL unavailable to app roles. Actual synthetic non-super schema-owner install tested. |
| Collector source reader | SELECT approved Equipment/WO columns | No canonical/candidate/cursor mutation, DDL or admin role. Synthetic SELECT succeeds, source UPDATE and evidence access denied. |
| Participating full projector | SELECT Equipment/WO; SELECT/INSERT/UPDATE canonical two domains, capture domain/run/item/target, required B2 ledger and queue/event tables | No source/cursor UPDATE, DELETE/TRUNCATE, schema CREATE, trigger disable or ownership. Non-owner full-capture tested. Mutable source-free scope still trusted application code. |
| Deferred/replay writer | Above plus scoped B2 family/version/dependency/event/occurrence and B3 queue/event inserts/updates | **GAP:** B3 source FOR SHARE requires UPDATE privilege. Do not grant source UPDATE merely to make replay pass. Restricted role design requires separate approval/remediation. |
| Coverage reader | USAGE + column SELECT capture items excluding payload; SELECT other reviewed candidate tables and canonical proof rows | No source tables/cursors, mutations, DDL, CREATE/TEMP or ownership. Existing B4 actual role tests required; fixed scope is not caller authorization. |
| Operational administrator | Reviewed backup/restore and emergency ownership actions, outside app credentials | Explicit human authorization and audit; superuser/owner bypass is outside application guard guarantees. |

Functions are SECURITY INVOKER; trigger execution needs underlying table privileges.
No SECURITY DEFINER helper is introduced. Function EXECUTE/search_path/role
membership and schema ownership need operator review; do not imply the role matrix
is an operational grant script. An app role able to write canonical targets must
be trusted not to issue arbitrary unfenced SQL; the candidate is not a malicious
SQL-writer sandbox. SQL constraints/trigger tests prove specific immutability,
CAS/audit/fence checks, not universal prevention of deliberate forgery.

## Canonical writer compatibility (checked-in source inventory)

| Path | Commit/locking behavior | Compatibility |
| --- | --- | --- |
| B1/B2/B3 `ProjectionStore.process` / `ReplayStore` | Same Session target+sidecar+receipt+ledger; domain/fence/expiry | Participating, co-located; replay role gap pending |
| `LocalMartProjector.project` → `MartWriter.persist_collection` | Independent canonical transaction, separate legacy state/watermark | **RESTRICTED:** no shared candidate fence; stop/exclude under separate rollout authority |
| `ControlledMartLoader.run` / CLI mart-load and bootstrap | `persist_collection` separate transaction; may acquire sources when invoked | **RESTRICTED:** never invoked here; future freeze/exclusion required |
| `MartWriter.persist_collection` direct callers | Own commit, no capture receipt/fence | **RESTRICTED** for candidate domains |
| Registry reconciliation/import | Registry ownership; no inference that technical targets prove membership | Separate governed workflow; do not change it for coverage |
| Cockpit mapping/Engineering stores | Separate authorized domains/stores; not an equivalent projector | No activation or privilege expansion under B5 |

Search scope: checked-in `maximo-collector/src` and `reliability-cockpit/src` Python
canonical-target references plus CLI/loader callsites. External scripts, ignored
overrides and deployed processes may add writers; actual exclusion remains unproven.
A legacy target-drift simulation demonstrates detection before the next candidate
receipt; it does not prevent the initial incompatible write. OPERATIONAL_GO=NO.
