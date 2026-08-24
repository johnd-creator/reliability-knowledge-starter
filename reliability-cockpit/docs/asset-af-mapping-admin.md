# Governed Asset to PI AF Mapping Administration

This is an internal, operator-run workflow for candidate governance data. It
does not query Maximo or PI, write to either source system, or expose a browser
mutation API.

## Import format

The CSV header must contain these fields:

```text
canonical_asset_id,pi_source_id,af_server_ref,af_database_ref,af_element_ref,mapping_role,evidence_method
```

Optional fields are:

```text
evidence_ref,verification_note,source_assetnum_snapshot,source_siteid_snapshot,source_orgid_snapshot,af_path_snapshot,af_element_name_snapshot
```

The file must explicitly identify both sides. `mapping_status` is not an
accepted column. Credentials, authorization material, cookies, PI usernames,
live values, and host credentials are not accepted fields. Use synthetic
references in development; see
[`asset-af-mapping-import.example.csv`](./asset-af-mapping-import.example.csv).

The initial bounded limits are 500 data rows, 2 MiB per file, and 2,000
characters per cell. Duplicate headers, missing or unexpected columns, blank
required identifiers, and spreadsheet formula-style values beginning with
`=`, `+`, `-`, or `@` are rejected.

`pi_source_id` is allowlisted to the governed `CENTRAL_PI` alias used by the
foundation fixtures. AF references are checked syntactically only; AF
existence is not validated through a live PI request.

## Commands and lifecycle

Run a validation-only dry run first:

```bash
cockpit mapping import --file ./candidate-mappings.csv --dry-run
```

The machine-readable result reports `rows_seen`, `valid`, `accepted`,
`rejected`, `duplicates`, `unknown_assets`, `conflicts`, `dry_run`, and bounded
row results. Typical reason codes include `VALID`, `MISSING_REQUIRED_FIELD`,
`UNKNOWN_ASSET`, `NON_REGISTERED_ASSET`, `DUPLICATE_INPUT`,
`ACTIVE_MAPPING_CONFLICT`, `INVALID_ROLE`, `INVALID_EVIDENCE_METHOD`,
`UNSUPPORTED_PI_SOURCE`, `FORMULA_VALUE`, and `OVERSIZED_CELL`.

After a clean dry run, the non-dry-run command validates the entire batch again
and writes all rows in one transaction:

```bash
cockpit mapping import --file ./candidate-mappings.csv
```

Any invalid row causes zero writes. Re-importing the same active proposal is a
deterministic conflict and does not create a duplicate. Retired history is
preserved and does not establish readiness.

Every imported row is `PROPOSED`, even if a file author attempted to provide a
verification value. `PROPOSED` is never usable identity. A human must run the
explicit transition with an actor and evidence:

```bash
cockpit mapping verify \
  --mapping-id <mapping-id> \
  --verified-by <human-operator-id> \
  --verification-note "Reviewed against controlled evidence"
```

`VERIFIED` requires `verified_at`, `verified_by`, and either
`verification_note` or `evidence_ref`. A verified row cannot be silently
re-verified; correction requires retirement and a new proposal. Retirement is
also explicit and keeps provenance:

```bash
cockpit mapping retire \
  --mapping-id <mapping-id> \
  --retired-by <human-operator-id> \
  --reason "Superseded by a new proposal"
```

`RETIRED` requires `retired_at`, `retired_by`, and `retirement_note`. It stays
available as historical governance evidence and cannot be reactivated directly.

## Boundaries

- Only the internal mapping command store can write the mapping table.
- `MartDatabase`, `MartQueryRepository`, and the public Reliability API remain
  SELECT-only.
- The public mapping endpoint remains GET-only and has no POST, PUT, PATCH, or
  DELETE route.
- No description, Asset-name, AF-name, PI-tag, Levenshtein, embedding, or LLM
  matching is performed.
- No production mappings are seeded by this workflow.
- Migration `003_asset_af_mapping_provenance.sql` is schema-only and must be
  applied deliberately in a later runtime migration task; this task does not
  apply it to an active Mart.
