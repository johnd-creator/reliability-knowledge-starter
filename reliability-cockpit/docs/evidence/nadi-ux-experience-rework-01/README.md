# NADI experience rework — matching browser comparisons

**SYNTHETIC FIXTURES. These are actual React component browser captures, not plant data, live preview activation or PO approval.**

[Open the interactive comparison](compare.html) to select a screen, size and theme.
[Design critique, rationale and verification](../../NADI-UX-EXPERIENCE-REWORK-01.md).

40 matching pairs: all five screens × 1440/1920/768/390 × light/dark. Full-page PNGs;
viewport height 1086. Images differ in document height because the real layout changes.
The same harness/fixtures and input values are used for both sides. Theme transitions
settle before capture. V2 comes from the pristine reviewed `260c4f9` source; candidate
comes from this branch. `index.json` records dimensions and SHA256 hashes.

The measurement state contains three original-value rows (0, 4.2, UNKNOWN/null), literal
mm/s units and a fixed zone-bearing timestamp. The Case state is an author-owned DRAFT
with a frozen synthetic inspection reference; no independent reviewer decision is
fabricated. Status and unavailability disclosures stay visible. The author role cannot
approve its own record. The screenshot harness intercepts **every request**, never
contacts localhost/source systems, and starts no listener or service.

To reproduce, install the locked web dependencies, supply Playwright and axe using
`NADI_PLAYWRIGHT_MODULE` / `NADI_AXE_MODULE`, then run `node scripts/experience-browser.mjs`
from `reliability-cockpit/web`. `NADI_BROWSER_OUTPUT` chooses the output directory.
For baseline captures, use the same script with its browserBundle import pointing to
a pristine V2 checkout and `NADI_EXPERIENCE_BASELINE=1`; run from that checkout's web root.

Review scope: hierarchy, record discoverability, measurement ergonomics, provenance and
review separation, light/dark contrast, keyboard focus and all four widths. Full desktop
layouts have been visually inspected, along with tablet registers, mobile form/details
and dark mode. Automated axe scans are bounded evidence, not a complete accessibility
certification. The keyboard regression separately exercises 1/3/12 rows, forward/reverse
Tab and 125% effective-width proxy scenarios.

| Screen | Width | Theme | V2 | Proposed experience |
|---|---:|---|---|---|
| executive | 1440 | light | [Before](before/executive-light-1440.png) | [After](after/executive-light-1440.png) |
| executive | 1440 | dark | [Before](before/executive-dark-1440.png) | [After](after/executive-dark-1440.png) |
| executive | 1920 | light | [Before](before/executive-light-1920.png) | [After](after/executive-light-1920.png) |
| executive | 1920 | dark | [Before](before/executive-dark-1920.png) | [After](after/executive-dark-1920.png) |
| executive | 768 | light | [Before](before/executive-light-768.png) | [After](after/executive-light-768.png) |
| executive | 768 | dark | [Before](before/executive-dark-768.png) | [After](after/executive-dark-768.png) |
| executive | 390 | light | [Before](before/executive-light-390.png) | [After](after/executive-light-390.png) |
| executive | 390 | dark | [Before](before/executive-dark-390.png) | [After](after/executive-dark-390.png) |
| pdm | 1440 | light | [Before](before/pdm-light-1440.png) | [After](after/pdm-light-1440.png) |
| pdm | 1440 | dark | [Before](before/pdm-dark-1440.png) | [After](after/pdm-dark-1440.png) |
| pdm | 1920 | light | [Before](before/pdm-light-1920.png) | [After](after/pdm-light-1920.png) |
| pdm | 1920 | dark | [Before](before/pdm-dark-1920.png) | [After](after/pdm-dark-1920.png) |
| pdm | 768 | light | [Before](before/pdm-light-768.png) | [After](after/pdm-light-768.png) |
| pdm | 768 | dark | [Before](before/pdm-dark-768.png) | [After](after/pdm-dark-768.png) |
| pdm | 390 | light | [Before](before/pdm-light-390.png) | [After](after/pdm-light-390.png) |
| pdm | 390 | dark | [Before](before/pdm-dark-390.png) | [After](after/pdm-dark-390.png) |
| measurement | 1440 | light | [Before](before/measurement-light-1440.png) | [After](after/measurement-light-1440.png) |
| measurement | 1440 | dark | [Before](before/measurement-dark-1440.png) | [After](after/measurement-dark-1440.png) |
| measurement | 1920 | light | [Before](before/measurement-light-1920.png) | [After](after/measurement-light-1920.png) |
| measurement | 1920 | dark | [Before](before/measurement-dark-1920.png) | [After](after/measurement-dark-1920.png) |
| measurement | 768 | light | [Before](before/measurement-light-768.png) | [After](after/measurement-light-768.png) |
| measurement | 768 | dark | [Before](before/measurement-dark-768.png) | [After](after/measurement-dark-768.png) |
| measurement | 390 | light | [Before](before/measurement-light-390.png) | [After](after/measurement-light-390.png) |
| measurement | 390 | dark | [Before](before/measurement-dark-390.png) | [After](after/measurement-dark-390.png) |
| cases | 1440 | light | [Before](before/cases-light-1440.png) | [After](after/cases-light-1440.png) |
| cases | 1440 | dark | [Before](before/cases-dark-1440.png) | [After](after/cases-dark-1440.png) |
| cases | 1920 | light | [Before](before/cases-light-1920.png) | [After](after/cases-light-1920.png) |
| cases | 1920 | dark | [Before](before/cases-dark-1920.png) | [After](after/cases-dark-1920.png) |
| cases | 768 | light | [Before](before/cases-light-768.png) | [After](after/cases-light-768.png) |
| cases | 768 | dark | [Before](before/cases-dark-768.png) | [After](after/cases-dark-768.png) |
| cases | 390 | light | [Before](before/cases-light-390.png) | [After](after/cases-light-390.png) |
| cases | 390 | dark | [Before](before/cases-dark-390.png) | [After](after/cases-dark-390.png) |
| case-detail | 1440 | light | [Before](before/case-detail-light-1440.png) | [After](after/case-detail-light-1440.png) |
| case-detail | 1440 | dark | [Before](before/case-detail-dark-1440.png) | [After](after/case-detail-dark-1440.png) |
| case-detail | 1920 | light | [Before](before/case-detail-light-1920.png) | [After](after/case-detail-light-1920.png) |
| case-detail | 1920 | dark | [Before](before/case-detail-dark-1920.png) | [After](after/case-detail-dark-1920.png) |
| case-detail | 768 | light | [Before](before/case-detail-light-768.png) | [After](after/case-detail-light-768.png) |
| case-detail | 768 | dark | [Before](before/case-detail-dark-768.png) | [After](after/case-detail-dark-768.png) |
| case-detail | 390 | light | [Before](before/case-detail-light-390.png) | [After](after/case-detail-light-390.png) |
| case-detail | 390 | dark | [Before](before/case-detail-dark-390.png) | [After](after/case-detail-dark-390.png) |
