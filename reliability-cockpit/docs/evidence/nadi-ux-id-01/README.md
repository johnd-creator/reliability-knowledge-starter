# NADI-UX-ID-01 — visual and localization evidence

Source implementation: `2abbe61a0973d2cd8ce1d788e7fad525cb0173b6` (delivery docs do not change this frontend tree).

**DEMO / QA SINTETIS — network-isolated candidate components.** All browser requests, including login, Case/Recommendation/Advisory/ACK commands, are fulfilled by synthetic fixtures. No Next/QA listener, real credential, source request, persistent QA write or runtime deployment is involved. These are frontend interaction/visual results; actual security/persistence remains covered separately by unchanged backend tests and exact-head CI.

| Page | Desktop 1440 | Tablet 768 | Mobile 390 |
|---|---|---|---|
| executive | [PNG](executive-1440.png) | [PNG](executive-768.png) | [PNG](executive-390.png) |
| assets | [PNG](assets-1440.png) | [PNG](assets-768.png) | [PNG](assets-390.png) |
| asset-detail | [PNG](asset-detail-1440.png) | [PNG](asset-detail-768.png) | [PNG](asset-detail-390.png) |
| data-trust | [PNG](data-trust-1440.png) | [PNG](data-trust-768.png) | [PNG](data-trust-390.png) |
| login | [PNG](login-1440.png) | [PNG](login-768.png) | [PNG](login-390.png) |
| pdm | [PNG](pdm-1440.png) | [PNG](pdm-768.png) | [PNG](pdm-390.png) |
| recommendation | [PNG](recommendation-1440.png) | [PNG](recommendation-768.png) | [PNG](recommendation-390.png) |
| action-board | [PNG](action-board-1440.png) | [PNG](action-board-768.png) | [PNG](action-board-390.png) |
| case | [PNG](case-1440.png) | [PNG](case-768.png) | [PNG](case-390.png) |
| advisory | [PNG](advisory-1440.png) | [PNG](advisory-768.png) | [PNG](advisory-390.png) |
| inbox | [PNG](inbox-1440.png) | [PNG](inbox-768.png) | [PNG](inbox-390.png) |
| glossary | [PNG](glossary-1440.png) | [PNG](glossary-768.png) | [PNG](glossary-390.png) |

[Dark mobile](dark-390.png) · [370 browser checks](browser-results.json) · [SHA256 manifest](screenshot-sha256.json) · [1344 presentation key/translation pairs](terminology-matrix.csv) · [read-only preservation results](preservation-results.json).

24 route/component scenes × three sizes produced 72 captures plus dark mode; 37 selected originals are retained here. Data Trust/maintenance/FMEA/RCFA/health scenes also exercise explicit unavailable states where fixture contracts are absent. This is not evidence that operational data is unavailable. Real values, names, identifiers, codes, timestamps and original record text are not translated or substituted in factual mode.

Candidate methods/threshold definitions in the 41-entry glossary remain **Menunggu Validasi Engineer**. Original `konsep1.png`–`konsep5.png`, NADI logo and workbook are unchanged. Full methodology, safety boundaries, remaining preview blocker and acceptance status: [review report](../../nadi-ux-id-01.md).
