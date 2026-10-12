"""Hermetic confinement checks; no DB, service controller or source request."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('heap_probe',ROOT/'deploy/development/probes/run.py')
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
summary_spec=importlib.util.spec_from_file_location('heap_summary',ROOT/'deploy/development/probes/summarize.py')
summary=importlib.util.module_from_spec(summary_spec);summary_spec.loader.exec_module(summary)

class ProbeConfinementTest(unittest.TestCase):
    def test_live_and_repository_paths_are_refused(self):
        for path in [str(ROOT/'.nadi-dev/new'),'/home/john-d/.nadi-dev/new','/tmp/elsewhere/new','relative','/tmp/nadi-fix04-private/../escape']:
            with self.subTest(path=path),self.assertRaises(ValueError):probe.validate_output(path)

    def test_existing_directory_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):probe.validate_output(directory)

    def test_existing_symlink_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            link=Path(directory)/'link';link.symlink_to('/tmp')
            with self.assertRaises(ValueError):probe.validate_output(str(link))

    def test_new_private_leaf_is_allowed(self):
        self.assertEqual(probe.validate_output('/tmp/nadi-fix04-private/never-created-unit-test-leaf'),Path('/tmp/nadi-fix04-private/never-created-unit-test-leaf'))

    def test_compiled_function_ids_cannot_expose_private_paths(self):
        for name in ['(ssr)/../../home/private-owner/project',r'(ssr)C:\Users\private-owner\project','file:///private/worktree/module','webpack://private-owner/module']:
            with self.subTest(name=name):
                self.assertEqual(summary.public_function_name(name),'(compiled module)')

    def test_public_function_names_are_bounded(self):
        self.assertEqual(summary.public_function_name('defaultLoadImpl'),'defaultLoadImpl')
        self.assertEqual(summary.public_function_name(''),'(anonymous)')
        self.assertEqual(len(summary.public_function_name('x'*1000)),80)

if __name__=='__main__':unittest.main()
