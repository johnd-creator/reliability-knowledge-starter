"""Guarded rehearsal boundary tests; all external candidates are synthetic files."""
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch
import yaml

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rehearsal_runner', TOOLS / 'run_rehearsal.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
HEAD = '8bb1bcb2c485feeb792235c64b5aef6bbce5e3cc'


class RehearsalRunnerTest(unittest.TestCase):
    def invoke(self, body='pass', *, empty=False, skip=False):
        with tempfile.TemporaryDirectory(prefix='nadi-rehearsal-guard-test-') as temporary:
            root = Path(temporary)
            (root / 'rehearsals').mkdir()
            outside = root / 'outside.sqlite'
            with sqlite3.connect(outside) as c:
                c.execute('CREATE TABLE canary (value text)')
                c.execute("INSERT INTO canary VALUES ('unchanged')")
            before = outside.read_bytes()
            if not empty:
                source = 'import unittest, os, sqlite3, tempfile\nfrom pathlib import Path\nclass F03LocalRehearsalTest(unittest.TestCase):\n'
                for index, identity in enumerate(sorted(r.EXPECTED)):
                    name = identity.rsplit('.', 1)[-1]
                    if index == 0 and skip:
                        source += '    @unittest.skip("synthetic")\n'
                    source += '    def ' + name + '(self):\n' + textwrap.indent(body if index == 0 else 'pass', '        ') + '\n'
                (root / 'rehearsals/test_f03_local_rehearsal.py').write_text(source)
            env = {k: v for k, v in os.environ.items() if k not in ('GITHUB_STEP_SUMMARY', 'GH_TOKEN')}
            env['TEST_OUTSIDE_SQLITE'] = str(outside)
            report = root / 'report.json'
            process = subprocess.run([sys.executable, str(TOOLS / 'run_rehearsal.py'),
                '--root', str(root), '--sha', HEAD, '--report', str(report)],
                env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(outside.read_bytes(), before)
            return process.returncode, json.loads(report.read_text())

    def test_real_owned_file_backup_and_cleanup(self):
        code, report = self.invoke('''\
owned=Path(os.environ['NADI_REHEARSAL_ROOT'])
self.assertEqual(owned.stat().st_mode & 0o777, 0o700)
with tempfile.TemporaryDirectory(dir=owned) as temporary:
    source=Path(temporary)/'source.sqlite'
    with sqlite3.connect(source) as c:
        c.execute('CREATE TABLE sample (value integer)')
        c.execute('INSERT INTO sample VALUES (7)')
    with sqlite3.connect(source.as_uri()+'?mode=ro', uri=True) as c, sqlite3.connect(Path(temporary)/'copy.sqlite') as d:
        c.backup(d)
        self.assertEqual(d.execute('SELECT value FROM sample').fetchone(), (7,))''')
        self.assertEqual(code, 0)
        self.assertEqual((report['tests'], report['discovered'], report['blocked_external_io']), (6, 6, 0))
        self.assertTrue(report['owned_root_removed'])

    def test_caught_external_paths_uri_and_symlink_still_fail(self):
        cases = [
            "sqlite3.connect(os.environ['TEST_OUTSIDE_SQLITE'])",
            "sqlite3.connect(Path(os.environ['TEST_OUTSIDE_SQLITE']).as_uri()+'?mode=ro',uri=True)",
            "sqlite3.connect(str(Path(os.environ['NADI_REHEARSAL_ROOT'])/'..'/'not-allowed.sqlite'))",
            "sqlite3.connect((Path(os.environ['NADI_REHEARSAL_ROOT'])/'..'/'not-allowed.sqlite').as_uri()+'?mode=ro',uri=True)",
            "sqlite3.connect((Path(os.environ['NADI_REHEARSAL_ROOT'])/'new.sqlite').as_uri()+'?mode=ro&vfs=unix-none',uri=True)",
            "sqlite3.connect((Path(os.environ['NADI_REHEARSAL_ROOT'])/'new.sqlite').as_uri()+'?mode=ro',uri=False)",
            "sqlite3.connect((Path(os.environ['NADI_REHEARSAL_ROOT'])/'new.sqlite').as_uri()+'?mode=ro')",
            "sqlite3.connect(Path(os.environ['NADI_REHEARSAL_ROOT']).as_uri()+'/new%00.sqlite?mode=ro',uri=True)",
            "sqlite3.connect(Path((Path(os.environ['NADI_REHEARSAL_ROOT'])/'new.sqlite').as_uri()+'?mode=ro'),uri=False)",
            "sqlite3.connect('relative.sqlite')",
            "sqlite3.connect('file://elsewhere/database.sqlite?mode=ro',uri=True)",
            "Path(os.environ['NADI_REHEARSAL_ROOT'],'link.sqlite').symlink_to(os.environ['TEST_OUTSIDE_SQLITE']); sqlite3.connect(str(Path(os.environ['NADI_REHEARSAL_ROOT'],'link.sqlite')))",
            "os.environ['NADI_REHEARSAL_ROOT']=str(Path(os.environ['TEST_OUTSIDE_SQLITE']).parent); sqlite3.connect(os.environ['TEST_OUTSIDE_SQLITE'])",
        ]
        for operation in cases:
            with self.subTest(operation=operation):
                code, report = self.invoke('try:\n    '+operation+'\nexcept Exception:\n    pass')
                self.assertEqual(code, 1)
                self.assertGreater(report['blocked_external_io'], 0)
                self.assertTrue(report['owned_root_removed'])

    def test_attach_and_unwrapped_connection_fail_closed(self):
        for operation in (
            "sqlite3.connect(':memory:').execute('ATTACH DATABASE ? AS forbidden', (os.environ['TEST_OUTSIDE_SQLITE'],))",
            "sqlite3.connect(':memory:').execute('ATTACH DATABASE ? AS forbidden', (str(Path(os.environ['NADI_REHEARSAL_ROOT'])/'attach.sqlite'),))",
            "sqlite3.Connection(':memory:')",
        ):
            with self.subTest(operation=operation):
                code, report = self.invoke('try:\n    '+operation+'\nexcept Exception:\n    pass')
                self.assertEqual(code, 1)
                self.assertGreater(report['blocked_external_io'], 0)

    def test_network_subprocess_and_other_databases_remain_blocked(self):
        for imports, operation in (
            ('import socket', "socket.create_connection(('192.0.2.1',9))"),
            ('import subprocess', "subprocess.run(['true'])"),
            ('import psycopg', "psycopg.connect('host=192.0.2.1 dbname=synthetic')"),
            ('from sqlalchemy import create_engine', "create_engine('postgresql+psycopg://x:x@192.0.2.1/x').connect()"),
        ):
            with self.subTest(operation=operation):
                code, report = self.invoke(imports+'\ntry:\n    '+operation+'\nexcept Exception:\n    pass')
                self.assertEqual(code, 1)
                self.assertGreater(report['blocked_external_io'], 0)

    def test_sqlalchemy_private_file_and_memory_allowed(self):
        code, report = self.invoke('''\
from sqlalchemy import create_engine, text
path=Path(os.environ['NADI_REHEARSAL_ROOT'])/'owned.sqlite'
for url in ('sqlite://', 'sqlite:///'+str(path)):
    with create_engine(url).begin() as c:
        self.assertEqual(c.scalar(text('SELECT 1')),1)''')
        self.assertEqual((code,report['blocked_external_io']), (0,0))

    def test_failed_skipped_or_missing_coverage_cannot_pass(self):
        for options in ({'body': "self.fail('synthetic')"}, {'skip': True}, {'empty': True}):
            with self.subTest(options=options):
                code, report = self.invoke(**options)
                self.assertEqual(code, 1)
                self.assertEqual(report['conclusion'], 'FAIL')

    def test_environment_scrub_and_dotenv_guard(self):
        with patch.dict(os.environ, {'MAXIMO_PASSWORD':'synthetic', 'DATABASE_URL':'synthetic', 'PGHOST':'synthetic', 'NADI_REHEARSAL_ROOT':'/not-an-allowed-input'}):
            code, report = self.invoke('''\
from dotenv import load_dotenv
load_dotenv()
for name in ('MAXIMO_PASSWORD','DATABASE_URL','PGHOST'):
    self.assertNotIn(name,os.environ)
self.assertNotEqual(os.environ['NADI_REHEARSAL_ROOT'],'/not-an-allowed-input')''')
        self.assertEqual((code,report['conclusion']), (0,'PASS'))

    def test_workflow_requires_both_suites_at_same_selected_sha(self):
        workflow=yaml.load((TOOLS.parents[1]/'workflows/nadi-maximo-collector.yml').read_text(),Loader=yaml.BaseLoader)
        collector=workflow['jobs']['collector']
        steps=[s for s in collector['steps'] if 'run_offline.py' in s.get('run','') or 'run_rehearsal.py' in s.get('run','')]
        self.assertEqual(len(steps),2)
        for step in steps:
            self.assertEqual(step['env']['TESTED_SHA'],'${{ needs.select.outputs.sha }}')
            self.assertNotIn('continue-on-error',step)
            self.assertNotIn('if',step)
            self.assertIn('ci-tools/.github/scripts/maximo_ci/',step['run'])
        self.assertIn('collector',workflow['jobs']['gate']['needs'])
