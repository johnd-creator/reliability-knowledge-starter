# NADI V2 browser evidence

**Synthetic fixture UI only; not live backend UAT or Product Owner acceptance.**
Actual React components rendered by the existing network-isolated Chromium harness.
Before: main `c7930694187b61ffa6dae90e6a14938e7564c3e7`.
After: this branch, UI checkpoint `43885e4` (subsequent commits package tests/docs).
No private runtime state, credentials or operational captures are included.

Each pair uses the same fixture, workflow state, theme and viewport width (filename).
Full-page heights may differ because the layout changed. Case register is captured
after the same synthetic workflow with no selected detail; Case detail uses the
same deep link. Login and logout are preservation comparisons. The Reports and
Integration harnesses also cover 1920px. The broader route harness covers 24 routes
at 390/768/1440px, including unavailable states where fixtures have no contract.

| Screen / viewport | Main baseline | V2 candidate |
|---|---|---|
| overview-1440 | [Before](before-overview-1440.png) | [After](after-overview-1440.png) |
| assets-1440 | [Before](before-assets-1440.png) | [After](after-assets-1440.png) |
| asset-detail-1440 | [Before](before-asset-detail-1440.png) | [After](after-asset-detail-1440.png) |
| pdm-1440 | [Before](before-pdm-1440.png) | [After](after-pdm-1440.png) |
| case-detail-1440 | [Before](before-case-detail-1440.png) | [After](after-case-detail-1440.png) |
| recommendations-1440 | [Before](before-recommendations-1440.png) | [After](after-recommendations-1440.png) |
| action-board-1440 | [Before](before-action-board-1440.png) | [After](after-action-board-1440.png) |
| case-register-1440 | [Before](before-case-register-1440.png) | [After](after-case-register-1440.png) |
| measurement-1440 | [Before](before-measurement-1440.png) | [After](after-measurement-1440.png) |
| reports-1440 | [Before](before-reports-1440.png) | [After](after-reports-1440.png) |
| integration-1440 | [Before](before-integration-1440.png) | [After](after-integration-1440.png) |
| login-1440 | [Before](before-login-1440.png) | [After](after-login-1440.png) |
| logout-1440 | [Before](before-logout-1440.png) | [After](after-logout-1440.png) |
| measurement-390 | [Before](before-measurement-390.png) | [After](after-measurement-390.png) |
| measurement-768 | [Before](before-measurement-768.png) | [After](after-measurement-768.png) |
| pdm-dark-390 | [Before](before-pdm-dark-390.png) | [After](after-pdm-dark-390.png) |
| integration-dark-768 | [Before](before-integration-dark-768.png) | [After](after-integration-dark-768.png) |
| reports-dark-1920 | [Before](before-reports-dark-1920.png) | [After](after-reports-dark-1920.png) |
| login-dark-390 | [Before](before-login-dark-390.png) | [After](after-login-dark-390.png) |
| assets-768 | [Before](before-assets-768.png) | [After](after-assets-768.png) |

## Inspection and reproducibility

Manually inspected representative full-page desktop, tablet, mobile and dark
captures. Fixed search icon overlap, oversized text-only statistic cards, cyan
badge contrast, and mobile PdM statistic density during this work. Tables retain
internal horizontal scrolling; narrow screenshots do not display every column
simultaneously. Measurement rows become grouped two-column fields at tablet width
and single-column fields on mobile.

Use Node 22 and `npm ci` in `reliability-cockpit/web`, then the existing
`localization-browser.mjs`, `pdm-input-browser.mjs`, `integration-browser.mjs`,
`reports-browser.mjs`, and `login-visual-browser.mjs` scripts. Set
`NADI_PLAYWRIGHT_MODULE` to the trusted installed Playwright module and
`NADI_AXE_MODULE` to `@axe-core/playwright/dist/index.mjs` for the localization,
Reports and Integration scans. CI installs those tools in runner temporary storage.
No persistent frontend listener is needed. See [delivery report](../../NADI-UX-V2-OVERHAUL-01.md)
for counts, scope and pending acceptance. `manifest.json` records screenshot hashes.
