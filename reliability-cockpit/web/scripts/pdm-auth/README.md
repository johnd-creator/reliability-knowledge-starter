# PdM authenticated workspace regression

Run from `reliability-cockpit/web` with its installed dependencies. The fixture imports the actual authentication wrapper, PdM page/form/command hook, and draft providers. Its composition keeps only `PdmDraftProvider` outside `AuthenticatedWorkspace`; the unchanged Engineering providers remain inside. Test diagnostics are hidden and do not belong to the product.

Build a temporary browser bundle using the existing helper:

```sh
node --input-type=module - <<'JS'
import {browserBundle} from './scripts/localization-browser-build.mjs';
const bundle = await browserBundle('scripts/pdm-auth/entry.tsx');
console.log(bundle.temp + '/candidate.js');
JS
```

Use the resulting path and an available Chromium executable. The Python environment needs Playwright; the script does not install a browser.

```sh
python scripts/pdm-auth-browser-check.py \
  --bundle /tmp/nadi-id-browser-EXAMPLE/candidate.js \
  --chromium /path/to/chromium \
  --report /tmp/pdm-auth-workspace-results.json
```

All requests are intercepted at `https://pdm-auth-workspace-fixture.invalid`; unexpected requests abort and fail the test. No server, PostgreSQL, real login, localhost runtime, source system, operational record, or authentication configuration is used. Synthetic API responses exercise actual mounted components. This is behavioral qualification, not visual UAT or a test of the active laptop login deployment.

The thirteen scenarios cover same-identity focus recovery, pending completion after remount, lost-ACK retry identity, cross-record discard consent, transient session503 retry, pending receipts through session503, bounded listing and honest pagination, multiline source/context/clock text, changed subject/role/asset scope, and session401/403 cleanup. A failed scenario exits nonzero and records diagnostics. `--only` accepts an optional scenario-name substring for diagnosis; no match also exits nonzero.

The one-record inspection list is checked against an honest paginated mock. The separate backend/contract checks qualify actual persistence and input bounds. This fixture does not infer Case/Recommendation lifecycle readiness, engineering method approval, canonical mapping, or permission to merge or deploy.
