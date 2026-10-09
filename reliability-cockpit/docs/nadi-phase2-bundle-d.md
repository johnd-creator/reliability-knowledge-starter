# Phase 2 Bundle D — development acceptance and activation manifest

## Final integration-review checkpoint

[NADI-D-INTEGRATION-01](nadi-d-integration-01.md) supersedes merge-readiness
claims below: reproduced session cancellation defect corrected in PR48/6f66ecd;
forward merges preserve stack; current implementation c03e57c and final PR50 head.
Cockpit610/Maximo181/PI191/contracts14 final PASS,11Timescale executed, browser25
and real proxy8 PASS. Activation remains BLOCKED. Historical counts below retain
original measured acceptance. Merge requires new explicit operator authorization.

## Verdict and exact baseline

**PASS for disposable development/test acceptance. Operational activation BLOCKED.**
Phase 1 remains **CURRENT/PARTIAL**; Phase 2 is an integrated QA candidate, not
an operationally accepted application. No automatic merge or deployment.

Baseline main: `e836710d1984af7a4bfb739bad0bfbbb96d544ca`, containing merged
Bundle C PR37–43. Tested implementation: `ee20307a2664e7ca64737c3f43f1256f26cdf9f6`.
D7 adds documentation only; its immutable final SHA is the D7 PR head. Main was
re-fetched and remained the exact baseline before D7. Original workspace,
unrelated spreadsheet, accepted runtime, private journals and config preserved.
Graph generation did not cover Bundle C/D; exact source fallback was used.

## Review stack and checkpoint evidence

Review dependencies are linear; each PR contains its incremental checkpoint.
Retarget/re-evaluate after an authorized merge; do not merge this stack now.

