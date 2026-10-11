# Fullscreen login evidence

See [implementation and review](../../nadi-ux-login-01.md).

Actual before screenshots are privately retained under
`.nadi-dev/state/ux-login-01/before/` at the prior serving SHA 5d8b5c0.
The real HTTPS login displayed AppShell at all three widths.

Candidate component screenshots from the hermetic browser suite are labeled as
network-isolated fixture evidence, separate from actual live HTTPS screenshots.
The suite preserves simulated Case/Recommendation/Advisory/ACK semantics and makes
no requests to operational services or the persistent QA database.

Actual credential-free login images and the exact source/CI/runtime handoff are
added after the official controlled frontend-only preview checks. Engineering
screens with operational data, account names or audit contents remain private.

## Network-isolated component fixtures

395 checks PASS. No live backend/data/persistence claim.

| Width | Light | Dark |
| --- | --- | --- |
| 1440px | [Light](fixture-login-1440.png) | [Dark](fixture-login-dark-1440.png) |
| 768px | [Light](fixture-login-768.png) | [Dark](fixture-login-dark-768.png) |
| 390px | [Light](fixture-login-390.png) | [Dark](fixture-login-dark-390.png) |
