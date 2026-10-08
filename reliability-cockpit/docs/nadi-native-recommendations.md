# NADI-native recommendation foundation

Candidate implementation only. Operational routers are unmounted. A recommendation is a human proposal, never a Maximo WO or approval to perform maintenance.

## Governed local path

Trusted server principal → exact registered asset → authorized existing Engineering Case → locally resolved canonical evidence and optional existing WO → NADI application record. The catalog builds reference provenance server-side; clients cannot submit frozen factual payloads. A controlled directory must validate PIC and team scope. No source client or source credential is used.

DRAFT → IN_REVIEW → APPROVED / REJECTED. Creator, contributors and responsible PIC cannot review their own proposal. Rejected records may be revised; approved records can be reopened while local follow-up remains PROPOSED. Once follow-up starts, a new proposal is required rather than silently changing approved intent.

APPROVED means reviewed NADI record. It does not authorize maintenance execution. Local follow-up is PROPOSED → PLANNED → IN_PROGRESS → COMPLETED, or CANCELLED from a non-terminal state, with explicit reasons and immutable application revisions. These statuses do not update any source record. WO status displayed in a frozen reference remains a timestamped source fact, not a synchronized action command.

Every command uses expected revision and actor-scoped request identity. Record changes, history and replay receipt commit atomically. Replays preserve the original result and timestamps. Conflicts fail rather than overwrite. Canonical Mart access remains SELECT-only; writes use the separate application store guarded against Mart schema anchors.

## Activation and engineer questions

Enterprise identity, approved team/PIC directory, application provisioning/migration review, retention and UX validation remain prerequisites. Confirm priority semantics, follow-up responsibility, target-date meaning, and how existing WO links are reviewed. This bundle invents no maintenance thresholds, recommendations, Maximo endpoints or live collection.

Candidate application migration 004 is additive to the existing application DB, independent of the similarly numbered Mart migration. Rollback disables candidate APIs and revokes writer/session access; preserve record and audit tables. No live migration is executed.

The candidate `engineering-recommendation.schema.json` is distinct from the existing generic `recommendation.schema.json`; the existing contract is preserved unchanged.
