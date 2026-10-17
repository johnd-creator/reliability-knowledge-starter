# Live development evidence — NADI-PH2-UI-BUNDLE-01

Actual HTTPS3000, active HEAD `7daab3a62866f19b30fb45462a94bafff8795dc5`
with task presentation edits/dirty state. Authenticated **synthetic local QA**;
no intercepted browser fixtures or operational measurements in these screenshots.
Screenshots show actual existing DEV provenance banner; its design is outside scope.

| Screen | Desktop1440 | Tablet768 | Mobile390 |
|---|---|---|---|
| Case register | [Desktop](cases-register-1440-light.png) | [Tablet](cases-register-768-light.png) | [Mobile](cases-register-390-light.png) |
| Case form, viewport positioned at form | [Desktop](case-form-1440-light.png) | [Tablet](case-form-768-light.png) | [Mobile](case-form-390-light.png) |
| Case review/detail, viewport positioned at detail | [Desktop](case-review-1440-light.png) | [Tablet](case-review-768-light.png) | [Mobile](case-review-390-light.png) |
| PdM register | [Desktop](pdm-register-1440-light.png) | [Tablet](pdm-register-768-light.png) | [Mobile](pdm-register-390-light.png) |
| Measurement form, viewport positioned at form | [Desktop](pdm-input-1440-light.png) | [Tablet](pdm-input-768-light.png) | [Mobile](pdm-input-390-light.png) |
| Inspection detail, viewport positioned at detail | [Desktop](pdm-detail-1440-light.png) | [Tablet](pdm-detail-768-light.png) | [Mobile](pdm-detail-390-light.png) |
| Measurement history | [Desktop](pdm-history-1440-light.png) | [Tablet](pdm-history-768-light.png) | [Mobile](pdm-history-390-light.png) |

Before: [Case register](before-cases-1440.png), [PdM register](before-pdm-1440.png).
Dark: [PdM](pdm-register-1440-dark.png), [Case detail](case-review-1440-dark.png).
Fast Refresh: [actual browser](fast-refresh-live-1440.png), [same-document proof](fast-refresh.json).

Routes: `/engineering/cases`, `/engineering/cases?record=<synthetic-case>`, `/pdm`,
`/pdm?record=<synthetic-inspection>`. Form/history use existing in-page navigation.
Full-page screenshots and viewport screenshots are distinguished in the table;
viewport captures do not claim to show the entire form.

[Live E2E](live-e2e.json) · [Filter/security](filter-security.json) ·
[Responsive/routes](browser-visual.json) · [History responsive retest](history-responsive.json) ·
[Frontend checks](frontend-checks.json) · [Preservation](preservation.json) · [Runtime final](runtime-final.json).

No passwords, cookies, CSRF tokens, private DSNs or backup contents are included.
Read the [implementation report](../../NADI-PH2-UI-BUNDLE-01.md) for scope,
failed attempts, skipped tests and remaining engineer/PO acceptance gates.
