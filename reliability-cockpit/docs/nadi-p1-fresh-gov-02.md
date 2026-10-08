# NADI-P1-FRESH-GOV-02 — owner approval and release preparation

**PASS — owner decision recorded; component endorsements pending; activation not authorized.**
Phase 1 remains CURRENT/PARTIAL. This checkpoint updates existing PR #27.

## Authoritative decision and provenance

Fauzi, project owner, approved provisional monitoring thresholds on **8 October
2026**: MAXIMO_WO=660s; MART_FACTUAL=660s; PI_COLLECTOR=1800s; CONDITION_SOURCE
and CONDITION_PROJECTION stay UNSET. Evidence is the human-supplied GOV-02 task,
section 1, explicitly stating that this conversational owner decision was already
received. It is recorded as **PROJECT_OWNER_APPROVED**, without a digital signature,
externally authenticated approval or a new request for the same owner decision.

Scope is operational monitoring only. No long-term SLA, health scoring, automatic
maintenance action, acquisition, change to condition-acquisition governance or
runtime activation is authorized. The historical GOV-01 PENDING matrix is retained
as evidence of the earlier proposal, rather than rewritten as approved at that time.

The [approval register](nadi-p1-fresh-gov-02-approval-register.json) separates:
PROPOSED → PROJECT_OWNER_APPROVED; component-specific
COMPONENT_ENDORSEMENT_PENDING; **ACTIVATION_NOT_AUTHORIZED**;
future EXPIRED / RENEWAL_REQUIRED. Those last states are conditional future states,
not claims that today's approval has expired or renewal was received.

## Approval time and expiry precision

The supplied evidence specifies a date only. `approval_timestamp` and timezone are
NULL; precision is DATE_ONLY. Calendar reference **15 October 2026** is calculated
as 8 October + 7 days. `expires_at` remains NULL because an exact expiry instant cannot
be derived without inventing approval time/timezone.

Before activation, resolve an evidence-backed approval timestamp/timezone or obtain
owner clarification of the effective expiry instant. This is a precision
clarification, **not another request to approve the same thresholds**. Until
resolved, the activation gate is closed. Do not use task receipt time, Git commit
time, current clock, signal approval timestamp, or later activation time as the
freshness approval time. Expiry is seven days from approval, not seven days from
activation; activation must occur while approval is still valid. Explicit renewal
is required to extend it. No expiry timer is installed by this task.

## Current approval matrix

| Component | Owner-approved value / scope | Owner decision | Technical reviewer / component endorsement | Activation / 24h / 72h | Expiry / rollback |
|---|---|---|---|---|---|
| MAXIMO_WO |660s, successful WO polling only; asset source freshness excluded |Fauzi /2026-10-08 /PROJECT_OWNER_APPROVED |Named Maximo Operations Owner unknown; COMPONENT_ENDORSEMENT_PENDING |NULL /NULL /NULL; endorsement, expiry and separate authorization required |15Oct calendar reference; exact instant NULL; Fauzi proposed rollback operator, assignment pending |
| MART_FACTUAL |660s, BOTH factual projector successes; source freshness independent |Fauzi /2026-10-08 /PROJECT_OWNER_APPROVED |Named Mart/Platform Owner unknown; COMPONENT_ENDORSEMENT_PENDING |NULL /NULL /NULL; same gate |Same expiry and rollback rule |
| PI_COLLECTOR |1800s, full-success technical collection only; partial/error cycles retain previous success |Fauzi /2026-10-08 /PROJECT_OWNER_APPROVED |Named PI Historian/Collector Owner unknown; COMPONENT_ENDORSEMENT_PENDING |NULL /NULL /NULL; same gate |Same expiry and rollback rule |
| CONDITION_SOURCE |UNSET; numeric engineering policy still DEFERRED |Fauzi /2026-10-08 /PROJECT_OWNER_APPROVED_KEEP_UNSET |No endorsement claimed; no numeric activation proposed |NULL /NULL /NULL; preserve UNSET |Any future numeric proposal requires its own evidence/approval |
| CONDITION_PROJECTION |UNSET; numeric engineering policy still DEFERRED |Fauzi /2026-10-08 /PROJECT_OWNER_APPROVED_KEEP_UNSET |No endorsement claimed; no numeric activation proposed |NULL /NULL /NULL; preserve UNSET |Any future numeric proposal requires its own evidence/approval |

Register stores actual activation and review due dates as NULL. After an authorized
activation, record its exact timestamp; compute 24h/72h review due dates from that
timestamp. Those are independent from approval expiry. If expiry arrives first,
rollback/renewal takes precedence; never extend validity to finish a review.

### Reliable reviewer identity evidence

Scoped local documents identify Fauzi as accountable project operator and Hidayat
as System Owner Boiler / Senior Engineer for equipment identity review. They do
not establish named owners of Maximo Operations, Reliability Mart/Platform or PI
Historian/Collector, nor freshness endorsement by any of those owners. Their
register identities and endorsement timestamps remain NULL. Hidayat's mapping
review and Fauzi's signal-use approval are not component freshness endorsements.
No endorsement requests were sent to anyone by tools.

## Prepared technical endorsement requests — not sent

### Maximo Operations Owner

