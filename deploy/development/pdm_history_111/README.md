# Exact PR110/PR111 historical-source support

This is a separately selected support package. It does not replace the generic
launcher modules in `deploy/development`, install itself, migrate a database,
change privileges or activate an application.

The five files in `controller/` are byte-identical to the independently reviewed
local bridge. The only accepted compatibility transition remains:

- From `e84eaec0e38e57cf0f057abaeda04e34739b01f8` (PR110).
- To `85e6bb61eb5cb724e436846b9bdeee31709dffd4` (PR111).
- Migration007 SHA256 `95806119fe0a131ec8c64733da9f41de85e59389cae3ee80820876f27abad524`.
- PostgreSQL16 schema digest `7dc4b17be2b6281887fcd02fe2042794d8a5f1d67bf05cdad3856d54c8f56411`.

The commit which publishes this support package is **not an accepted runtime
target**. A future different target needs a new reviewed compatibility set; never
substitute its SHA into these constants or the private approval manifest.
`runtime_contract.json` exposes public source-object/checksum bindings only.

The bridge exposes the full002–007 ledger. PR110 may start with007 wholly absent
or exactly applied. PR111 startup/forward selection requires007 applied. Unknown
ledger, partial schema, changed source/schema/default/index/constraint/trigger/
RLS, missing bridge and changed/stale receipts fail closed. The actual imported
source controls dispatch; an old config cannot give a candidate the old exception.
No source monkeypatch, hidden ledger rows, startup DDL or automatic data restore.

## Prepared installer

`python install_prepared.py` reports preparation only and does not read runtime
state. Actual installation additionally requires explicit human authorization,
`--apply`, an absolute `--approval-file` and the exact execution acknowledgement.
The approval must be owner-private and contain an independent GO, all five exact
file hashes, the hash of this packaged installer, and freshly reconciled installed
wrapper/manifest/active-state hashes. It is never committed or included here.
The earlier task-local installer's approval cannot authorize this path-adapted
installer: its executable hash differs and must be reviewed independently.

Public source files may be world-readable; their ownership, regular-file identity,
non-writable-by-others mode and reviewed bytes are checked. Runtime, review and
configuration files retain strict owner-private checks. Installation copies source
into an immutable owner-private release, swaps metadata atomically and preserves
known preimages on failure. Unknown concurrent metadata is never overwritten.
It neither restarts units nor changes the active application pointer.

The installer is restricted to the existing johnd-creator laptop repository;
it is not a generic deployment tool. Installation and live execution are not
performed by publication or CI.

## Execution and recovery gates

Follow [the exact migration/activation proposal](../../../reliability-cockpit/docs/nadi-complete-demo-activation-proposal.md)
from the repository root path `reliability-cockpit/docs/nadi-complete-demo-activation-proposal.md`.
Use fresh backups and managed same-SHA PR110 reselection **before007** so both
units bind the new bootstrap. Apply only007 through the owning boundary, permit
only the seven named history-table privileges, then prepare the exact e84→85
receipt and managed selection. Never use fixture reset, blanket grant_writer,
certificate bypass, account/grant changes or collector operations.

After007, source rollback to e84 must retain this new five-file bridge controller,
all source-history rows and later human edits. The older four-file controller is
not a post007 fallback. Any destructive restore/downgrade needs new specific
permission and reconciliation; a private backup is not automatic permission.

Public CI uses only synthetic data and disposable PostgreSQL with exact historical
Git worktrees. Full private-workbook qualification is separate local evidence;
no workbook values, private config, accounts, snapshots or raw evidence dumps
are included in this package. Process cutover and visual UAT remain live gates.
