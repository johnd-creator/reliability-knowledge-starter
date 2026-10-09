# Private attachment candidate

AttachmentService uses explicit application store, private storage and canonical
asset authorization. AUTHOR upload, owner or scoped reviewer/admin retrieval.
Metadata and audit insert atomically; immutable checksum verifies retrieval.
PDF/PNG/JPEG type/magic allowlist and explicit size cap; conservative filenames,
opaque keys, no symlinks/public URLs. Missing scanner means QUARANTINED with denied
retrieval. Fixture scanner is not operational malware scanning. Spectrum/report
formats beyond this allowlist require engineer/security approval.

DisposableFileStorage is test-only. Production requires private encrypted backend,
scanner/instrument output validation, quotas, retention/legal hold, credentials,
backup/restore and review. Inspection/case evidence must reference metadata by
identity; attachment availability does not constitute approved inspection evidence.
Orphan plan: reconcile opaque storage keys absent from committed metadata after
an approved grace period; retain quarantined records and immutable audit. No
automatic cleanup/delete scheduler. Failure cleanup discards only newly uncommitted
blob. Crash orphans remain a documented reconciliation requirement.