Please give ENDORSE / REVISE / DECLINE for 660 seconds of WO polling activity
monitoring. Confirm scope excludes general Maximo asset source freshness; observed
failure gaps can correctly produce STALE; acquisition errors remain independently
degraded; no workload or scheduling change is needed. Record accountable name,
role, decision date/timezone, evidence reference and any scope qualification.

### Reliability Mart / Platform Owner

Please give ENDORSE / REVISE / DECLINE for 660 seconds of successful factual
projection activity. Confirm BOTH `asset_master` and `maintenance_event` require
valid success timestamps; either missing/stale/error state cannot PASS. Recent
projection does not make outdated source records current. Confirm the preserved
error behavior and rollback of only the three component keys are acceptable.
Record name, role, date/timezone, evidence reference and qualifications.

### PI Historian / Collector Owner

Please give ENDORSE / REVISE / DECLINE for 1800 seconds of full-success technical
collection monitoring. Confirm partial/failed cycles retain prior successful time;
bad-quality and epoch timestamp anomalies remain visible independently; enabling
monitoring needs no extra PI Server acquisition or schedule change. Record name,
role, date/timezone, evidence reference and qualifications. This does not approve
condition-source or projection freshness policies.

## PR reconciliation and validation

Fetched PR #27 is OPEN; reviewed HEAD
`916a3d9c8cd852bc9ee0a09a93f87f89a2687090`, base/main
`1cf7fed971594581913e8e7f635691f834133b6e`. Its original seven-file diff is limited
to documentation, aggregate fixtures and offline simulation. This continuation
adds approval documentation/register, a source-free validation artifact and the
GOV-03 handoff; no application, Compose, migration or workflow changes.
The original 14-case simulator/input/results remain intact and are reproduced.
Only names, roles, public policy decisions and evidence references are introduced;
no secret, operational private payload or private configuration value is copied.

GitHub reports no check runs and no submitted PR reviews at the inspected HEAD.
The reviewed tree contains no`.github` files; absence of reported checks is not
proof that branch protection is absent. The update remains OPEN/UNMERGED for
review of its new scope. No merge, bypass, deployment or policy activation occurs.
Repository checks/review requirements must be re-evaluated at the final immutable
HEAD before any permitted merge; merge is not a GOV-03 authorization.

Source-free evidence:14decision cases reproduce; targeted component, governance,
readiness and integration suites reproduce45PASS/9isolated-PostgreSQL skips.
Approval-register validation asserts five exact owner decisions, date-only expiry
precision, three pending component endorsements, NULL activation/review clocks,
legacy/condition UNSET scope and unchanged original 14-case artifacts.
`git diff --check` passes. No product defect requires repair or deployment.

## Prepared GOV-03 and acceptance limits

[Controlled activation handoff](nadi-p1-fresh-gov-03-handoff.md) is prepared only.
It requires recorded component endorsements, exact expiry resolution, explicit
activation authorization, pinned reviewed merged source and accountable rollback
assignment. It details offline parser/Compose preflight, local smoke tests,
24h/72h reviews, expiry/renewal and rollback. It installs no automation.

Actual readiness remains 5 PASS / 4 UNKNOWN; the frozen hypothetical three-policy
simulation is 8 PASS / 1 UNKNOWN, overall UNKNOWN. Condition readiness is not promoted
by owner approval or Good quality. Phase 1 final acceptance is NOT COMPLETE.
R3's 54.84218978881836 Ton/h evidence and source/collection/projection timestamps,
NULL collector success, original artifacts/journals remain unchanged. No replay.
Other assets remain unverified; BFPT remains REJECTED/FROZEN/DO NOT VERIFY and
PI_AF_KKS_LOOKUP_UNRESOLVED remains open.

Task-attributable source GETs0; production policy/credential changes0; acquisition,
Mart evidence writes, mapping/signal/operational approval mutations0; DDL/reset/
truncate/history0; deployment/restarts0; registry/scheduler/CEMS/NK changes0.
All eight runtime settings stay UNSET. Normal background collectors remain separate.

## Executed GOV-02 validation and preservation

From `reliability-cockpit`, exact released Python executable:
`/home/john-d/.codex/worktrees/nadi-pi-diagnostics-release/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python`.

```bash
python docs/validation/nadi-p1-fresh-gov-02-validation.py
python docs/validation/nadi-p1-fresh-gov-01-simulation.py
# Generated simulation JSON equals the original committed results byte-for-byte.
PYTHONPATH=tests:/tmp/nadi-phase1-host-testdeps \
DATABASE_URL=sqlite+pysqlite:///:memory: COCKPIT_CONFIG_MODE=managed \
python -m unittest test_component_freshness test_freshness_governance \
  test_phase1_readiness test_integration_status
# 54 discovered: 45 PASS / 9 optional isolated PostgreSQL SKIP.
```

Final read-only preservation: full R3 latest/state and mapping/selection unchanged;
34 historical artifacts retain exact bytes and mtimes; all 23 container IDs,
images, start times and restart counts match GOV-01. Private configuration
metadata unchanged; file and API runtime policies all UNSET; reader SELECT-only;
reviewed release clean, original workspace/untracked file preserved. Actual
require-pass exit2/UNKNOWN, five PASS and four UNKNOWN gates. No acquisition,
replay, production policy mutation, service replacement or source request.
