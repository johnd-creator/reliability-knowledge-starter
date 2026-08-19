# PI Discovery Hierarchy (verified)

Verified AF (Asset Framework) hierarchy on asset server **PIAF**,
database **Indonesia Power Corporate**, via read-only PI Web API probes
(2026-08-14). Scope: **BSR → BSR1 only**.

```text
PI Web API root (/)
├── DataServers                          [verified: PI1, pi2]
│   └── Points                           [verified: Units=null at this level]
│       └── Streams                      [verified: value/recorded/interpolated/summary]
└── AssetServers
    └── PIAF                             [verified]
        └── AssetDatabases
            ├── Indonesia Power Corporate  [primary reliability DB]
            ├── Pump CBM                   [condition-based monitoring]
            └── (12 others — not in scope)
                └── Elements (top level = generating unit/site codes)
                    ├── BSR  ← matches Maximo site_id BSR
                    │   └── BSR1                          [4 systems]
                    │       ├── Boiler System
                    │       │   ├── BSR1.Pulverizer       [98 attrs]
                    │       │   ├── BSR1.Coal Feeder       [73 attrs]
                    │       │   ├── Boiler Temp            [187 attrs]
                    │       │   └── BSR.FDF A/B, BSR1.FDF ... (boiler aux)
                    │       ├── Generator System
                    │       │   └── BSR1.Generator         [12 attrs, 7 with units]
                    │       ├── NPHR                       [100 attrs, calc/KPI]
                    │       └── Turbine System
                    │           ├── BSR1.Turbine           [48 attrs, bearings+vib+steam]
                    │           ├── BSR1.HP Turbine        [11 attrs, inlet/outlet steam]
                    │           ├── BSR1.IP Turbine        [11 attrs, inlet/outlet steam]
                    │           ├── BFPT                   [0 attrs]
                    │           └── BFPT1A                 [1 attr]
                    ├── ADP, BEU, BKT, BLB, BLI, BLT, BRU, BTG, ... (not in scope)
                    └── ... (20+ unit codes)
```

## Counts (BSR1 total: 541 attributes)

| System | Attrs | With units |
|---|---|---|
| Boiler System | 358 | ~50 |
| NPHR | 100 | ~10 |
| Turbine System | 71 | ~48 |
| Generator System | 12 | 7 |
| **Total** | **541** | **150** |

## Key finding: where units live

- **PI Point level** (`/dataservers/{id}/points`): `Units` is **null** for the
  points sampled. Point names are verbose and include GUID suffixes
  (e.g. `02 Generator.BLR DRUM LVL AVG.{guid}`).
- **AF Attribute level** (`/elements/{id}/attributes`): carries clean business
  names **and** units via `DefaultUnitsName` (e.g. `degree Celsius`,
  `Micrometer`, `Tonne per hour`, `kilopascal`).

> **Implication:** map reliability parameters from AF **attributes**, not from
> raw PI points. The attribute path encodes equipment + parameter + position
> and supplies the engineering unit. Raw points are only needed to resolve a
> WebId when no AF attribute covers the measurement.

For each discovered item, record both technical identity (WebId, path) and
business meaning (equipment, parameter, position, unit).
