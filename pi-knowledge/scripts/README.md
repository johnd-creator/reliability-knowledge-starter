# Safe PI Discovery Scripts

All discovery scripts must:

- perform read-only requests only
- use conservative request rates
- have explicit timeouts
- load secrets from environment variables
- redact Authorization/session output
- avoid bulk historical downloads by default
- store metadata first, data samples second
