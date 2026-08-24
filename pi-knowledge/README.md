# PI Knowledge

Read-only knowledge base for the central PI Web API / PI Asset Framework
operational boundary used by NADI discovery.

The existing acquisition path remains outside this repository:

```text
DCS / control systems → existing OPC / PI Interface pipeline
    → central PI Data Archive / PI AF → PI Web API → future NADI evidence
```

PI Vision is a visualization surface. It is not treated as a second source
system. PI Web API is the supported integration candidate only where an
instance-verified GET contract exists.

This repository records:

- Data Servers
- PI Points / Tags
- Asset Servers
- AF Databases
- Elements
- Attributes
- WebIds
- units of measure
- stream access patterns
- recorded/interpolated/summary capabilities
- unit-specific equipment mappings

No PI collector is created by this knowledge task. Any future collector must
consume verified AF/stream evidence through the read-only API and keep
credentials outside Git.

## Principle

A PI tag alone is not enough.

The target is semantic knowledge such as:

```text
BFP 1A Motor DE Bearing Temperature
→ equipment: BFP-1A
→ parameter: bearing_temperature
→ position: motor_drive_end
→ unit: degC
→ source: PI
→ tag/webid: verified source identifier
```
