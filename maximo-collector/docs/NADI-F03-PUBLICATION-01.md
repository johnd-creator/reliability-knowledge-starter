# F03 recovery safeguards — stacked publication

This draft publishes the reviewed local patch from
[safe fixes review02](NADI-F03-FIX-REVIEW-02.md). The earlier reports describe
their local, unpublished checkpoints; publication changes that status only.
F03 operational acceptance remains **NO-GO**, and the identity/enrollment decisions
in those reports remain OPEN. No merge, auto-merge, deployment or activation.

## Base and reviewable scope

The dedicated branch starts from exact PR100 head
`952160cca72724e456b5a4e092301f5e475143e3`. Its PR base is
`codex/nadi-aud02b-b5-fix01-source-lock`, not main. This makes the PR diff show
the new safeguards, tests and supporting evidence rather than all unmerged
recovery foundations. It does not modify PR94–100 branches or metadata.

The prerequisite DAG is **95 → 96 → 97 → 98 → 99 → 100 → this fix**. PR94 is
independent discovery documentation. Those prerequisite implementations remain
unmerged; this fix cannot be integrated or operated independently of them.
Current main at publication preflight is
`35f3c101129241745e1795edd78a34c3617dccd7` after PR106. The prior isolated
combination with that main passed its local tests; it is not the ancestry of
this incremental PR. A future approved integration must preserve main's PR106
source-integrity/rehearsal changes and reconcile DEV-LOG. Retargeting to main
before dependencies are integrated would expose the cumulative stack diff.

## Changes

- B2/B3/B4 retain complete catalog hash computation and all existing fresh pins.
  Only the independently reviewed logical-restore hashes are accepted on exactly
  PostgreSQL16.14. Function, trigger, type, owner and ACL checks remain intact.
- WO references that would change case during reconstruction fail closed as
  FAILED/INVALID_MAPPING, retaining raw provenance and avoiding canonical writes.
  `a` and `A` remain distinct; whitespace-only uppercase references still work.
  Old incompatible resolved fingerprints require review without receipt rewrite.
- Four fixture controllers use identity-verified pidfd cleanup even if startup's
  wait reports timeout/nonzero, preserving original and cleanup errors separately.
- CI source selection additionally accepts only the exact pinned PR100 base
  branch/SHA in this same repository. Current-head/open/repository guards and
  final recheck remain. Arbitrary or moved stacked bases are refused.

No SQL migration, source grant, runtime configuration, scheduler or replay policy
is changed. There is no automatic alias resolution, terminal reset, budget increase
or next-generation enrollment. Existing source acquisition stays read-only.

## Verification and limits

The original local RED→GREEN evidence includes two independent PostgreSQL16.14
clusters, SQL and ORM restored replay DONE, actual B4 VERIFIED, and targeted
RECOVERY_BY_ID/PARTIAL without a fabricated full-population completion proof.
Real enum/predicate/index/trigger/ACL/owner drift and sealed-capture provenance
changes are refused. Tests for unknown/wrong observed server versions remain
fail-closed; those negatives do not alter server configuration.

Final publication checks run against this actual PR100-based branch. Counts may
differ from the main-integrated checkpoint because PR106 and other later main
changes are deliberately absent from its diff/ancestry. Exact tested source hashes,
commands and results are recorded locally; the draft PR description identifies
the final commit, executed counts and remote exact-head run links.

The PostgreSQL16.14-only full restore rehearsal is an explicit synthetic command,
not an operational restore or a silently skipped CI lane. Standard remote CI
continues its fresh-install transaction, coverage, source-lock, unit and contract
checks. PostgreSQL versions other than the qualified restore profile remain
unqualified; local qualification is reported separately from hosted CI.

Portable manual reproduction (from a reviewed checkout with component test
dependencies installed and a trusted PostgreSQL16.14 tool directory):

```bash
python .github/scripts/qualification_ci/f03_restore_rehearsal.py \
  --source "$PWD" --sha "$(git rev-parse HEAD)" \
  --pg-bindir /usr/lib/postgresql/16/bin \
  --report /tmp/f03-restore-report.json
```

This command accepts no DSN. It creates two private Unix-only clusters and checks
their on-disk/server identities, restores only synthetic content into its own new
target, then stops only verified owned processes. It requires the tools and server
to be exactly16.14. Use a new report filename; retained archives/logs contain only
synthetic fixtures. Direct/module/SQLAlchemy connections share an endpoint guard;
async connections and unapproved libpq options are refused. The sibling coverage
worker independently verifies the private cluster before its SELECT-only reader.

Publication authorization does not settle case-sensitive source keys versus
verified aliases/collision/provenance, or explicit successor episodes after DONE
with lifetime/per-generation budgets and B4 interpretation. BLOCKED has no new
unblock policy. Operational backup/PITR/RPO/RTO, legacy-writer exclusion, expiry
disposition and owner/engineer acceptance remain separate gates.
