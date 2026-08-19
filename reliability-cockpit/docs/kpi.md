# Reliability KPI Computation

KPIs are computed by the cockpit from normalized data — they are NOT direct
Maximo fields. Formulas use explicit units (vendor-neutral).

| Metric | Formula | Unit | Inputs |
|---|---|---|---|
| MTBF | operating_hours / failures | hours | failure_count, total_operating_hours |
| MTTR | downtime_hours / failures | hours | failure_count, total_downtime_hours |
| AVAILABILITY | (total - downtime) / total × 100 | percent | total_operating_hours, total_downtime_hours |
| PM_COMPLIANCE | completed / scheduled × 100 | percent | pm_scheduled, pm_completed |

When `failures == 0`, MTBF/MTTR value is `null` (not zero) — a null indicates
"no failures observed in the window" rather than an absence of data.

Availability over a period uses operating hours + downtime hours as the
denominator. Period windows are explicit (`period_start`, `period_end`).

## Data gaps

- Failure count currently comes from work-order failure data
  (`work_order.failure_code`); the Maximo FAILURECODE master is still
  read-forbidden. Until it is verified, MTBF/MTTR reflect reported CM work
  orders with failure codes only.
- No downtime-report object yet; downtime is taken from
  `work_order.downtime_hours` / `equipment.downtime_total_hours`.
- `PM_COMPLIANCE` requires `worktype=PM` work orders; scheduled/planned counts
  depend on the PM object (currently forbidden) as an improvement.