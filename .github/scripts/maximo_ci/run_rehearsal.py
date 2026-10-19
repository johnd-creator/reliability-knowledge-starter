"""Private-file rehearsal qualification; standard offline runner stays memory-only.

Accidental-I/O defense, not a sandbox for malicious Python/native code. Run only
on ephemeral CI without plant credentials. Only a new runner-owned0700 directory
can contain SQLite files; no network, subprocess, external DB or ATTACH is allowed.
"""
import argparse
import contextlib
import json
import os
from pathlib import Path
import platform
import shlex
import sqlite3
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

EXPECTED = frozenset('test_f03_local_rehearsal.F03LocalRehearsalTest.' + name for name in (
    'test_interruption_records_failure_without_advancing_success_or_source_cursor',
    'test_first_failure_has_no_invented_success_or_watermark',
    'test_private_separate_restore_roundtrips_all_fixture_tables_and_cursors',
    'test_existing_restore_target_and_corrupt_backup_are_refused',
    'test_missing_dependency_requires_full_reconciliation_on_legacy_projector',
    'test_failure_journal_error_does_not_mask_original_projection_error',
))


def private_sqlite(value, owned):
    """Reject ambiguity, URI options and escaped paths before SQLite opens a file."""
    if value == ':memory:':
        return True
    try:
        value = os.fspath(value)
        if not isinstance(value, str):
            return False
        if value.startswith('file:'):
            uri = urlsplit(value)
            if uri.scheme != 'file' or uri.netloc or uri.query != 'mode=ro' or uri.fragment:
                return False
            value = unquote(uri.path, errors='strict')
        if '\0' in value:
            return False
        target = Path(value)
        if not target.is_absolute() or '..' in target.parts or target == owned:
            return False
        if not target.resolve().is_relative_to(owned):
            return False
        return not any(p.is_symlink() for p in (target, *target.parents) if p != owned and p.is_relative_to(owned))
    except (ValueError, TypeError, OSError):
        return False


