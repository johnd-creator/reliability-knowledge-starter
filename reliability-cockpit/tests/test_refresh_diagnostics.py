"""Private diagnostics preserve evidence and reject arbitrary process metadata."""
import hashlib, io, json, tempfile, unittest
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import Mock, patch
from src.services.condition_refresh import CollectorLauncherSource, RefreshError, SourceHandoff, private_write
from src.domain.condition_evidence import EvidenceBatch
from src.cli import cmd_condition_refresh, parse_args
import test_condition_refresh as refresh_fixture

class RefreshDiagnosticsTest(unittest.TestCase):
    approve = refresh_fixture.RefreshTest.approve
    reader = refresh_fixture.RefreshTest.reader
    source_document = refresh_fixture.RefreshTest.source_document
    project = refresh_fixture.RefreshTest.project
    setUp = refresh_fixture.RefreshTest.setUp
    tearDown = refresh_fixture.RefreshTest.tearDown
    runner = refresh_fixture.RefreshTest.runner
    execute = refresh_fixture.RefreshTest.execute
    snapshot = refresh_fixture.RefreshTest.snapshot

    def test_failure_code_journal_and_preservation(self):
        old = self.snapshot()
        self.document['results'][0].update(status='SOURCE_UNAVAILABLE', evidence=None)
        self.source.collect.side_effect = lambda *a: SourceHandoff(EvidenceBatch.model_validate(self.document), 1, 'SOURCE_TLS_FAILED')
        r = self.runner()
        with patch.object(self.store, 'project', wraps=self.store.project) as writer:
            with self.assertRaises(RefreshError) as c:
                self.execute(r)
            writer.assert_not_called()
        self.assertEqual(c.exception.reason, 'SOURCE_UNAVAILABLE')
        self.assertEqual(c.exception.source_failure_code, 'SOURCE_TLS_FAILED')
        self.assertEqual(r.journal()[-1]['source_failure_code'], 'SOURCE_TLS_FAILED')
        self.assertEqual(r.journal()[-1]['source_gets'], 1)
        self.assertFalse(any((x['event'] == 'WRITER_STARTED' for x in r.journal())))
        self.assertEqual(old, self.snapshot())
        self.assertFalse(r.pending_writes())
        with self.assertRaisesRegex(RefreshError, 'DUPLICATE_ATTEMPT'):
            self.execute(r)
        self.assertEqual(self.source.collect.call_count, 1)

    def test_legacy_failure_unknown(self):
        self.document['results'][0].update(status='SOURCE_UNAVAILABLE', evidence=None)
        self.source.collect.side_effect = lambda *a: SourceHandoff(EvidenceBatch.model_validate(self.document), 1)
        with self.assertRaises(RefreshError) as c:
            self.execute()
        self.assertEqual(c.exception.source_failure_code, 'SOURCE_CAUSE_UNKNOWN')

    def test_cli_typed_code_only(self):
        args = parse_args(['condition', 'refresh', '--state-directory', 'unused', '--baseline-file', 'unused', '--baseline-sha256', 'a' * 64, '--attempt-id', 'synthetic'])
        fake = Mock()
        fake.run.side_effect = RefreshError('SOURCE_UNAVAILABLE', source_failure_code='SOURCE_AUTH_FAILED')
        out = io.StringIO()
        with patch('src.repositories.condition_store.ConditionCommandStore.from_environment', return_value=Mock()), patch('src.services.condition_refresh.ConditionRefreshRunner', return_value=fake), redirect_stdout(out):
            self.assertEqual(cmd_condition_refresh(args), 2)
        self.assertEqual(json.loads(out.getvalue()), {'status': 'FAILED', 'reason': 'SOURCE_UNAVAILABLE', 'source_failure_code': 'SOURCE_AUTH_FAILED'})
        self.assertIsNone(RefreshError('SOURCE_UNAVAILABLE', source_failure_code='https://private.invalid/secret').source_failure_code)

class ReceiptDiagnosticsTest(unittest.TestCase):

    def collect(self, failures, version='1.1'):
        from test_condition_evidence import ConditionProjectionTest
        f = ConditionProjectionTest()
        f.setUp()
        try:
            document = f.source_document({'motor_current': {'unavailable': True}})
        finally:
            f.tearDown()
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            launcher = d / 'launcher'
            launcher.write_text('#!/bin/sh\nexit 0\n')
            launcher.chmod(448)
            raw = json.dumps(document)
            private_write(d / 'handoff.json', raw)
            receipt = {'contract_version': version, 'source_gets': 1, 'max_source_gets': 5, 'handoff_sha256': hashlib.sha256(raw.encode()).hexdigest()}
            if version == '1.1':
                receipt['source_failures'] = failures
            private_write(d / 'receipt.json', json.dumps(receipt))
            process = Mock()
            process.wait.return_value = 0
            process.__enter__ = Mock(return_value=process)
            process.__exit__ = Mock(return_value=False)
            source = CollectorLauncherSource(launcher, hashlib.sha256(launcher.read_bytes()).hexdigest())
            with patch('src.services.condition_refresh.subprocess.Popen', return_value=process) as child:
                result = source.collect(EvidenceBatch.model_validate(document).plan, d, 0)
                self.assertEqual(child.call_count, 1)
                self.assertIn('--diagnostics', child.call_args.args[0])
                self.assertEqual(child.call_args.kwargs['env'], {'PATH': '/usr/bin:/bin', 'PI_CONFIG_MODE': 'managed'})
                return result

    def test_valid_and_legacy_receipts(self):
        self.assertEqual(self.collect([{'signal_id': 'synthetic-current', 'code': 'SOURCE_TIMEOUT'}]).source_failure_code, 'SOURCE_TIMEOUT')
        self.assertIsNone(self.collect(None, '1.0').source_failure_code)

    def test_untrusted_metadata_rejected(self):
        for f in [[{'signal_id': 'synthetic-current', 'code': 'https://private.invalid/secret'}], [{'signal_id': 'wrong', 'code': 'SOURCE_TLS_FAILED'}], [], [{'signal_id': 'synthetic-current', 'code': 'SOURCE_TLS_FAILED', 'secret': 'never'}], [{'signal_id': 'synthetic-current', 'code': {}}]]:
            with self.subTest(f=f), self.assertRaisesRegex(RefreshError, 'SOURCE_DIAGNOSTICS_INVALID'):
                self.collect(f)
