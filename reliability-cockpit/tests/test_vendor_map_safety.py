"""Hermetic FIX-06 controller confinement and exact source rejection."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
import os
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('vendor_run', ROOT/'deploy/development/vendor-maps/run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class VendorMapSafety(unittest.TestCase):
    def test_output_confinement(self):
        for value in ['relative', '/tmp/other', '/tmp/nadi-fix06-private/../escape', '/tmp/nadi-fix06-private']:
            with self.subTest(value=value), self.assertRaises(ValueError): module.private_output(value)
        with patch.object(Path, "exists", return_value=False), self.assertRaises(ValueError):
            module.private_output("/tmp/nadi-fix06-private")
    def test_source_and_staged_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); file=root/'reliability-cockpit/web/components/DevelopmentStatus.tsx'
            file.parent.mkdir(parents=True);file.write_text('<span>DEV</span>')
            def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
            git('init','-q');git('add','.');git('-c','user.name=Test','-c','user.email=test@invalid','commit','-qm','Fixture')
            sha=git('rev-parse','HEAD');module.verify_source(root,sha)
            file.write_text('<span>DEV PROBE 25</span>');module.verify_source(root,sha)
            git('add','.');
            with self.assertRaises(RuntimeError):module.verify_source(root,sha)
            git('restore','--staged',file.relative_to(root).as_posix());file.write_text('<span>other</span>')
            with self.assertRaises(RuntimeError):module.verify_source(root,sha)
            file.write_text('<span>DEV</span>');(root/'.env').write_text('SYNTHETIC_ONLY=1')
            with self.assertRaises(RuntimeError):module.verify_source(root,sha)
    def test_private_process_evidence(self):
        record=module.process_evidence(os.getpid())
        self.assertEqual(record['pid'],os.getpid())
        self.assertEqual(record['parent'],os.getppid())
        self.assertTrue(record['start_ticks'].isdigit())
        self.assertEqual(len(record['command_sha256']),64)
        self.assertNotIn('command',record)
        self.assertTrue(module.process_evidence(99999999)['unverified_or_vanished'])
    def test_no_official_adapter_installation(self):
        for file in ['reliability-cockpit/web/next.config.js','deploy/development/nadi-dev.py','deploy/development/frontend_preview.py']:
            self.assertNotIn('vendor-maps/adapter', (ROOT/file).read_text())

    def test_fast_duration_and_memory_policy(self):
        for duration in [0,59,121,180,600,5700,7200]:
            with self.assertRaises(ValueError):module.bounded_seconds(duration)
        self.assertEqual(module.bounded_seconds(120),120)
        text=(ROOT/'deploy/development/vendor-maps/run.py').read_text()
        self.assertIn('--max-old-space-size=4096',text)
        self.assertIn('MemoryMax=6144M',text)

    def test_browser_and_attestation_outcomes_are_independent(self):
        passed=dict(completed=True,counts=dict(navigations=2),errors=[])
        result=module.separate_outcome('UNREADABLE_PROCESS_EVIDENCE','TRANSIENT_MEMBERSHIP_UNVERIFIED',passed)
        self.assertEqual(result['browser_functional']['status'],'PASS')
        self.assertEqual(result['process_attestation']['status'],'BLOCKED')
        self.assertEqual(result['overall'],'BLOCKED')
        self.assertFalse(result['application_crash_established'])
        cancelled=dict(completed=False,failure='Target page, context or browser has been closed',errors=[])
        result=module.separate_outcome('UNREADABLE_PROCESS_EVIDENCE','TRANSIENT_MEMBERSHIP_UNVERIFIED',cancelled)
        self.assertEqual(result['browser_functional']['status'],'INCOMPLETE_INTERRUPTED_BY_ATTESTATION')
        self.assertEqual(module.separate_outcome(None,None,passed)['overall'],'PASS')
    def test_actual_browser_assertion_failure_is_preserved(self):
        result=module.separate_outcome('UNREADABLE_PROCESS_EVIDENCE','UNREADABLE_APPROVED_PROCESS',dict(completed=False,errors=['Fixture assertion failed']))
        self.assertEqual(result['browser_functional']['status'],'FAIL_BROWSER_ASSERTIONS')
        self.assertEqual(result['overall'],'BLOCKED')

    def test_independent_browser_failure_is_not_hidden_by_attestation(self):
        browser=dict(completed=False,failure='Fixture locator timeout',errors=[])
        result=module.separate_outcome('UNREADABLE_PROCESS_EVIDENCE','TRANSIENT_MEMBERSHIP_UNVERIFIED',browser)
        self.assertEqual(result['browser_functional']['status'],'FAIL_BROWSER_CHECK')
        self.assertEqual(result['browser_functional']['reason'],'Fixture locator timeout')
        result=module.separate_outcome('BROWSER_FAILURE',None,browser)
        self.assertEqual(result['process_attestation']['status'],'VERIFIED_OBSERVED_INTERVAL')
        self.assertEqual(result['overall'],'BLOCKED')
