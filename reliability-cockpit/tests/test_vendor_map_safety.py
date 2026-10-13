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
        for duration in [0,59,181,600,5700,7200]:
            with self.assertRaises(ValueError):module.bounded_seconds(duration)
        self.assertEqual(module.bounded_seconds(180),180)
        text=(ROOT/'deploy/development/vendor-maps/run.py').read_text()
        self.assertIn('--max-old-space-size=4096',text)
        self.assertIn('MemoryMax=6144M',text)
