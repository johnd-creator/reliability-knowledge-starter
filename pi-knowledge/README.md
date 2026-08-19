# PI Knowledge

Living knowledge base for PI Web API / PI-related operational data.

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
