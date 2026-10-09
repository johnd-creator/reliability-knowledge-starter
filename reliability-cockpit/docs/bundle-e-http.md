# E5 — bounded HTTP/session/proxy readiness

Development proxy now caps raw request bytes before parsing (1MiB), upstream
bytes (2MiB), and one whole request/body/fetch/response operation deadline (15s).
These are disposable QA safety caps, not approved operational thresholds.
Chunked requests, oversized first chunks and stalled streams are tested; abort
cancels readers without waiting indefinitely. Redirects remain forbidden.

Backend disposable QA factory has bounded ASGI ingress, declared/actual size and
body deadline. Oversized/invalid/disconnected/timed-out bodies never invoke the
application, session lease or writer. No actor/role/Authorization headers are
forwarded. Exact HTTPS origin and server CSRF/cookie enforcement remain intact.

Operational create_app remains unchanged/unmounted. Real reverse proxy must strip
all inbound forwarding/actor/identity headers and recreate reviewed Host/scheme/
client-address headers only from approved ingress CIDRs. Backend inaccessible
outside private ingress. Uvicorn proxy trust must use explicit allowlisted proxy
IPs, never '*'. Forwarded identity headers are never authentication. TLS/HSTS,
timeouts/byte caps/rate limits and final origin require operator approval.

Session capacity is bounded; cleanup survives entry/exit/repeated cancellation,
same-session operations serialize, revocation races deny subsequent access,
pool timeouts and provider errors are sanitized. Provider guard must have approved
deadline and serialize grant changes, not a no-op. Pool overflow0 and explicit
connect/statement/lock/deadline policy are reviewed configuration requirements.

QA health routes disclose only LIVE/READY/UNAVAILABLE and query injected local
application DB SELECT1. They do not certify enterprise IdP, permissions, source
freshness or operational readiness. Logs use request correlation/reason codes;
never body, cookie, proof, auth headers, DSN or raw exception. Metrics must avoid
subject/asset IDs as high-cardinality/public labels. Operator retention is pending.

This hardening prepares the boundary; production UI transport and enterprise
callback integration remain separately reviewed activation prerequisites.
