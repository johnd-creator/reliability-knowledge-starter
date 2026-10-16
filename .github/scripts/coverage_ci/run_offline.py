"""CI-owned adaptation of PR91's runner; all tests are discovered under guards.

Accidental-I/O defense, not a sandbox for malicious Python/native code. Use only
ephemeral CI runners with no plant credentials or private database configuration.
"""
import argparse
import contextlib
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import unittest
from unittest.mock import patch


def run(root, tested_sha, report_path,component):
    source=root.resolve()
    root=source/('reliability-cockpit' if component=='cockpit' else 'reliability-data-contracts')
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    run_url = os.environ.get("CI_RUN_URL", "LOCAL_OFFLINE")
    workflow_sha = os.environ.get("CI_WORKFLOW_SHA", "LOCAL_OFFLINE")
    for key in list(os.environ):
        if (key.startswith(("MAXIMO_", "PI_", "CEMS_", "DCS_", "PG", "NADI_", "RELIABILITY_", "COCKPIT_"))
                or key.endswith(("_DSN", "_TOKEN", "_PASSWORD", "_SECRET", "_KEY"))
                or key in ("DATABASE_URL", "DATABASE_ECHO", "GH_TOKEN")):
            os.environ.pop(key)
    os.environ["PYTHON_DOTENV_DISABLED"] = "1"
    os.environ["COCKPIT_CONFIG_MODE"] = "managed"
    if not root.is_dir():
        report_path.write_text(json.dumps(dict(component=component,tested_sha=tested_sha,tests=0,
            discovered=0,failures=0,errors=0,skips=0,blocked_external_io=0,
            infrastructure_error='MISSING_COMPONENT',conclusion='FAIL'))+'\n')
        return 1
    os.chdir(root)
    sys.path[:0] = [str(root), str(root / "tests")]
    blocked = []

    def deny(kind):
        # Never include addresses, DSNs, credential values or audit arguments.
        blocked.append(kind)
        raise AssertionError("UNEXPECTED_EXTERNAL_IO:" + kind)

    helper=(source/'pi-collector/tests/fixtures/condition_source.py').resolve()
    helper_hash="151bc63777c0a3a02befeab43c629808112affad1573dabab6a4ebb175fda02a"
    def audit(event, args):
        if event=='subprocess.Popen':
            import hashlib
            argv=args[1]
            if (isinstance(argv,list) and argv==[sys.executable,str(helper)]
                    and hashlib.sha256(helper.read_bytes()).hexdigest()==helper_hash):
                return  # Exact existing fake-HTTP fixture only, no arbitrary helper.

        if event in ("socket.connect", "socket.getaddrinfo", "socket.sendto",
                     "socket.sendmsg", "subprocess.Popen", "os.system"):
            deny(event)
        if event == "sqlite3.connect" and args[0] != ":memory:":
            deny("sqlite_file")

    sys.addaudithook(audit)
    result = None
    discovered = 0
    infrastructure_error = False
    try:
        # Install guards before importing source or discovering any tests.
        from sqlalchemy.engine import Engine
        import psycopg
        original = Engine.connect

        def connect(engine, *args, **kwargs):
            if (engine.url.get_backend_name() == "sqlite"
                    and engine.url.database in (None, "", ":memory:")):
                return original(engine, *args, **kwargs)
            return deny("external_database")

        with contextlib.ExitStack() as stack:
            stack.enter_context(patch("sqlalchemy.engine.Engine.connect", connect))
            stack.enter_context(patch.object(psycopg, "connect", lambda *a, **k: deny("psycopg")))
            for cls in (psycopg.Connection, psycopg.AsyncConnection):
                stack.enter_context(patch.object(cls, "connect", lambda *a, **k: deny("psycopg")))
            stack.enter_context(patch("dotenv.load_dotenv", return_value=False))
            stack.enter_context(patch("dotenv.main.load_dotenv", return_value=False))
            if component=='cockpit':
                names=['test_integration_status','test_integration_observations_client',
                       'test_integration_ui_contract','test_projection_coverage']
                suite=unittest.defaultTestLoader.loadTestsFromNames(names)
            else:
                suite=unittest.defaultTestLoader.discover(str(root/'tests'))
            discovered = suite.countTestCases()
            result = unittest.TextTestRunner(verbosity=2).run(suite)
    except Exception as error:
        infrastructure_error = True
        print("OFFLINE_INFRASTRUCTURE_ERROR:" + type(error).__name__, file=sys.stderr)
    success = bool(result is not None and result.wasSuccessful() and discovered > 0
                   and result.testsRun == discovered and not result.skipped
                   and not result.expectedFailures and not blocked and not infrastructure_error)
    data = {
        "component":component,"python": platform.python_version(), "tested_sha": tested_sha,
        "workflow_sha": workflow_sha, "run_url": run_url,
        "command": shlex.join([sys.executable, *sys.argv]),
        "discovered": discovered, "tests": result.testsRun if result else 0,
        "failures": len(result.failures) if result else 0,
        "errors": len(result.errors) if result else 0,
        "skips": len(result.skipped) if result else 0,
        "expected_failures": len(result.expectedFailures) if result else 0,
        "blocked_external_io": len(blocked), "blocked_io_kinds": sorted(set(blocked)),
        "infrastructure_error": infrastructure_error, "conclusion": "PASS" if success else "FAIL",
    }
    report_path.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data))
    if summary:
        with open(summary, "a") as output:
            output.write("## B4 component qualification\n\n```json\n"
                         + json.dumps(data, indent=2) + "\n```\n")
    return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--component",choices=("cockpit","contracts"),required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not __import__("re").fullmatch(r"[0-9a-f]{40}", args.sha):
        parser.error("--sha must be a full commit SHA")
    sys.exit(run(args.root, args.sha, args.report.resolve(),args.component))
