# Evidence-preserving rollback and proposed integration sequence

## Synthetic backup/restore result

The B5 controller alone creates a private Unix-only cluster, verifies its on-disk
system identifier/data directory and fixed databases, and later stops only that
cluster. The backup helper dumps three synthetic checkpoint schemas (partial,
targeted and final) with schema/data; file is private0600 in private0700 storage.
It validates archive TOC/readability and restores with error-stop/single-transaction
into **a separate `nadi_b5_restored` database in that same disposable cluster**.
No active database is overwritten. SHA256 and row counts/hashes for every restored
table are compared against the source (84 tables,143 synthetic rows in the local
scenario). This includes source cursors, manifests, receipts, obligations,
supersession, audit events, queue claims and domain fences.

The dump intentionally excludes other experiment schemas and global roles. It is
not a full operational backup, role restore or persistent QA/session acceptance.
No operational credential is used. Original private logs, failed runs, archives and
comparison manifests are retained outside Git. The final CI records archive hash,
size, fixture identity and cleanup; large/generated/private evidence is not committed.

## Future operator-run application rollback (NOT EXECUTED)

1. Obtain explicit rollout/rollback authority, exact release/checksum manifest,
   owning DB/co-location proof and least-privilege identity review.
2. Inventory every actual canonical writer, including legacy projector, bootstrap,
   controlled loader and ignored/deployment scripts. Establish approved exclusive
   ownership/shared fencing before candidate writes; B5 does not stop them.
3. Capture validated complete backups of owning source/Mart/candidate store,
   required globals/role definitions, deployment config and independent application
   stores/sessions. Verify privacy, checksum, storage capacity, recovery objectives
   and restore to separate infrastructure before operational acceptance.
4. For application rollback, explicitly cease only the candidate under approved
   controls, preserving queue/run/fence ownership evidence. Select reviewed disabled
   application version. Candidate reader downgrade must return UNKNOWN/non-CURRENT
   when evidence is unavailable; do not reinterpret legacy SUCCEEDED as coverage.
5. Retain candidate tables and all capture/debt/receipt/audit history. Never run down
   scripts, DROP/TRUNCATE evidence or reset source cursors to enable a downgrade.
   Do not start an incompatible legacy writer merely because UI/application rolled back.
6. Database restore is a separate disaster-recovery decision, with independent
   approval and reconciliation of changes since backup. Restore elsewhere first;
   never overwrite the active store simply to demonstrate rollback.
7. Verify exact source release, source/target checksums, unresolved debt, queue claims,
   audit continuity, source cursors, auth/session boundaries and operational service
   state. Keep claims unresolved if identity or ownership cannot be proven.

No executable operational command/DSN is embedded here. The test controller cannot
select an operational DB; it accepts no input DSN. An operator runbook must fill
owner-specific identities and approvals, not substitute fixture names.

## Git ancestry and actual repository settings

Pinned ancestry is linear: main → B1 commits776ff8d/ce6a29a → B2 86d760c → B3
6859bfc/662ce7b → B4 bee49a3 → new B5 qualification. No commits are cherry-picked,
squashed, rebased or rewritten here. Each slice's accepted SHA and report remain
traceable. B5 PR lists incremental B4→B5 and cumulative main→B5 inventories.

Read-only GitHub settings query: merge commits, squash and rebase methods enabled.
The main branch-protection endpoint returned404 "Branch not protected". This is not
permission to merge without gates. The repository ruleset list was empty; recheck protection/rulesets immediately
before any authorized merge.
CI policy requires same-repository open PR targeting main, direct exact source SHA,
pinned workflow tools and a final fresh-runner HEAD check.

| Proposed approach | Benefits | Risks / required gates |
| --- | --- | --- |
| Sequential PR95→96→97→98→B5, non-squash merge commits | Preserves original source commits and each accepted slice | Five main transitions; recheck each remaining diff/base/HEAD and rerun impacted/post-merge CI after each. Never assume an earlier green run qualifies a changed merge base. |
| Controlled integrated promotion branch from exact B5 | One reviewed cumulative tree, one main transition, retains all original source ancestry | Senior Review must accept every slice and unresolved findings first; verify no unrelated commits and exact tree, qualify promotion PR and post-merge main. |

Recommendation: after technical blockers are remediated and requalified, use one
separately authorized integrated promotion candidate from the reviewed B5 lineage
(the B5 PR can serve as that review surface). A single non-squash merge preserves
slice SHAs and reduces intermediate main states. Do not create/merge that promotion
now. Do not automatically close the dependency PRs; any superseded closure follows
explicit authorization and verified post-merge tree/ancestry.

## Proposed exact-head gate sequence (requires separate authority)

- Re-read main and all dependent heads; STOP on unexpected change. Verify approved
  findings disposition, CI/source/workflow SHAs and migration checksums unchanged.
- Verify cumulative commit set, ancestry, feature DISABLED and zero unrelated changes.
  Check branch/ruleset policy and repository merge method at execution time.
- Qualify direct exact source on all required lanes; for PR merge-commit regression
  verify tree identity explicitly. No equivalence inference from SHA alone.
- Execute only the specifically authorized PR merge with expected-head protection,
  using a non-force merge commit. Never merge unrelated draft or frozen PRs.
- Read back merge response/new main and verify all accepted source commits remain
  ancestors, tree matches intended result and migration files retain exact bytes.
- Require full post-merge main qualification. Failure: STOP/report; no automatic
  deploy, revert, retry or operational action.
- Merge is not activation. Existing laptop/frontend/collector/DB state remains
  unchanged until a separate approved rollout/rollback preparation task.

## Operational readiness checklist — all unresolved gates stay NO-GO

Owning DB/co-location and deployed schema; full backup/restore acceptance; migration
and grant authority; source-lock role design; legacy writer exclusion/shared fencing;
historical UNKNOWN/unlinked debt treatment; source absence/poison/stale-claim policy;
resource and retention approval; Phase1 acceptance/expiry disposition; AUD11 endorsement;
trusted-actor review for any future detailed endpoint; exact rollout and rollback
approval. No synthetic test closes these operational prerequisites or Astra F-03.
