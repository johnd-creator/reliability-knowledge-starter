# Bundle D quality gates

All tests use managed config isolation and disposable loopback stores. Commands:

- Cockpit: `PYTHONPATH=.:tests:<testdeps> COCKPIT_CONFIG_MODE=managed DATABASE_URL=sqlite:// NADI_COMPOSE_TESTS=1 NADI_APPLICATION_TEST_DSN=<local *_test> NADI_ENGINEERING_TEST_DSN=<local *_test> NADI_MART_TEST_DSN=<local *_test> python -m unittest discover -s tests -q` —600 passed,0 failed,0 skipped.
- Maximo Collector: `PYTHONPATH=.:<testdeps> MAXIMO_CONFIG_MODE=managed python -m unittest discover -s tests -q` —181 passed,0 failed,0 skipped.
- PI Collector: `PYTHONPATH=.:<compatible API testdeps> PI_CONFIG_MODE=managed PI_MIGRATION_TEST_DSN=<local pi_runtime_test> python -m unittest discover -s tests -q` —191 passed,0 failed,0 skipped.
- Contracts: `python -m unittest discover -s tests -q` —14 passed.
- Socket HTTPS/PostgreSQL: `python -m unittest test_bundle_d_http.RealHttpQaTest -v` —11 passed; also included in full Cockpit regression after canonical fixture migration update.
- Browser: `python tests/qa/browser.py` —25 passed; real UI/proxy/backend and durable records, three viewport widths.
- Frontend: `npm run check:engineering`37, `check:phase2`25, `check:workflow`38, `check:http-qa`10; all pass. `check:product-safety`29 UI source files pass; `npx tsc --noEmit`, `npm run build`, `git diff --check` pass.

The11 former Timescale skips now run on a separate cached Timescale2.16.1/PG16
container, private loopback port and tmpfs data only. Migration guards require
pi_runtime_test and source request mocks. No operational volume/network/worker
is changed. No claim about production Timescale acceptance is made here.

Private test dump catalog/restore verified matching application row counts.
No production backup/DDL or source request. Initial environment-only failures
(wrong working directory/interpreter, automatic dev certificate generation) were
corrected locally; final gates use exact candidate source. Real browser exposed
missing explicit select labels, repaired and revalidated. Build is validation,
not deployment. Temporary preview/database resources are stopped after tests.

CI candidate has read-only GitHub permission, pinned actions, bounded timeouts,
no production secrets, development application fixtures and a frontend job.
D6 GitHub run37887690942 completed SUCCESS for backend-fixtures and frontend.
See https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/37887690942.
Browser/Timescale execution is local acceptance; this bounded workflow does not
claim those CI jobs exist. Later documentation PR checks are reported separately.

## NADI-D-INTEGRATION-01 revalidation after review correction

Final Cockpit610/Maximo181/PI191/contracts14 PASS,0FAIL/0SKIP in full runs.
All PostgreSQL fixture DSNs use explicit `postgresql+psycopg://`.
Cockpit uses `PYTHONPATH=.:tests:<testdeps>` plus managed config, Compose fixture
flag and NADI_APPLICATION_TEST_DSN /NADI_ENGINEERING_TEST_DSN /NADI_MART_TEST_DSN
pointing only to isolated loopback *_test stores; command unchanged above.
Targeted `python -m unittest test_session_cleanup -v` runs10new checks.
PI uses `PI_MIGRATION_TEST_DSN=postgresql+psycopg://<disposable fixture>` and
compatible local API dependencies; all11Timescale tests execute.
Browser command above repeated25PASS; real Next proxy negatives8PASS.
Frontend commands above repeated110PASS/typecheck/build/product safety.
Scoped corrected PR49 run37892980855 SUCCESS at c03e57c; includes session cleanup.
The600-count and old run IDs above remain historical pre-correction evidence.
Initial implicit-driver fixture failures were corrected, not counted as skips.
See [senior review and merge plan](nadi-d-integration-01.md).
