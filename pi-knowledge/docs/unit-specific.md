# Unit-Specific PI Knowledge (verified, site BSR / unit BSR1)

Verified against PI Web API `pivision.plnindonesiapower.co.id/piwebapi`
(read-only, 2026-08-14). Scope: **BSR site, BSR1 unit only** — all other unit
codes (ADP, BEU, BKT, ...) are out of scope.

## Site & unit naming

- Top-level AF elements under `Indonesia Power Corporate` are **generating
  unit/site codes**: `ADP`, `BSR`, `BEU`, `BKT`, `BLB`, `BLI`, `BLT`, `BRU`,
  `BTG`, `BTO`, `CLG`, `DRJ`, `EBT`, `GSL`, `HTC`, `JMB`, `JPR`, ... (20+).
- **`BSR`** is the site that matches Maximo `siteid=BSR` (org `IP`). Cross-ref
  equipment IDs against `maximo-knowledge` (site BSR).
- Under a site, the unit is suffixed with `1` (e.g. `BSR` → `BSR1`).
- Under the unit, four systems exist: **Boiler System**, **Generator System**,
  **NPHR** (net plant heat rate), **Turbine System**.

## Equipment inventory (BSR1, verified)

| AF element path | System | Attrs (with units) | Reliability meaning |
|---|---|---|---|
| BSR1.Turbine | Turbine System | 48 (42) | main turbine — bearings, vibration, steam |
| BSR1.HP Turbine | Turbine System | 11 (8) | HP turbine inlet/outlet steam |
| BSR1.IP Turbine | Turbine System | 11 (8) | IP turbine inlet/outlet steam |
| BSR1.Generator | Generator System | 12 (7) | generator excitation, H2, rotor |
| BSR1.Pulverizer | Boiler System | 98 (~30) | coal pulverizer temps (A–G) |
| BSR1.Coal Feeder | Boiler System | 73 (~8) | coal feeder A–G flow |
| Boiler Temp | Boiler System | 187 (~20) | boiler tube/furnace temperatures |
| NPHR | NPHR | 100 (~10) | calculated KPIs (heat rate, efficiency) |
| BFPT / BFPT1A | Turbine System | 1 (0) | boiler feed pump turbine (stale) |

## Dead references (verified 2026-08-14)

Full stream verification of all 541 attributes (`discovery/stream-verification.json`,
method: GET /streams/{webId}/value each): **433 ok, 98 gone (410), 10 error**.
The registry now retains all 541 attributes: **150 semantically reviewed** and
391 `unclassified`. Within the reviewed 150 parameters: **93 ok, 57 broken**.

Broken categories (AF attribute exists, backing PI Point deleted from PI1):

| Equipment | Broken | What |
|---|---|---|
| BSR1.Pulverizer | 43 | Gearbox/Motor bearing temps, Motor Power, Running Hour, PA damper (A–G) |
| BSR1.Turbine | 12 | Vib predictions 2X/3X, calc points (Boiler Eff, Heat Rate, Isentropis), IP Turbine steam, RH/SH Spray Flow (formula attrs) |
| BSR1.Generator | 2 | `Field Current`/`Field Voltage` — superseded by working `Excitation Field Current/Voltage` |

Equivalent live points under the new naming: `BSR1.Pulverizer A.Motor Current`,
`BSR1.Pulverizer A.Outlet Temperature`, `BSR1.Pulverizer A.PA Flow`,
`BSR1.Generator.Excitation Field Current`, etc. Data server `pi2` is
disconnected (HTTP 502) — no BSR1 points there.

## Verified parameter categories + units

| Category | Typical AF attribute | Unit | Equipment |
|---|---|---|---|
| Bearing temperature | `Bearing N Left/Right Temperature` | `degree Celsius` | BSR1.Turbine |
| Bearing vibration | `Bearing NX Vibration` | `Micrometer` | BSR1.Turbine |
| Vibration prediction | `Bearing NX Vibration Prediction` | `Micrometer` | BSR1.Turbine |
| Axial displacement | `Axial Displacement 1/2` | (none) | BSR1.Turbine |
| Speed | `Speed` | `revolution per minute` | BSR1.Turbine |
| Power output | `Generator Net Capacity` | `megawatt` | BSR1.Turbine |
| Steam temperature | `Inlet/Outlet Steam Temperature` | `degree Celsius` | BSR1.Turbine, HP, IP |
| Steam pressure | `Inlet/Outlet Steam Pressure`, `MAIN STEAM HEAD PRE` | `kilopascal` | BSR1.Turbine, Boiler |
| Steam flow | `Inlet Steam Flow`, `MAIN STEAM FLOW` | `Tonne per hour` | BSR1.Turbine, Boiler |
| Coal flow | `Total Coal Flow`, `Coal Flow` | `Tonne per hour` | BSR1.Coal Feeder |
| Pulverizer temp | `PULV X OTL TEMP N` | (none at point) | BSR1.Pulverizer |
| Feedwater pressure | `Final Feedwater Pressure` | `kilopascal` | BSR1.Turbine |
| Excitation current | `Field Current`, `Excitation Field Current` | `ampere` | BSR1.Generator |
| Excitation voltage | `Field Voltage`, `Excitation Field Voltage` | `volt` | BSR1.Generator |
| Hydrogen temperature | `H2 Inlet Temperature` | `degree Celsius` | BSR1.Generator |
| Hydrogen purity | `H2 Purity` | `percent` | BSR1.Generator |
| Rotor temperature | `Rotor Temperature` | `degree Celsius` | BSR1.Generator |
| Heat rate | `Nett Plant Heat Rate`, `Turbine Heat Rate` | `kcal/kWh` | BSR1.Turbine |
| Efficiency | `Boiler Efficiency`, `Turbine Eff Isentropis` | `percent` | BSR1.Turbine |

## Live snapshot sample (2026-08-14)

| Parameter | Value | Unit |
|---|---|---|
| Generator Net Capacity | 498.54 | MW |
| Speed | 3002.95 | rpm |
| Bearing 1X Vibration | 51.49 | µm |
| Bearing 2X Vibration | 62.55 | µm |
| Axial Displacement 1 | 0.29 | — |
| Main Steam Flow | 1690.95 | t/h |
| Main Steam Head Pre1 | 14.14 | kPa |

## Raw PI point naming (PI1 data server)

Raw points use prefixes like `ADP1.`, `ADP.` and descriptive names, e.g.:
- `ADP1.BEARING #1 OIL TEMP` — Float32, units null at point level
- `ADP.7X SHAFT VIB BEARING 7 MAIN TURBINE` — Float32
- `ADP1. BEARING OIL PRESS LL TRIPPED` — trip/alarm flag

> Raw point `nameFilter` supports wildcards (`*BEARING*`, `*TEMP*`, etc.).
> Keep `maxCount` bounded (≤100) to respect rate limits — categories return
> far more than the cap.

## Units vocabulary (BSR1, 13 distinct)

`degree Celsius` (56), `percent` (25), `Tonne per hour` (21), `Micrometer` (12),
`ampere` (9), `kilowatt` (7), `kilopascal` (7), `volt` (2),
`kilocalorie per kilowatthour` (2), `megawatt` (1), `revolution per minute` (1),
`hour` (7), plus 391 attributes with no unit recorded.

## Other AF databases (not in scope)

| Database | Note |
|---|---|
| `Indonesia Power Corporate` | primary asset hierarchy (BSR verified here) |
| `Pump CBM` | pump condition-based monitoring (not walked) |
