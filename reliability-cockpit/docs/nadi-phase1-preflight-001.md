# NADI-PHASE1-PREFLIGHT-001 — read-only candidate product gate

`cockpit phase1-readiness` produces JSON from local collector observations and the
explicit SELECT-only Mart reader. It never migrates, imports/verifies mappings,
approves signals, triggers source requests or restarts services. There is no
legacy/admin DSN fallback. Missing observations remain UNKNOWN.

`--require-pass` returns exit 2 unless all nine gates PASS; default exit 0 means
successful report generation, **not** product acceptance. Observation/validation
failure emits a safe UNKNOWN reason and exit 2 without exception secrets.

`--status-file <file>` evaluates a bounded canonical IntegrationStatus audit
snapshot without network/DB access and labels output `OPERATOR_DOCUMENT`. Such
an offline result is not a live runtime acceptance attestation.

| Gate | Evidence |
|---|---|
| P1-MAXIMO-CURRENT | Complete successful WO collector activity + cursor + collection policy |
| P1-MART-CURRENT | Both factual projector successes + explicit projection age policy |
| P1-PI-COLLECTOR-CURRENT | Completed successful snapshot run + collection policy; independent of source timestamp |
| P1-MART-GOVERNANCE-READY | Actual reader can query canonical governance shape |
| P1-CONDITION-SCHEMA-READY | Actual reader can query all three condition relations |
| P1-IDENTITY-MAPPING-READY | At least one uniquely usable VERIFIED pilot Asset; any ambiguity blocks |
| P1-SIGNAL-SELECTION-READY | Explicit approved selection for at least one usable pilot mapping |
| P1-CONDITION-PROJECTION-READY | Complete approved cohort, current source and projection policy, accepted quality, no degraded attempt |
| P1-INTEGRATION-STATUS-READY | Canonical five-component status contract is available, including honest blocked states |

Pilot readiness does not require mapping all registered Assets. Coverage remains
visible; no mapping is automatically created to satisfy a denominator. Schema
query compatibility is not migration checksum/constraint certification: the
existing controlled writer migration preflight remains required before deployment.

Real-like zero mappings: identity and downstream gates are BLOCKED with
`HUMAN_CROSSWALK_REQUIRED`. Missing condition migration is a separate runtime
blocker. Blank policy means UNKNOWN, never a fabricated production SLA. Synthetic
fully configured VERIFIED/approved/projected/current fixture reaches PASS.
Phase 1 remains CURRENT / PARTIAL until real runtime and human acceptance.
