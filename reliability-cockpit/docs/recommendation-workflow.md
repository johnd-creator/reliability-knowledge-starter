# Reviewed NADI recommendation workflow — candidate

Drafts may reference accessible same-asset cases while an investigation is in progress.
Submission requires an APPROVED Engineering Case and at least one resolvable supporting
evidence reference. The server pins case revision, content digest, reviewer and decision
time. Review/follow-up recheck this pin and evidence versions; changed or reopened
case/evidence blocks further actions. Frozen history is never replaced implicitly.

Independent review produces an APPROVED proposal, not maintenance authorization.
Local follow-up progresses PROPOSED → PLANNED → IN_PROGRESS → COMPLETED (or CANCELLED).
COMPLETED is a human report, not verification. VERIFY_COMPLETION requires an independent
asset-scoped reviewer, reason and 1–20 distinct frozen evidence selections. It records
VERIFIED local follow-up, reviewer/time and snapshots. No Maximo source action exists.
Original source WO status and timestamps remain informational and immutable.

Application CAS, receipts and immutable revision events cover every transition.
Application JSON persistence needs no additional DDL for these additive fields. Legacy
records remain readable; absent reviewed-case pins block new approval/follow-up until
the record is deliberately revised and resubmitted. Public routes remain unmounted;
production identity, writer provisioning/migrations and operational UAT remain gates.

Closure verification confirms the NADI follow-up record only; evidence selection does
not itself prove physical maintenance completion or authorize a source WO closure.

## Local integrity fix candidate — 2026-10-20

NADI-ENGINEERING-INTEGRITY-FIX-01 is an uncommitted local candidate based on
main35f3c101, not runtime activation or engineer acceptance. Submission and review
take application locks in Case → sorted Inspection → Recommendation order.
Completion locks the union of supporting/completion Inspections before rechecks.
Case mutations take their Case row before any Inspection lock; CAS and receipts
remain atomic, with no blanket deadlock retry.

New ASSET/MAINTENANCE/WORK_ORDER/FMEA references use `mart-facts-v2:` content
versions. The digest binds canonical identity, allowlisted factual fields and
source provenance keys. Strings are hashed incrementally without adding business
length limits. Raw source payloads, personal fields and ingestion-only churn are
excluded. This digest is neither a signature nor source/engineering approval.
Old frozen histories remain readable and unchanged. An old factual pin differs
from the new version and blocks new actions with EVIDENCE_VERSION_CHANGED;
deliberate revision/reselection or a new proposal is required. Progressed legacy
records still require an explicit owner recovery decision, never an automatic
pin rewrite or data migration.

The UI requires an explicit Save before submitting edited Recommendation fields.
In-memory subject/revision-bound recovery survives focus and workspace navigation;
full reload cannot preserve unsaved private content. Identity/role/asset changes
or revocation clear caches and every pending command slot. Retry IDs are scoped
by subject, method and path so another record's command cannot erase a lost
acknowledgement receipt. Frozen CONDITION values, quality and freshness are shown
from the linked snapshot, and detail401 invalidates the private register.

See [local fix report](NADI-ENGINEERING-INTEGRITY-FIX-01.md) for verification and limits.
