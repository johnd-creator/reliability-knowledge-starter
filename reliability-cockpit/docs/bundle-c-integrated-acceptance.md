# Bundle C integrated acceptance — candidate only

Baseline main: `7a846ef2c7e25306f23da99dd011e1d54aa8f4a4`.
All checks below are local fixtures, not a production readiness certification.

| Gate | Result | Evidence |
|---|---|---|
| Trusted server identity, CSRF/origin, revocation | PASS | Existing identity negatives plus `test_bundle_c_integration.py` trusted-session workflow |
| Same-asset context and invalid/partial providers | PASS | Context fixtures reject foreign identities before queries; corrupt pages become INVALID_RECORD, unavailable totals null |
| Inspection review and immutable lineage | PASS | Explicit SUBMITTED / UNDER_REVIEW / APPROVED / RETURNED / REJECTED; frozen reviewed snapshot preserves null/text/units/time |
| Case/recommendation linking and independent closure | PASS | Approved exact case pin, evidence version checks, local completion evidence; existing WO snapshot unchanged |
| Application concurrency | PASS | Disposable PostgreSQL CAS/audit/receipt/revocation tests; case reopening waits for recommendation submission lock, then further review fails closed |
| Mart writer isolation / reader SELECT-only | PASS | Existing disposable Mart governance/condition reader tests and wrong-store application guard; no application Mart DML |
| Source read-only / operational mount | PASS | Explicit new-path source/admin negatives; production create_app has no Engineering routes |
| Source quality vs freshness vs health | PASS | Good evidence can simultaneously be SOURCE_STALE under a fixture policy; blank policy UNKNOWN; asset NOT_ASSESSED |
| Frontend safety / typing / build | PASS | 37 Engineering + 25 Phase2 + 38 workflow assertions; 27 UI files safety checked; TypeScript and Next.js production build |
| Browser workflow / responsiveness | PASS | 32 loopback development assertions at 390/768/1365 widths; 8 production-build assertions prove demo blocked with both flags enabled |
| Production activation | BLOCKED | Enterprise provider/bootstrap, reviewed writer/migration provisioning, approved PdM fields and operational UAT still missing |

## Exact suite counts

- Cockpit: **532 run, 532 PASS, 0 FAIL, 0 SKIP**, with all three disposable local
  PostgreSQL fixture DSNs and Compose tests configured. Full-suite runtime about58s.
- Maximo Collector: **181 run, 181 PASS, 0 FAIL, 0 SKIP**.
- PI Collector: **191 run, 180 PASS, 0 FAIL, 11 SKIP**. The 11 Timescale migration
  tests require an isolated Timescale DSN; ordinary PostgreSQL is not represented as Timescale.
- Data contracts: **14 run, 14 PASS**; **35 Draft2020-12 schemas** validate.
- Integrated HTTP acceptance: **17 PASS** (SQLite + disposable PostgreSQL), included
  in the Cockpit total. These are not additional distinct tests to add to532.
- Frontend: **100 assertions PASS** (37+25+38); product safety covers27 UI files.
- Browser: **40 assertions PASS** (32 development +8 production gate).
- TypeScript, Next.js production build and `git diff --check`: PASS.

Existing fixture teardown can emit ResourceWarnings; no test failures or missing
Cockpit PostgreSQL suites are hidden. Timescale SKIPs remain explicit limitations.

## Reproduction (no production DSNs)

Run each subproject's own virtual-environment Python with dependencies installed:

```sh
# reliability-cockpit; point these ONLY to disposable localhost *_test DBs:
COCKPIT_CONFIG_MODE=managed DATABASE_URL=sqlite:// NADI_COMPOSE_TESTS=1 \
NADI_APPLICATION_TEST_DSN="$DISPOSABLE_APPLICATION_TEST_DSN" \
NADI_ENGINEERING_TEST_DSN="$DISPOSABLE_ENGINEERING_TEST_DSN" \
NADI_MART_TEST_DSN="$DISPOSABLE_MART_TEST_DSN" \
python -m unittest discover -s tests -q

# maximo-collector
python -m unittest discover -s tests -q
# pi-collector
PI_CONFIG_MODE=managed python -m unittest discover -s tests -v
# reliability-data-contracts
python -m unittest discover -s tests -q
# reliability-cockpit/web
npm run check:engineering
npm run check:phase2
npm run check:workflow
npm run check:product-safety
npx tsc --noEmit
COCKPIT_API_BASE=http://127.0.0.1:9 NEXT_TELEMETRY_DISABLED=1 npm run build
```

Browser harnesses: `scripts/bundle-c-browser.py` and
`scripts/bundle-c-production-gate.py`. They allow only the loopback test preview
ports and abort every other browser request. Start disposable development/production
previews with source backend unreachable, both Engineering flags true and respective
NODE_ENV. Preview processes are unrelated to operational containers. Screenshots and
logs stay outside Git; no accepted source payloads or credentials are used.

## In-scope acceptance repairs

C6 adds bounded provider shape/asset validation, application transaction guards for
reviewed case/inspection versions, canonical IN_REVIEW presentation states for cases
and recommendations, explicit neutral badge semantics, stable accessible input names,
review rationale retention and protection for unsaved case/proposal input. The full
stack must be reviewed together; C4/C5 alone are not an activation artifact.

Application record guards serialize same-store reviewed inputs on PostgreSQL.
Canonical Mart reads remain SELECT-only and bounded across stores, not an atomic
cross-database historical snapshot. Accepted source snapshots are frozen; changes
never replace prior reviewed evidence silently.

Task-attributable production source GET/write, DB write/DDL, deployment/restart,
mapping/signal/projection, Phase1 journal/cursor/evidence mutation counts: **0**.
No operational infrastructure inventory or secret configuration was read or published.
