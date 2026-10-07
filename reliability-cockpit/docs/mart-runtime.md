# Existing Reliability Mart governance operations

Mart belongs to existing `maximo-db/maximo_collector`. Legacy Cockpit
`DATABASE_URL` and canonical reader `RELIABILITY_MART_DATABASE_URL` are distinct.
No new operational database, source request, mapping seed or legacy fallback.

## Explicit credentials and migration owner

Managed configuration comes from `.env.platform`; standalone local dotenv
remains allowed. Managed Cockpit entrypoints use `COCKPIT_CONFIG_MODE=managed`
to skip local/home dotenv. Three separate settings are deliberate:

- `DATABASE_URL`: legacy Cockpit only; never used for governance.
- `RELIABILITY_MART_DATABASE_URL`: NADI reader, `nadi_mart_reader` in existing Mart.
- `RELIABILITY_MART_ADMIN_DATABASE_URL`: controlled local schema/mapping writer;
  maintenance/readiness/projector only, never the public API.

`RELIABILITY_MART_EXPECT_DATABASE` must explicitly name the existing owner DB.
The runner requires existing Collector/Mart anchors and canonical PKs. It will
not initialize missing stores, adopt untracked governance tables, or replay
legacy `001_init.sql`. Package path is explicit in the Docker image;
standalone uses repository SQL files. Only canonical Cockpit migrations
`002_asset_af_mapping.sql` and `003_asset_af_mapping_provenance.sql` are allowed.
Their checksums are recorded in `nadi_mart_schema_migration`. Drift, unknown or
out-of-order ledger, missing model columns, FK/index/lifecycle constraints,
unvalidated constraints, or wrong target fail closed.

Status is SELECT-only and creates no ledger/table. Apply takes a local advisory
transaction lease, uses 5s lock/30s statement timeouts and one atomic 002/003
transaction. Short SHARE locks on all 17 existing tables compare count/content
fingerprints before/after, including WO cursor/recovery evidence. No collector
stop, bootstrap, registry reload or historical recollection is required.
If a schema differs, preserve it and reconcile explicitly; do not force DDL.

## Safe managed operator sequence

Keep actual project identity and all accepted ignored overrides. Current
runtime control checkout is the historical feature checkout; inspect it first.
Use a reviewed candidate worktree/image for changed services only. Do not run
broad `up --build`, `down`, init-db, migration reset or volume replacement.
Never omit `secrets/maximo-wo-recency-002.runtime.yaml` (reviewed WO-only worker,
API/projector image) or the accepted PI override when operating this project.

1. Confirm PR #15 merged and new baseline includes it. Inventory real schema,
   owning DB, role/DSNs, worker/projector identities and WO recovery floor.
2. Make a private full `pg_dump -Fc` of the existing owning Maximo/Mart DB;
   record SHA256/size/time and validate its `pg_restore --list` catalog.
   A catalog check is not a restore drill. Do not publish backup bytes.
3. Configure explicit reader/admin DSNs and expected owner DB in private
   `.env.platform`, preserving all existing secrets/overrides.
4. On the reviewed source-controlled Compose, inspect then explicitly apply:

   ```bash
   docker compose --env-file .env.platform -f compose.yaml --profile mart-maintenance run --rm --no-deps mart-migrate
   docker compose --env-file .env.platform -f compose.yaml --profile mart-maintenance run --rm --no-deps mart-migrate cockpit mart-migrate --apply
   ```

   Add actual accepted overrides to both commands. Alternatively use the
   reviewed image on the existing platform network with a private admin env
   file; this avoids accidentally resolving/recreating unrelated old services.
5. Provision named reader deliberately using `cockpit mart-reader --apply`.
   `RELIABILITY_MART_READER_PASSWORD` supplies at least 24 private characters
   for first creation. Status/default never creates a role. Existing privileged
   attributes, memberships, ownership or table-write grants are rejected.
   Only CONNECT/schema USAGE and SELECT on nine named Mart tables are granted;
   `default_transaction_read_only=on`, no memberships/owner/source credentials.
   Future table grants require explicit review; no blanket default privileges.
   PostgreSQL PUBLIC privileges remain unchanged; this is a SELECT-only Mart
   relation boundary, not a global ban on temporary objects.
6. Check reader login and table grants. Recreate only `cockpit-api` with
   `up -d --no-deps --no-build cockpit-api`, preserving legacy DSN and all
   current override/image identities. Do not restart sources/projector/PI.
7. Validate factual NADI 7/30-day counts, mapping GET (UNMAPPED), cursor/floor,
   live local projection and PI stored acceptance. No real pilot mapping here.

## Ready gate and projector

Managed `mart-ready` runs status with `--require-ready`; it never applies DDL
and depends on healthy existing maximo-db only, not source acquisition.
`mart-projector` and `cockpit-api` wait for successful readiness. Projector uses
existing local incremental `mxcollector mart-project`, contracts mounted read-only
at `/contracts`, explicit writer DSN and 300s post-cycle pause. It does not query
Maximo or change source cursors. Existing projector can remain running while
additive governance is applied; ordering governs later reproducible starts.
For a new installation, base Maximo initialization must first be deliberately
completed before this gate can pass; governance is never automatic startup DDL.

Managed Maximo/Cockpit URLs explicitly choose packaged psycopg v3 driver.
Source-controlled Compose defines the accepted local projector but existing
private reviewed WO override still pins runtime image/WO-only source command.

## External collector mode

`compose.external.yaml` requires `RELIABILITY_MART_DATABASE_URL` explicitly.
Point it to the existing external Mart with its SELECT-only role and reachable
host; `host.docker.internal` has Linux host-gateway mapping. No Mart DB,
projector, admin credential, governance migration or source worker is created
in external mode. Its Cockpit init affects legacy Cockpit only. Existing
external Mart administration happens separately with writer/expected DB,
not implicitly through consumer startup. Missing reader DSN fails Compose;
missing schema remains unavailable, never replaced by legacy data.

## Mapping administration and recovery

`cockpit mapping` now requires **admin** DSN plus expected DB and ready canonical
schema; it cannot reuse the API reader or legacy URL. Workflow is controlled
CSV dry-run → PROPOSED import → explicit human verify → resolve → retire.
Canonical migrations provide identity, CENTRAL_PI alias input, PRIMARY_EQUIPMENT,
PROPOSED/VERIFIED/RETIRED and provenance constraints. No AF search/inference.
Use disposable synthetic PostgreSQL fixtures to exercise lifecycle, never
plausible operational mappings. An actual-Mart dry-run with nonexistent synthetic
Asset is safely rejected and writes zero. Real NADI-IDN-002 requires its own
human-approved evidence; schema readiness does not verify an Asset/AF identity.

Rollback an API issue by preserving/reusing its prior image and explicit DSNs;
prefer the newly scoped reader if compatible. Do not roll back facts/schema by
dropping mapping tables, deleting ledger, resetting cursor or restoring over a
live owning store. Canonical governance additions can remain empty while a
service issue is repaired. Destructive backup restore requires separate reviewed
recovery/quiescence and is not part of this task.
