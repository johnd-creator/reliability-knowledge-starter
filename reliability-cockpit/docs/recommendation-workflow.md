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
