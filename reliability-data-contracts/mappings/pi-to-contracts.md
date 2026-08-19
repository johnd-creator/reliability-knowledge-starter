# PI → Reliability Contracts Mapping

Field-by-field translation from the verified pi-knowledge registry
(`pi-knowledge/mappings/bsr1-parameters.yaml`, site BSR / unit BSR1) to
vendor-neutral contracts, as implemented by `pi-collector`. Mirror of
[`maximo-to-contracts.md`](./maximo-to-contracts.md).

Core contract fields are vendor-neutral (snake_case); PI identifiers live only
under `sources.pi`.

Status legend: ✅ verified via read-only `GET /streams/{webId}/value` ·
⊘ derived locally

---

## Registry intake (pi-knowledge YAML → pi-collector)

The loader consumes **only** entries with `status: verified` **and**
`stream_status: ok` (433 of 541 attributes; 98 gone, 10 error). Entries without
a `web_id` are skipped. Everything below assumes that filter.

YAML shape: header (`site`, `unit`, `status`, `verified_at`, …) →
`equipment.<name>.parameters.<key>[]` entries with `name`, `unit`, `position`,
`web_id`, `source_system`, `data_type`.

## ConditionParameter ← registry YAML

| Contract field | YAML / origin | Type | Notes |
|---|---|---|---|
| `attribute_id` | ⊘ slug of `site-unit-equipment-parameter-name[-position]` | string | lowercase, non-alphanumeric → `_`; ≤200 chars; natural key |
| `site` | header `site` | string | e.g. BSR |
| `unit` | header `unit` | string | plant unit e.g. BSR1 — **not** the engineering unit |
| `equipment` | `equipment` key | string | equipment group, e.g. `BSR1.Turbine` |
| `parameter` | `parameters` key | string | category, e.g. `bearing_temperature` |
| `business_name` | entry `name` | string | human-readable PI attribute name |
| `position` | entry `position` | string | measurement point, e.g. BFPT1A |
| `unit_of_measure` | entry `unit` | string | engineering unit abbreviation |
| `is_active` | ⊘ local | boolean | true on load; false after 410 Gone / upstream prune |
| `registered_at` | ⊘ local | datetime | last registry upsert |
| `sources.pi.web_id` | entry `web_id` | string | sole PI-read identifier; never hardcoded in app code |
| `sources.pi.af_path` | ⊘ `"site > unit > equipment > name"` | string | synthesized locally, not read from PI |

Not persisted by the collector (knowledge-level only): `source_system`,
`data_type`, `verified_at`, header verification summary.

## ConditionReading ← PI Web API stream values

Serves both the snapshot table (latest value per attribute) and the
TimescaleDB timeseries (snapshots + interpolated backfill + recorded history).

| Contract field | PI field / origin | Type | Notes |
|---|---|---|---|
| `attribute_id` | registry | string | FK to ConditionParameter |
| `timestamp` | `Timestamp` | datetime | event/measurement time; snapshot column `source_timestamp` maps here; idempotency key with `attribute_id` |
| `value` | `Value` | number\|null | **digital states / non-numeric → null** (never stored as text) |
| `value_good` | `Good` | boolean | string forms `"true"/"1"/"yes"` coerced |
| `units` | `UnitsAbbreviation` ⊘ fallback registry `unit` | string | snapshot only; historical points resolve units via the registry |
| `collected_at` | ⊘ local UTC now | datetime | collector write time |

## Standard query patterns (read-only)

```
GET /streams/{webId}/value            # snapshot
GET /streams/{webId}/interpolated     # backfill (start, end, interval)
GET /streams/{webId}/recorded         # raw archive (heavy; off-hours only)
GET /streamsets/{webIds joined}       # batched snapshots
```

Pagination: `Links.Next` is an absolute URL — strip the base URL before
re-requesting. Rate limit 1 req/s, response cap 1 MiB, GET/HEAD only.
