import os, subprocess, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from sqlalchemy import select
import test_attachments as fixtures
from src.domain.engineering import EngineeringError
from src.services.attachments import AttachmentRow, AttachmentAudit, DisposableFileStorage
from src.services.attachment_recovery import RetentionPolicy, reconcile_attachments, attachment_response
from src.api.private_attachments import build_attachment_delivery_router


class AttachmentReadinessTest(fixtures.AttachmentTest):
    def test_scanner_outage_is_quarantined(self):
        def unavailable(*args):
            raise RuntimeError("sensitive internal scanner URL")
        self.service.scanner = unavailable
        row = self.upload()
        self.assertEqual(row.scan_status, "QUARANTINED")
        with self.assertRaises(EngineeringError) as error:
            self.service.retrieve(self.actor, row.attachment_id)
        self.assertEqual(error.exception.code, "ATTACHMENT_QUARANTINED")

    def test_atomic_publish_never_overwrites_and_has_no_stage(self):
        key = "a"*32
        self.storage.put(key, b"original")
        with self.assertRaises(FileExistsError):
            self.storage.put(key, b"replacement")
        self.assertEqual(self.storage.get(key), b"original")
        self.assertEqual(list(self.storage.root.glob(".stage-*")), [])

    def test_size_first_and_symlink_denial(self):
        row = self.upload()
        self.storage.path(row.attachment_id).write_bytes(b"x"*101)
        with self.assertRaises(EngineeringError):
            self.storage.get_bounded(row.attachment_id, 100)
        self.storage.discard(row.attachment_id)
        self.storage.path(row.attachment_id).symlink_to("/etc/hosts")
        with self.assertRaises(Exception):
            self.service.retrieve(self.actor, row.attachment_id)
        link = self.storage.root / "root-link"
        link.symlink_to(self.storage.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            DisposableFileStorage(link)

    def test_explicit_quota_and_failed_metadata_cleanup(self):
        self.service.asset_quota_bytes = 20
        row = self.upload()
        with self.assertRaises(EngineeringError) as error:
            self.upload()
        self.assertEqual(error.exception.code, "ATTACHMENT_QUOTA_EXCEEDED")
        self.assertEqual([p.name for p in self.storage.root.iterdir()], [row.attachment_id])
        with self.engine.connect() as c:
            self.assertEqual(len(c.execute(select(AttachmentRow)).all()), 1)

    def test_read_only_reconciliation_missing_corrupt_orphan(self):
        policy = RetentionPolicy(30, 1, "fixture-approval")
        row = self.upload()
        self.storage.discard(row.attachment_id)
        key = "b"*32
        self.storage.put(key, b"private orphan")
        before = list(self.storage.root.iterdir())
        from src.repositories.application_boundary import ApplicationStore
        report = reconcile_attachments(
            ApplicationStore(self.engine, expected_database="attachments_test", isolated=True),
            self.storage, policy=policy, now=datetime.now(timezone.utc)+timedelta(seconds=2))
        self.assertEqual({r["code"] for r in report["findings"]}, {"FILE_MISSING", "ORPHAN_REVIEW_REQUIRED"})
        self.assertEqual(before, list(self.storage.root.iterdir()))
        self.assertEqual(report["automatic_deletions"], 0)

    def test_child_process_crash_orphan_is_not_deliverable(self):
        key = "c"*32
        code = ("import os; from src.services.attachments import DisposableFileStorage; "
                "s=DisposableFileStorage(" + repr(self.tmp.name) + "); "
                "s.put(" + repr(key) + ",b'%PDF-private'); os._exit(7)")
        result = subprocess.run([sys.executable, "-c", code], check=False,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 7)
        self.assertTrue(self.storage.path(key).exists())
        with self.assertRaises(EngineeringError) as error:
            self.service.retrieve(self.actor, key)
        self.assertEqual(error.exception.code, "NOT_FOUND")

    def test_retention_requires_approval_and_preserves_referenced_history(self):
        now = datetime.now(timezone.utc)
        policy = RetentionPolicy(1, 10, "fixture-approval", legal_hold=False)
        self.assertEqual(policy.decision(created_at=now-timedelta(days=2), now=now, referenced=True), "PRESERVE")
        self.assertEqual(policy.decision(created_at=now-timedelta(days=2), now=now, referenced=False), "REVIEW_DELETE")
        self.assertEqual(RetentionPolicy(1, 10, "fixture").decision(
            created_at=now-timedelta(days=2), now=now, referenced=False), "PRESERVE")
        with self.assertRaises(ValueError):
            RetentionPolicy(1, 10, "")

    def test_delivery_headers_and_trusted_default_off(self):
        row = self.upload()
        metadata, data = self.service.retrieve(self.actor, row.attachment_id)
        response = attachment_response(metadata, data)
        self.assertTrue(response.headers["content-disposition"].startswith("attachment;"))
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertIn("sandbox", response.headers["content-security-policy"])
        self.assertEqual(build_attachment_delivery_router(self.service).routes, [])
        with self.assertRaises(ValueError):
            build_attachment_delivery_router(self.service, enabled=True)

    def test_copy_restore_and_integrity_denial(self):
        import shutil
        row = self.upload()
        with tempfile.TemporaryDirectory() as clone:
            restored = DisposableFileStorage(clone)
            shutil.copyfile(self.storage.path(row.attachment_id), restored.path(row.attachment_id))
            restored.path(row.attachment_id).chmod(0o600)
            self.service.storage = restored
            self.assertEqual(self.service.retrieve(self.actor, row.attachment_id)[1], b"%PDF-fixture")
            restored.path(row.attachment_id).write_bytes(b"%PDF-tampered")
            with self.assertRaises(EngineeringError):
                self.service.retrieve(self.actor, row.attachment_id)
