# GOV03 — public migration-readiness summary

**INVENTORY PREPARED; MIGRATION NOT EXECUTED OR AUTHORIZED.** Complete infrastructure
inventory, accepted overlay order, host-specific configuration, storage identities,
image identities and recovery instructions remain in restricted ignored operational
evidence. They are intentionally excluded from this public engineering summary.

## Established engineering boundaries

Preserve existing collector-owned stores and the canonical Reliability Mart. The
legacy application store and canonical Mart reader path remain explicit and
separate, with no database fallback. Public NADI queries stay SELECT-only; controlled
administration/projector writers and source credentials remain separate. Never
create replacement operational databases or reset cursors, recovery floors,
registry, migration ledgers, governance history or accepted evidence to simplify
migration. Existing accepted Mart migrations 002/003/004 remain applied.

The reviewed application source is unchanged by GOV03. Detailed immutable image
identities, running-component inventory, dependency ordering and persistent storage
ownership are verified privately, rather than inferred from mutable tags or example
configuration. Future deployment must preserve accepted overlay semantics and
private configuration authority without publishing secrets or deployment topology.

## Required future acceptance

1. Establish accountable operator, target environment, access and cutover window
   under a separate reviewed deployment authorization.
2. Produce private validated database backups with consistency/version evidence;
   prove isolated restore, ownership, canonical schemas and reader grants. GOV03
   prepared a private configuration backup, not a new full database restore drill.
3. Preserve accepted pilot payload, lineage, source/collection/projection timestamps,
   VERIFIED=1/PROPOSED=0, approved signal/latest/state=1/1/1 and 433 active attributes.
4. Preserve technical acquisition ownership, request floors, post-cycle pause,
   WO cursor/recovery floor and both factual projector success paths. Ensure one
   active acquisition owner during cutover, rather than duplicate collectors.
5. Validate local APIs/UI/readiness and source-free launcher/budget/receipt contracts.
   Move private credentials/journals only through separately authorized secure
   channels with restricted access; no credentials in Git, reports or model prompts.
6. Independently approve bounded source connectivity checks from the future
   environment. No such check was performed by GOV03 or SEC01; historical live
   authorization cannot be reused. No discovery, history or recollection bootstrap.
7. Define recovery and fallback against the accepted environment before cutover.
   Do not shut down the current environment or remove storage under this task.
   If fallback cannot remain available, document an approved outage honestly.

Target access, connectivity, backup/restore acceptance and cutover approval remain
PENDING. No server migration, secret transfer or shutdown has occurred. Temporary
monitoring policies are not prerequisites for safe database migration and cannot
extend their own expiry through travel/cutover delays.

## Temporary monitoring handoff

Fauzi remains accountable for the manual checkpoint **12 October 2026 at 20:00 WIB**
and rollback before **13 October 2026 at 00:00 WIB** absent explicit extension.
There is no automatic expiry scheduler. The approved private procedure restores
only the three monitoring settings, preserving evidence and all unrelated runtime
configuration. Separate condition policies remain UNSET/UNKNOWN.

[Activation acceptance and dates](nadi-p1-fresh-gov-03.md) and
[approval register](nadi-p1-fresh-gov-03-activation-register.json) provide public
provenance. Phase 1 remains CURRENT/PARTIAL. This is a readiness handoff, not migration
execution permission or a claim that the future environment is already accepted.
