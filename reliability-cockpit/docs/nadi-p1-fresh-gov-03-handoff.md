# NADI-P1-FRESH-GOV-03 — controlled activation handoff (NOT EXECUTED)

## Entry gates — fail closed

1. Pin the merged reviewed commit containing GOV-02 approval documentation and
   component policy implementation; inspect clean release, effective Compose and
   accepted overrides. Verify no merge/deployment hook silently changed runtime.
2. Obtain recorded named endorsements for Maximo Operations, Mart/Platform and
   PI Historian/Collector, including scope, evidence and accountable decision dates.
3. Resolve exact approval expiry from evidence-backed approval timestamp/timezone
   or explicit owner expiry clarification. Confirm approval has not expired; if
   expired, require explicit renewal. Date-only15October is not an exact instant.
4. Obtain separate explicit GOV-03 activation authorization with accountable
   executor/rollback operator. Fauzi is the planned accountable operator; do not
   claim confirmed operational assignment before that authorization.
5. Record private accepted baseline: exact R3 payload/state, mapping VERIFIED1/
   PROPOSED0, selection/evidence/state1/1/1,433active PI attributes, WO cursor/floor,
   reader SELECT-only, container IDs and all eight freshness settings still UNSET.

A missing gate stops activation, while documentation preparation can complete.
There is no acquisition authority, automatic retry or timer in this handoff.

## Source-free dry-run — only after entry gates are proven

Offline parser validation may use a cleared, non-secret process environment:

```python
from unittest.mock import patch
from src.domain.condition_evidence import FreshnessPolicy
env = {
    "NADI_COLLECTOR_MAX_AGE_SECONDS": "",
    "NADI_SOURCE_MAX_AGE_SECONDS": "",
    "NADI_PROJECTION_MAX_AGE_SECONDS": "",
    "NADI_MAXIMO_WO_MAX_AGE_SECONDS": "660",
    "NADI_MART_FACTUAL_PROJECTION_MAX_AGE_SECONDS": "660",
    "NADI_PI_COLLECTOR_MAX_AGE_SECONDS": "1800",
    "NADI_CONDITION_SOURCE_MAX_AGE_SECONDS": "",
    "NADI_CONDITION_PROJECTION_MAX_AGE_SECONDS": "",
}
with patch.dict("os.environ", env, clear=True):
    policy = FreshnessPolicy.from_environment()
    assert policy.component_mode
    assert policy.condition_source_max_age_seconds is None
    assert policy.condition_projection_max_age_seconds is None
```

Run canonical 14-case offline simulation and policy/readiness targeted suites;
they are hypotheses, not activation. Mixing even equal legacy/component numeric
settings must reject. Validate effective Compose privately, emitting only policy
values and boolean credential-separation checks. Never print full Compose/env.
No live PI/Maximo/CEMS HTTP and no `condition refresh`/project/import commands.

## Authorized activation plan — not executed by GOV-02

Create a private permission-preserving backup of affected configuration. Update
only`NADI_MAXIMO_WO_MAX_AGE_SECONDS=660`,
`NADI_MART_FACTUAL_PROJECTION_MAX_AGE_SECONDS=660`,
`NADI_PI_COLLECTOR_MAX_AGE_SECONDS=1800` in authoritative private`.env.platform`.
Keep three legacy and both condition settings UNSET; preserve unrelated settings,
working source credentials and accepted overrides. Validate exclusive-component
parsing before replacement. Reload only cockpit-api if needed and separately
authorized; dependency graph must not recreate workers, DBs, volumes or networks.
No DDL, registry reload, history, new condition evidence or operational approval
record mutation. Keep exact source SHA, image identity, override list and pre/post
container IDs in private evidence without secrets.

Record exact actual activation time only after effective API settings are observed.
Compute review due dates as activation+24h/+72h; independently verify that approval
expiry still applies from approval+7days. Never extend approval from activation.

## Local operational smoke and reviews

Use stored-data APIs only: `/health`, factual overview, condition evidence and
platform/asset integration-status routes; inspect Data Trust and Coal Feeder UI.
Verify full R3 payload/state and timestamps unchanged, VERIFIED1/PROPOSED0,
signal/evidence/state1/1/1, reader SELECT-only,433active, WO cursor/floor retained.
Validate policy values in cockpit-api and no source credentials there. Inspect both
projector success timestamps independently. The current age/error evidence decides
acquisition PASS/PARTIAL/UNKNOWN; do not promise all three gates PASS just because
thresholds loaded. Condition source/projection stay UNKNOWN. Capture nine gates and
`phase1-readiness --require-pass`, which must remain nonzero while condition policy
is UNSET. UI quality does not imply equipment health.

At 24h and 72h from actual activation, read local ledgers/logs only. Review stale
episodes, failed/partial cycles, delay/false-alert trade-offs, both projector state
clocks, unknown/future times, bad-quality/epoch inventory and unchanged pilot.
Record reviewer identity, timestamp and outcome: CONTINUE / REVISE / ROLLBACK.
New threshold values require explicit review/approval; do not widen to hide outages.
Review dates remain NULL until activation; expiry takes precedence over review.

## Rollback

Stop on parser conflicts, implicit inheritance, hidden quality/coverage, future or
missing timestamps promoted CURRENT, unexpected service replacement, evidence/
governance mutation, regression or expiry without explicit renewal. Accountable
authorized operator returns only the three activated component keys to UNSET,
preserving unrelated private settings; reload only separately authorized cockpit-api
if required. Verify all eight policies UNSET, original pilot unchanged, reader SELECT-only,
workers preserved, freshness UNKNOWN and require-pass nonzero. Retain audit events.
No DB restore/reset/truncate, source retry, credential rotation or new acquisition.

No scheduler is installed to implement expiry. The accountable operator must
complete rollback or document explicit renewal by the approved expiry instant.
If that responsibility or exact deadline cannot be established, do not activate.

## GOV-02 state

Owner approval RECEIVED; three component endorsements PENDING; expiry-time precision
unresolved; activation authorization NOT RECEIVED. Actual activation/review clocks
NULL. GOV-03 NOT EXECUTED. Phase 1 CURRENT/PARTIAL; final acceptance NOT COMPLETE.
