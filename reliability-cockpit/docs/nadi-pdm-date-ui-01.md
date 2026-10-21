# NADI-PDM-DATE-UI-01 — Indonesian date readability

21 October 2026. Local candidate based on
`86278e916c70852ccac5d15eebb075f5f7e5591d`. Requirements: FR-03/04, UI-04.

The user requested understandable dates and times in Pusat PdM. This bounded
presentation change covers the inspection register/navigation, exact detail,
measurement history/scatter labels, revision/audit history, and form/filter
previews. It does not change DTOs, stored values, source collection, canonical
measurement eligibility, filters, application writes, authentication, or runtime.

## Reading rules

| Evidence | Indonesian presentation |
|---|---|
| Source DATE `2019-01-03` | `3 Januari 2019`; no invented midnight or zone |
| Known canonical/application instant `2026-10-20T23:30:00Z` | `21 Oktober 2026, 06.30.00 WIB` in fixed UTC+07:00 (WIB) |
| Source DATETIME `2019-01-03T00:15+09:00` | `3 Januari 2019, 00.15 WIT`; reported source offset retained |
| LOCAL_DATETIME | Calendar and clock retained; `zona waktu belum diketahui` |
| TIME | Clock retained; `tanggal dan zona waktu belum diketahui` |
| RAW | `Teks / serial belum ditafsirkan`; original text/serial remains accessible |
| Null / UNKNOWN | `Belum diketahui` |
| Invalid/mixed calendar/time | Explicit invalid-format label; original value remains accessible in detail |

Source clocks retain independent roles (sample/acquisition/analysis/report).
The register never substitutes record creation/update time for missing inspection
time. Application/audit times are labelled separately. Source detail exposes
both raw claims and explicit values, including conflicts, without reconciling
them automatically. Date-only/local values never pass through timezone conversion.
WIB is a proleptic fixed UTC+07:00 display, including dates before 1964, rather
than historical Jakarta civil time. `Etc/GMT-7` uses the reversed IANA sign for
UTC+07:00. The original source offset/ISO remains available. Pre-1964 tests cover
1900/1948/1960 and both genuine and false midnight boundaries.
RFC3339 `-00:00` remains an unknown zone. Explicit seconds/fractions are retained.
ISO values remain unchanged in inputs and raw detail. Form previews use the same
formatter; input accessible names remain stable. Per-measurement previews occupy
their own grid row so keyboard focus preserves existing control/button alignment.

## Reproducible qualification

From `reliability-cockpit/web`, use Node 22 and existing installed dependencies:

```sh
node scripts/pdm-date-check.mjs
node scripts/pdm-input-check.mjs
node scripts/pdm-workbook-check.mjs
node scripts/pdm-capture-check.mjs
node scripts/pdm-follow-up-check.mjs
node scripts/eng-product-check.mjs
node scripts/phase2-ui-check.mjs
node scripts/localization-check.mjs
node node_modules/typescript/bin/tsc --noEmit --incremental false
npm run lint
npm run build
```

The nine focused date groups cover leap/calendar validation, source precision,
WIB midnight conversion, offsets and `-00:00`, seconds/fractions, ambiguous locals,
null/invalid/mixed input, conflicting claims, locale/timezone independence, and
unchanged draft/readback values. The focused check is included in
`npm run check:pdm-input`; the formatter is included in lint coverage.

Actual component browser qualification:

```sh
NADI_PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs \
NADI_CHROMIUM_EXECUTABLE=/path/to/cached/chromium \
NADI_BROWSER_OUTPUT=/tmp/nadi-pdm-date-evidence \
node scripts/pdm-date-browser.mjs

NADI_PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs \
NADI_BROWSER_OUTPUT=/tmp/nadi-pdm-date-existing-input \
node scripts/pdm-input-browser.mjs
```

The focused fixture mounts actual Pusat PdM components, intercepts every request
at `https://pdm-dates.synthetic.invalid`, and rejects unexpected requests/writes.
It checks list/detail/native revision/measurement history/scatter/audit/form
consistency in en-US browsers using America/Los_Angeles and Pacific/Kiritimati;
it also checks source DATE/DATETIME/local/time/raw claims and captures source
detail at 1440/768/390 CSS pixels. No server, real login, network source, TLS
bypass, operational API, or database is used. Existing PdM browser assertions
retain their original focus/keyboard requirements without weakening tests.

## Local results

- Focused date checks: 9 groups PASS; actual component date browser: 40 checks PASS.
- Existing PdM input browser: 575 checks PASS, including 320 focus geometry
  observations with unchanged keyboard assertions (3/9/11/12 rows, light/dark,
  desktop widths and effective-width zoom proxy).
- Existing semantic checks: input 21, workbook 48, capture 11, follow-up 9,
  Engineering product 8, Phase 2 UI 8, localization 10 — all PASS.
- TypeScript, full configured lint, production build and `git diff --check` PASS.
  Existing unrelated warnings remain: EngineeringWorkspace useEffect dependency,
  missing Next ESLint plugin, and mixed-support CSS alignment values.
- Local evidence: `/tmp/nadi-pdm-date-ui-01-v2/results.json`, source-detail
  and source-clock screenshots at 1440/768/390; existing regression evidence at
  `/tmp/nadi-pdm-date-existing-input/results.json` and `keyboard/results.json`.
  Source-clock screenshots were visually inspected at 390 and 1440.

## Independent review correction — V2

The historical-clock regression reproduced on V1: UTC midnight in 1900 was
labelled `07.07.12 WIB`; historical Jakarta offsets similarly affected 1948 and
1960. V2 uses fixed UTC+07:00 for the application WIB display and leaves source
clock formatting untouched. Its nine semantic groups, 40 component browser
checks, TypeScript, focused formatter lint and whitespace checks pass. The
broader 575-check keyboard/workflow suite and production build above passed on
V1; they were not repeated for this formatter-only historical correction. Form,
CSS, focus logic and geometry tests are byte-for-byte unchanged from V1.

## Acceptance limits

Local automated/component visual checks establish candidate behavior only.
Screenshots are synthetic test evidence, not live visibility or engineer/PO UAT.
Exact-head CI, independent delta review and parent draft-PR publication remain
separate gates. No commit, push, deployment, database/grant change, source
collection, or operational activation is performed by this task.
