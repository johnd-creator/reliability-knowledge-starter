"""Read-only private blob reconciliation and explicit retention planning.

No delete scheduler, production adapter configuration or public blob URLs.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import os, re, stat
from sqlalchemy import select
from src.domain.engineering import EngineeringError
from src.services.attachments import AttachmentRow, AttachmentMetadata


@dataclass(frozen=True)
class RetentionPolicy:
    days: int
    orphan_grace_seconds: int
    approval_ref: str
    legal_hold: bool = True

    def __post_init__(self):
        if (type(self.days) is not int or self.days < 1
                or type(self.orphan_grace_seconds) is not int or self.orphan_grace_seconds < 1
                or not isinstance(self.approval_ref, str) or not self.approval_ref.strip()
                or type(self.legal_hold) is not bool):
            raise ValueError("APPROVED_RETENTION_POLICY_REQUIRED")

    def decision(self, *, created_at, now, referenced):
        if self.legal_hold or referenced:
            return "PRESERVE"
        if created_at.tzinfo is None or now.tzinfo is None or created_at > now:
            return "UNKNOWN"
        return "REVIEW_DELETE" if now - created_at >= timedelta(days=self.days) else "PRESERVE"


def reconcile_attachments(store, storage, *, policy, now):
    """Plan only; does not discard, update metadata, rescan or mutate audit."""
    if now.tzinfo is None:
        raise ValueError("AWARE_RECONCILIATION_TIME_REQUIRED")
    with store.engine.connect() as c:
        documents = list(c.scalars(select(AttachmentRow.document)))
    metadata = {m.attachment_id: m for m in map(AttachmentMetadata.model_validate, documents)}
    findings = []
    for key, row in sorted(metadata.items()):
        try:
            data = storage.get_bounded(key, row.size)
            if len(data) != row.size or sha256(data).hexdigest() != row.checksum:
                findings.append({"attachment_id": key, "code": "INTEGRITY_FAILED"})
        except FileNotFoundError:
            findings.append({"attachment_id": key, "code": "FILE_MISSING"})
        except Exception:
            findings.append({"attachment_id": key, "code": "STORAGE_UNAVAILABLE_OR_UNSAFE"})
    for entry in sorted(storage.root.iterdir()):
        if entry.name in metadata:
            continue
        if not (re.fullmatch(r"[a-f0-9]{32}", entry.name)
                or re.fullmatch(r"\.stage-[a-f0-9]{32}", entry.name)):
            findings.append({"code": "UNEXPECTED_PRIVATE_ENTRY"})
            continue
        info = entry.lstat()
        if not stat.S_ISREG(info.st_mode):
            findings.append({"code": "UNSAFE_PRIVATE_ENTRY"})
            continue
        created = datetime.fromtimestamp(info.st_mtime, timezone.utc)
        age = (now - created).total_seconds()
        findings.append({"attachment_id": entry.name, "code":
                         "ORPHAN_REVIEW_REQUIRED" if age >= policy.orphan_grace_seconds
                         else "ORPHAN_GRACE_OR_CLOCK_UNKNOWN"})
    return {"mode": "READ_ONLY", "metadata_records": len(metadata), "findings": findings,
            "automatic_deletions": 0}


def attachment_response(metadata, data):
    """Private delivery after trusted service authorization and retrieval audit."""
    from fastapi import Response
    # Filename comes from upload allowlist, never browser/header interpolation.
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_. -]{0,119}", metadata.filename):
        raise EngineeringError("ATTACHMENT_FILENAME_INVALID", 422)
    return Response(data, media_type=metadata.content_type, headers={
        "Content-Disposition": 'attachment; filename="' + metadata.filename + '"',
        "Cache-Control": "private, no-store", "Pragma": "no-cache",
        "X-Content-Type-Options": "nosniff", "Content-Security-Policy": "sandbox; default-src 'none'",
        "Referrer-Policy": "no-referrer", "Cross-Origin-Resource-Policy": "same-origin"})
