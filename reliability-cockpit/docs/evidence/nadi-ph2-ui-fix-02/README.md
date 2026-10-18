# Live evidence — NADI-PH2-UI-FIX-02

HTTPS3000, HEAD7daab3a with Mode A dirty edits. Actual browser, verified existing CA,
no TLS bypass. Authenticated content is **synthetic QA**. No operational data snapshot.

Before: [large header](before-header-1440.png), [embedded PdM login](before-pdm-signed-out-1440.png).

| Screen | 1440 | 768 | 390 |
|---|---|---|---|
| Signed out `/pdm` | [Desktop](pdm-signed-out-1440-light.png) | [Tablet](pdm-signed-out-768-light.png) | [Mobile](pdm-signed-out-390-light.png) |
| Technical details open | [Desktop](header-details-1440-light.png) | [Tablet](header-details-768-light.png) | [Mobile](header-details-390-light.png) |
| Standalone `/login` | [Desktop](login-1440-light.png) | [Tablet](login-768-light.png) | [Mobile](login-390-light.png) |
| Authenticated `/pdm` | [Desktop](pdm-authenticated-1440-light.png) | [Tablet](pdm-authenticated-768-light.png) | [Mobile](pdm-authenticated-390-light.png) |
| PdM dark mode | [Desktop](pdm-authenticated-1440-dark.png) | [Tablet](pdm-authenticated-768-dark.png) | [Mobile](pdm-authenticated-390-dark.png) |
| Login dark mode | [Desktop](login-1440-dark.png) | [Tablet](login-768-dark.png) | [Mobile](login-390-dark.png) |

[Real test-session revocation](case-session-revoked-1440.png) ·
[Signed-out factual dashboard/header](dashboard-compact-1440.png).
Technical details and dashboard captures are viewport screenshots; remaining page
captures are full-page. Passwords/CSRF/session tokens are not shown.

**Fixture only:** [critical mismatch with panel collapsed](fixture-only-mismatch-collapsed-1440.png).
Only the disposable browser's status response is intercepted. Server/runtime provenance
is unchanged and healthy; this file is not evidence of an actual runtime mismatch.

[Browser results](browser-results.json) · [Frontend checks](frontend-checks.json) ·
[Hermetic auth result](auth-regression.log) · [Lint](lint.log).
[Report, limitations and correction history](../../NADI-PH2-UI-FIX-02.md).