def test_ids(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from test_ids(item)
        else:
            yield item.id()


def run(root, tested_sha, report_path):
    root = root.resolve()
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    run_url = os.environ.get('CI_RUN_URL', 'LOCAL_REHEARSAL')
    workflow_sha = os.environ.get('CI_WORKFLOW_SHA', 'LOCAL_REHEARSAL')
    for key in list(os.environ):
        if (key.startswith(('MAXIMO_', 'PG', 'NADI_', 'RELIABILITY_', 'COCKPIT_'))
                or key.endswith(('_DSN', '_TOKEN', '_PASSWORD', '_SECRET'))
                or key in ('DATABASE_URL', 'DATABASE_ECHO', 'GH_TOKEN')):
            os.environ.pop(key)
    os.environ['PYTHON_DOTENV_DISABLED'] = '1'
    os.chdir(root)
    sys.path[:0] = [str(root), str(root / 'rehearsals')]
    blocked = []
    result = None
    ids = []
    infrastructure_error = False

    def deny(kind):
        blocked.append(kind)
        raise AssertionError('UNEXPECTED_EXTERNAL_IO:' + kind)

    with tempfile.TemporaryDirectory(prefix='nadi-ci-rehearsal-') as temporary:
        owned = Path(temporary).resolve()
        owned.chmod(0o700)
        os.environ['NADI_REHEARSAL_ROOT'] = str(owned)

        def authorize(action, *_):
            if action == sqlite3.SQLITE_ATTACH:
                blocked.append('sqlite_attach')
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        opening = threading.local()

        def audit(event, args):
            if event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto',
                         'socket.sendmsg', 'subprocess.Popen', 'os.system'):
                deny(event)
            if event == 'sqlite3.connect':
                if not getattr(opening, 'allowed', False):
                    deny('sqlite_unwrapped')
                if not private_sqlite(args[0], owned):
                    deny('sqlite_file')

        sys.addaudithook(audit)
        try:
            from sqlalchemy.engine import Engine
            import psycopg
            original = Engine.connect
            original_sqlite_connect = sqlite3.connect

            def sqlite_connect(*args, **kwargs):
                try:
                    value = os.fspath(args[0] if args else kwargs.get('database'))
                except TypeError:
                    return deny('sqlite_target')
                uri = args[7] if len(args) > 7 else kwargs.get('uri', False)
                if isinstance(value, str) and value.startswith('file:') and uri is not True:
                    return deny('sqlite_uri_mode')
                previous = getattr(opening, 'allowed', False)
                opening.allowed = True
                try:
                    connection = original_sqlite_connect(*args, **kwargs)
                finally:
                    opening.allowed = previous
                connection.set_authorizer(authorize)
                return connection

            def connect(engine, *args, **kwargs):
                if (engine.url.get_backend_name() == 'sqlite'
                        and (engine.url.database in (None, '', ':memory:')
                             or private_sqlite(engine.url.database, owned))):
                    return original(engine, *args, **kwargs)
                return deny('external_database')

            with contextlib.ExitStack() as stack:
                stack.enter_context(patch('sqlalchemy.engine.Engine.connect', connect))
                for module in ('sqlite3', 'sqlite3.dbapi2', '_sqlite3'):
                    stack.enter_context(patch(module + '.connect', sqlite_connect))
                stack.enter_context(patch.object(psycopg, 'connect', lambda *a, **k: deny('psycopg')))
                for cls in (psycopg.Connection, psycopg.AsyncConnection):
                    stack.enter_context(patch.object(cls, 'connect', lambda *a, **k: deny('psycopg')))
                stack.enter_context(patch('dotenv.load_dotenv', return_value=False))
                stack.enter_context(patch('dotenv.main.load_dotenv', return_value=False))
                suite = unittest.defaultTestLoader.discover(str(root / 'rehearsals'))
                ids = list(test_ids(suite))
                if len(ids) != len(EXPECTED) or frozenset(ids) != EXPECTED:
                    raise ValueError('REHEARSAL_TEST_COVERAGE_MISMATCH')
                result = unittest.TextTestRunner(verbosity=2).run(suite)
        except Exception as error:
            infrastructure_error = True
            print('REHEARSAL_INFRASTRUCTURE_ERROR:' + type(error).__name__, file=sys.stderr)
        finally:
            os.environ.pop('NADI_REHEARSAL_ROOT', None)
    success = bool(result is not None and result.wasSuccessful()
                   and result.testsRun == len(EXPECTED) and not result.skipped
                   and not result.expectedFailures and not blocked and not infrastructure_error)
    data = {
        'python': platform.python_version(), 'tested_sha': tested_sha,
        'workflow_sha': workflow_sha, 'run_url': run_url,
        'command': shlex.join([sys.executable, *sys.argv]),
        'test_ids': ids, 'discovered': len(ids), 'tests': result.testsRun if result else 0,
        'failures': len(result.failures) if result else 0,
        'errors': len(result.errors) if result else 0,
        'skips': len(result.skipped) if result else 0,
        'expected_failures': len(result.expectedFailures) if result else 0,
        'blocked_external_io': len(blocked), 'blocked_io_kinds': sorted(set(blocked)),
        'infrastructure_error': infrastructure_error, 'owned_root_removed': not owned.exists(),
        'conclusion': 'PASS' if success else 'FAIL',
    }
    report_path.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data))
    if summary:
        with open(summary, 'a') as output:
            output.write('## Maximo private-file rehearsal qualification\n\n```json\n'
                         + json.dumps(data, indent=2) + '\n```\n')
    return 0 if success else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--sha', required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if not __import__('re').fullmatch(r'[0-9a-f]{40}', args.sha):
        parser.error('--sha must be a full commit SHA')
    sys.exit(run(args.root, args.sha, args.report.resolve()))
