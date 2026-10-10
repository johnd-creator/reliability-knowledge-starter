# Bundle B responsive evidence

2026-10-10 · functional source `0df4b47b951013aa03ae1bb97fad7e4167bb474e`.
All fifteen screenshots use browser-intercepted DEMO fixtures; no plant or personal records.
The display-only fixture identity is sanitized. Actual authentication/API regressions run separately.
Original official PNGs remain at repository root, unchanged.

| Page | Desktop 1440 | Tablet 768 | Mobile 390 |
|---|---|---|---|
| Asset Register | [1440px](asset-register-1440.png) | [768px](asset-register-768.png) | [390px](asset-register-390.png) |
| Asset Detail | [1440px](asset-detail-1440.png) | [768px](asset-detail-768.png) | [390px](asset-detail-390.png) |
| PdM Center | [1440px](pdm-1440.png) | [768px](pdm-768.png) | [390px](pdm-390.png) |
| Recommendations | [1440px](recommendations-1440.png) | [768px](recommendations-768.png) | [390px](recommendations-390.png) |
| Action Board | [1440px](action-board-1440.png) | [768px](action-board-768.png) | [390px](action-board-390.png) |

[Browser assertions](browser-report.json) — 129 PASS, including read-only actual routes and synthetic cases.
[HMR / rollback checks](runtime-report.json) — 18 PASS.
[Implementation and review](../../../reliability-cockpit/docs/nadi-ux-bundle-b.md).

Narrow tables intentionally scroll inside keyboard-focusable regions. The mobile recommendation
screenshot retains the keyboard focus indicator from the scroll test. Screenshot appearance and
self-review do not establish Product Owner approval or operational engineering acceptance.
