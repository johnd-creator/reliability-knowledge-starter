"""Hermetic FIX-06 controller confinement and exact source rejection."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('vendor_run', ROOT/'deploy/development/vendor-maps/run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class VendorMapSafety(unittest.TestCase):
    def test_output_confinement(self):
        for value in ['relative', '/tmp/other', '/tmp/nadi-fix06-private/../escape', '/tmp/nadi-fix06-private']:
            with self.subTest(value=value), self.assertRaises(ValueError): module.private_output(value)
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
    def test_no_official_adapter_installation(self):
        for file in ['reliability-cockpit/web/next.config.js','deploy/development/nadi-dev.py','deploy/development/frontend_preview.py']:
            self.assertNotIn('vendor-maps/adapter', (ROOT/file).read_text())
