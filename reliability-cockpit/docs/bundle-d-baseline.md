# Bundle D baseline and activation dependencies

D0 baseline e836710d1984af7a4bfb739bad0bfbbb96d544ca; Bundle C37–43 merged.
Original workspace and unrelated spreadsheet preserved; isolated candidate worktree.
Graph generation August24 misses Bundle C symbols; exact merged source inspected.
Existing: trusted sessions, RBAC, independent review, transactional records, frozen
evidence, CAS and receipts. Missing: enterprise verifier/durable directory,
application ledger/grants, private storage, real UI transport. D1→D2→D3→D4→D5→D6→D7.

Enterprise checklist: provider registration; signature/algorithm/issuer/audience;
expiry/nonce/state/PKCE/replay; stable subject; authoritative scoped role directory
and serializing guard; HTTPS/proxy/origin/session policy; revocation propagation;
audit retention; callback limits; accountable security/UAT approval. No production
SSO configuration exists here. Verifier supplies subject, directory supplies roles.
Fixture proofs are tests only. Operational routes remain unmounted. Mart remains
SELECT-only, separate from existing application store. No new operational database.
