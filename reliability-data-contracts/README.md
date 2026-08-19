# Reliability Data Contracts

Vendor-neutral semantic contracts used by reliability applications.

The purpose is to prevent application code from becoming tightly coupled to
Maximo or PI. Application domain models consume these contracts; vendor-specific
field names live only in the `sources.maximo` / `sources.pi` blocks.

## Source of truth

Field mappings are verified against `maximo-knowledge` (site BSR, org IP) and
`pi-knowledge` (site BSR, unit BSR1). See
[`mappings/maximo-to-contracts.md`](./mappings/maximo-to-contracts.md) and
[`mappings/pi-to-contracts.md`](./mappings/pi-to-contracts.md) for the
field-by-field translation tables.

## Schemas

### Verified against Maximo (site BSR)
| Schema | Maximo source | Status |
|---|---|---|
| [`equipment.schema.json`](./schemas/equipment.schema.json) | MXASSET (69 fields) | ✅ verified |
| [`work-order.schema.json`](./schemas/work-order.schema.json) | MXWODETAIL (166 fields) | ✅ verified |
| [`service-request.schema.json`](./schemas/service-request.schema.json) | MXAPISR (96 fields) | ✅ verified |
| [`person.schema.json`](./schemas/person.schema.json) | MXPERSON (34 fields) | ✅ verified |
| [`item.schema.json`](./schemas/item.schema.json) | MXITEM (40 fields) | ✅ verified |
| [`labor.schema.json`](./schemas/labor.schema.json) | MXAPILABOR (14 fields) | ✅ verified |

### Vendor-neutral source
| Schema | Source | Status |
|---|---|---|
| [`condition-parameter.schema.json`](./schemas/condition-parameter.schema.json) | pi-knowledge registry YAML via pi-collector | ✅ verified (v2, breaking rename 2026-08) |
| [`condition-reading.schema.json`](./schemas/condition-reading.schema.json) | PI Web API streams via pi-collector | ✅ verified (snapshot + timeseries) |

### Computed reliability concepts (derived, not a direct source field)
| Schema | Derived from |
|---|---|
| [`failure.schema.json`](./schemas/failure.schema.json) | work_order.failure_code (MXFAILURECODE ⛔ forbidden) |
| [`downtime.schema.json`](./schemas/downtime.schema.json) | work_order.downtime / equipment.downtime_total |
| [`location.schema.json`](./schemas/location.schema.json) | location_id on Equipment/WO/SR (MXAPILOCATION ⛔ forbidden) |
| [`maintenance-event.schema.json`](./schemas/maintenance-event.schema.json) | work_order actuals — actstart/actfinish/actlabhrs (MXWODETAIL) |
| [`reliability-kpi.schema.json`](./schemas/reliability-kpi.schema.json) | MTBF, MTTR, availability, PM compliance |

## Catalog examples

- [`catalog/equipment.example.yaml`](./catalog/equipment.example.yaml)
- [`catalog/work-order.example.yaml`](./catalog/work-order.example.yaml)
- [`catalog/condition-parameter.example.yaml`](./catalog/condition-parameter.example.yaml)

## Core concepts

Equipment · Location · WorkOrder · MaintenanceEvent · Failure ·
ConditionParameter · Alarm · Downtime · ReliabilityKPI

## Rules (see AGENTS.md)

1. Do not copy vendor-specific payloads into core contract fields.
2. Preserve source-system identifiers under `sources`.
3. Prefer stable organization-owned IDs where available.
4. Document units explicitly. Use ISO-8601 timestamps.
5. Mark nullable/unknown fields intentionally.
6. Breaking schema changes require a version bump.
