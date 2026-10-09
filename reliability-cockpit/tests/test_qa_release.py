import copy, tempfile, unittest
from pathlib import Path
from hashlib import sha256
from src.qa.release import verify_release


class QaReleaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/"src").mkdir();(self.root/"application-migrations").mkdir()
        for name,content in {"src/a.py":"fixture-code","application-migrations/002.sql":"SELECT 1",
                             "pyproject.toml":"fixture-package"}.items():
            (self.root/name).write_text(content)
        self.manifest={"schema_version":"1.0","source_sha":"a"*40,
            "files":{name:sha256((self.root/name).read_bytes()).hexdigest()
                     for name in ("src/a.py","application-migrations/002.sql","pyproject.toml")}}
    def tearDown(self):self.tmp.cleanup()
    def test_exact_artifact_integrity(self):
        self.assertEqual(verify_release(self.manifest,self.root),"a"*40)
    def test_tamper_and_extra_code_rejected(self):
        (self.root/"src/a.py").write_text("modified")
        with self.assertRaises(ValueError):verify_release(self.manifest,self.root)
        (self.root/"src/extra.py").write_text("untracked")
        with self.assertRaises(ValueError):verify_release(self.manifest,self.root)
    def test_missing_files_invalid_sha_and_symlink_rejected(self):
        for change in [{"source_sha":"not-a-sha"},{"schema_version":"0"},{"extra":"unexpected"}]:
            manifest={**self.manifest,**change}
            with self.assertRaises(ValueError):verify_release(manifest,self.root)
        (self.root/"src/a.py").unlink();(self.root/"src/a.py").symlink_to("/etc/hosts")
        with self.assertRaises(ValueError):verify_release(self.manifest,self.root)