| Checkpoint | PR / base | Head | Development verdict / evidence |
|---|---|---|---|
| D1 Identity | [44](https://github.com/johnd-creator/reliability-knowledge-starter/pull/44) / main | 40e9674 | PASS — 23 identity/session tests; enterprise integration external |
| D2 Persistence | [45](https://github.com/johnd-creator/reliability-knowledge-starter/pull/45) / D1 | dbda9a1 | PASS — 3 PostgreSQL migration/privilege tests |
| D3 Attachments | [46](https://github.com/johnd-creator/reliability-knowledge-starter/pull/46) / D2 | 6faf40a | PASS — 7 attachment/migration tests; production upload/storage inactive |
| D4 HTTP UI | [47](https://github.com/johnd-creator/reliability-knowledge-starter/pull/47) / D3 | 38dbc34 | PASS — injected QA backend and development-gated proxy |
| D5 Acceptance | [48](https://github.com/johnd-creator/reliability-knowledge-starter/pull/48) / D4 | 02f6022 | PASS — 11 actual HTTPS/PostgreSQL tests, 25 browser checkpoints |
| D6 Quality | [49](https://github.com/johnd-creator/reliability-knowledge-starter/pull/49) / D5 | ee20307 | PASS — full local regression and completed GitHub jobs |
| D7 Handoff | branch `codex/nadi-ph2-d7-handoff` / D6 | D7 PR head | Documentation, activation gates and UAT handoff |

## Implemented path and honest limits

Verified identity adapter → authoritative asset-scoped directory → expiring,
revocable server session → CSRF/origin-protected API → application-owned
transactions/CAS/revision audit → real HTTP UI. Fixture verifier/directory are
explicit test adapters, never production SSO or a browser-controlled identity.
Operational `create_app` does not mount Engineering/session mutation routers.

QA factory requires development and an explicit disposable loopback PostgreSQL
application store. Browser QA uses HTTPS and secure HttpOnly cookies. Next proxy
forwards only cookie/origin/JSON/CSRF, never actor/role headers or source credentials.
QA enablement is development-only; normal production routes remain default-off.

UI at `/engineering/qa` is an HTTP contract workbench with paginated records,
canonical command editor, validation/conflict/error states, history and local
recommendation follow-up. It proves integration and durable data; dedicated
engineer-approved method forms, polished Action Board and operational screen
integration still require UAT. Synthetic facts are clearly labeled; UNKNOWN and
NOT ASSESSED remain visible. Good source quality is not health or freshness.

Private attachment service provides metadata, bounded PDF/PNG/JPEG content,
asset/ownership permissions, checksum, quarantine and transactional audit. It is
not mounted as a production upload/download endpoint. Missing scanner fails
closed. Fixture scan callbacks do not constitute operational malware scanning.

## Real acceptance and security negatives

Actual HTTPS sockets and browser → Next → backend → PostgreSQL proved engineer
inspection draft/submit, independent review, frozen evidence attachment to Case,
Case review, recommendation review and internal follow-up. Reload retains records;
390/768/1365 viewport checks passed. Tests reject forged/revoked identity, cross-
asset evidence, self-approval, unreviewed evidence, stale revision and replay.
Missing/unavailable source state remains unknown. Invalid attachment content and
ownership are rejected by service tests. No Maximo mutation route or WO operation.

Codex Security diff review sealed the exact baseline→D6 range: all15 changed
source/config surfaces reviewed plus supporting controls/tests/docs; no concrete
reportable vulnerability established. No applicable SECURITY.md was present.
This is not production certification. Before activation review cancellation during
threaded session lease entry, capacity/timeouts, provider atomic revocation guard,
attachment filesystem/DB crash consistency, and inherited/PUBLIC DB privileges.
Current QA reachability did not establish an exploitable path for those limits.
Private scan artifacts remain outside Git. D7 changes only this handoff and roadmaps.

## Test and CI evidence

See [exact commands and counts](bundle-d-quality.md). Final local results:
Cockpit600, Maximo181, PI191, contracts14, frontend110 assertions; 29 product-safety
files, TypeScript, production build and diff-check PASS. No test failures or skips
in those full backend runs.11 formerly skipped Timescale integration tests ran
against a separate disposable Timescale fixture; no operational PI access.
Actual socket11 and browser25 acceptance complement unit/ASGI tests, not replace them.

D6 GitHub [run37887690942](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/37887690942)
completed SUCCESS for both backend-fixtures and frontend checks. It is a bounded
candidate workflow, not full local browser/Timescale CI. D7 checks are reported by
its PR and are not inferred from D6. No skipped suite is represented as PASS.

Private disposable application dump (custom format,28,077 bytes), catalog and
restore into a second isolated fixture matched Case1/event4/human2/revisions8/
sessions10/ledger4. SHA256:
`bf33e145b52480aba669800aff4aa272d9107917548f28401a01fa10de848da7`.
Backup bytes/logs/certificates/browser screenshots are private and excluded from
Git. This does not certify backup/restore of an operational application store.
Owned temporary previews and DB fixtures are stopped after validation.

## Activation manifest — every gate must be independently authorized

| Gate | Required evidence / accountable approval | Current state |
|---|---|---|
| Enterprise identity | Provider registration; signature/issuer/audience/expiry; nonce/state/PKCE/replay; stable subject and authoritative role/asset directory; atomic guard/revocation propagation | BLOCKED — adapter tested, real provider absent |
| Application provisioning | Approved existing application store identity; owner separate from NOLOGIN writer capability; reviewed LOGIN membership, CONNECT, PUBLIC/default/legacy privileges; Mart SELECT-only credential | BLOCKED — fixtures only |
| Migration/recovery | Explicit owner applies canonical002→003→004→005 plus checksum ledger; wrong DB/Mart denied; private backup and approved restore drill before operational DDL | BLOCKED — disposable sequence/restore proven only |
| Storage | Approved private storage, scanner, size/quotas, retrieval headers, retention/orphan reconciliation, crash recovery, malware failure UAT | BLOCKED — service contract only |
| PdM fields | Responsible engineers approve method/version, field meaning, unit, optional/required fields and reviewer qualifications; no inferred technical limits | BLOCKED — field proposals provisional |
| UI/service operation | Reviewed hosting/TLS/origin, sessions, provider lease cancellation/capacity, accessibility/conflict/unavailable UAT; separate real QA authorization | BLOCKED — local contract workbench only |
| Source coverage | Separately authorize any new Maximo domain or PI acquisition; preserve approved collector contracts | NO NEW ACCESS AUTHORIZED |

### Deployment and rollback proposal (not executed)

After merge/security review and separate operator authorization: pin exact reviewed
release; inventory accepted overrides; verify application-store identity and role
privileges; back up privately; status/checksum preflight; apply only approved missing
application migrations using owner; reconcile writer and separate SELECT-only Mart
reader; inject real verifier/directory; approve storage and fields; run isolated UAT;
then explicitly approve route mounting. Never couple this to source acquisition.
Existing schemas lacking ledger must be reconciled and reviewed, never auto-adopted.

Rollback first removes route enablement and runtime authority/revokes sessions,
then restores the previous reviewed software if schema-compatible. Preserve new
immutable evidence, receipts and ledger. No destructive down migration, table
truncate or restore over newer evidence. Restore/recovery needs a separately
approved plan and accountable administrator. No scheduler or source backfill.

### Engineer/reviewer UAT checklist

- Engineer confirms asset scope, each field/method/version/unit, timestamps,
  source provenance versus interpretation and null/unavailable states.
- Engineer validates draft/save/reload, submission, duplicate/conflict feedback,
  pagination and unsaved changes; no source or Mart mutation.
- Independent qualified reviewer inspects exact frozen revision/evidence lineage,
  rejects own submission and records accountable decision/audit.
- Both validate Case→recommendation→internal follow-up; existing WO is reference
  only, never created/updated by NADI, never implied maintenance authorization.
- Security/platform validate revocation, expiry, CSRF, asset isolation, private
  attachment quarantine/retrieval and least privilege before operational UAT.

## Safety and next recommendation

Task-attributable production Maximo/PI/CEMS GET0; source writes0; Maximo WO
create/update/status0; production DB writes/DDL0; deployment/restart0;
operational Engineering activation0; Phase1 evidence/journal/cursor/mapping/
approved-signal mutation0. Disposable test records/DDL are separate authorized
fixtures. CEMS/NK unchanged; original operational/private evidence preserved.

Next: senior review D1→D7, then enterprise identity and platform provisioning
approval plus PdM engineer field UAT. Real QA provisioning needs explicit owner
authorization. Do not mark Phase1 complete or Phase2 production-ready.
