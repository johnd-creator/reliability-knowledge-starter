# Real HTTP development candidate

Operational create_app is unchanged. create_qa_app requires development mode,
loopback PostgreSQL *_test and the same explicit application engine for all
writers. No DSN fallback or startup schema creation. Services/source reader and
enterprise verifier/directory are injected. Only fixture harness supplies test
proofs; this is not an enterprise login implementation.

/engineering/qa and /api/engineering-qa exist only with development NODE_ENV and
explicit NADI_ENGINEERING_QA_ENABLED=true. Proxy target restricted to loopback
port13xxx, no URL credentials, redirects or arbitrary origins. Only cookie,
origin, JSON and CSRF forwarded; actor/role headers excluded. Secure host cookie
requires HTTPS localhost for browser QA. No production flags or Compose changes.

QA workspace provides HTTP session/context, paginated records, commands/reviews,
history and action-board recommendation responses. Canonical JSON editor is a
QA contract workbench; domain-specific engineer-approved form UX remains UAT
work. Input survives validation/conflict/network failure. No browser-local
record state or client authority replaces backend validation. Fixtures disclosed.
