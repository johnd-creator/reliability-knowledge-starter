# E4 — private attachment readiness

Local filesystem adapter is hardening-tested with disposable storage only.
Private root and every file must have restricted ownership/permissions; no symlink
root/files, public URLs or browser paths. Atomic stage→opaque key publication,
fsync and size-first bounded regular-file reads avoid partial content publication
and unbounded retrieval. Process death can leave staged/published private orphans.

Read-only reconciliation compares metadata/file existence, size/checksum and
unexpected keys/symlinks; approved grace/retention policy yields operator review,
never automatic deletion. Legal hold/reference preservation wins. Deletion remains
a separately authorized audited operator procedure; metadata/history never erased.
Root location, encryption/key management, disk quotas and retention approval are
REQUIRED_OPERATOR_INPUT. No S3/remote store is contacted or claimed implemented.

Scanner is injected. Only exact True means CLEAN. Missing/outage/rejected scanner
quarantines; quarantined content cannot be delivered. Scanner timeout/protocol,
version/signature age, encrypted/unsupported formats and approved backend require
security owner review. No fixture scanner may be used in real QA.

Explicit asset byte quota serializes metadata insertion through PostgreSQL
advisory transaction lock; inspection/case review remains independent. Filesystem/
tenant/in-flight quotas must also be enforced by approved infrastructure. Upload
HTTP body adapter remains gated; no operational upload routes mounted.

Delivery router is default-off and requires trusted principal dependency; existing
service checks canonical asset/owner/reviewer and audit before returning bytes.
Download response is attachment-only/no-store/nosniff/sandbox/same-origin. No
unauthenticated direct files or inline executable content.

Backup: consistent private DB dump plus opaque blob/checksum manifest under
approved quiesce window, restore both into disposable clone, reconcile before
opening ingress. Missing/tampered files deny retrieval. E7 rehearses restore and
immutable audit; real storage restore/RPO/RTO require approval, not invented SLA.
