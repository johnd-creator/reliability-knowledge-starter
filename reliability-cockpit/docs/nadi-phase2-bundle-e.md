# Bundle E — governed QA preparation and NO-GO handoff

## Verdict and exact baseline

**Preparation foundations PASS; overall PARTIAL; real QA NO-GO.**
No real QA/production deployment, provisioning, identity connection or Engineering
activation occurred. Disposable acceptance is not real engineer UAT.

Baseline main: eda3595a9b8d86726dd0d89192ebf4657b66d27e. Bundle D PR44–50
confirmed MERGED in order. Their merge parents/incremental trees were accepted.
Final Bundle E implementation: d3a7d43f55a619440f758ec6ef21ae6c2156422d.
Final documentation candidate is the exact PR59 HEAD reported in its GitHub body.
Main must remain baseline; do not merge these PRs automatically.

Original workspace/other worktrees, source stores, Phase1 evidence, private
config, journals and cursors preserved. Inventory used repository evidence only,
not live host or current-production health probes. Graph2026-08-24 misses E code;
all changed code was inspected directly; no exhaustive graph claim.

## Checkpoints and dependency order

| Checkpoint | PR / commit | Result / boundary |
|---|---|---|
| E0/E1 architecture | 51 /727f115 | PASS; separate QA design/default-off templates, external inputs enumerated |
| E2 identity readiness | 52 /b2f91dd | PASS contracts; actual provider/directory BLOCKED |
| E3 database readiness | 53 /2b4a039 | PASS disposable PostgreSQL ACL/identity/migration faults |
| E4 attachment readiness | 54 /7493e68 | PASS disposable integrity/quarantine/quota/recovery/delivery |
| E5 HTTP/session hardening | 55 /e1dec11 | PASS streams/deadlines/HTTP/concurrency/cleanup; real transport activation gated |
| E6 preflight/handoff | 56 /fa5405a | PASS source-free validation and expected NO-GO |
| E7 integrated rehearsal | 57 /f367419 | PASS actual HTTPS/restart/DB+blob restore, not real QA UAT |
| E6 release binding follow-up | 58 /d3a7d43 | PASS Git-free exact-code inventory/checksums, no image build/deploy |
| E8 manifest/roadmap | 59 /PR HEAD | PASS documentation/manifest; real activation NO-GO |

Review sequence51→52→53→54→55→56→57→58→59. Each PR has only its incremental
checkpoint against its predecessor; OPEN/UNMERGED. No force-push/history rewrite.
E6 follow-up closes an identified preparation-image Git provenance gap rather
than pretending a container has a source checkout.

## Architecture and identity

[Architecture/inventory](bundle-e-architecture.md),
[identity decision matrix](bundle-e-identity.md), [operator runbook](../../deploy/qa/RUNBOOK.md).
Operator explicitly allowed naming: nadi-qa, nadi_qa_application,
nadi_qa_owner, nadi_qa_writer, nadi_qa_runtime. These names are not provisioning
approval. https://nadi-qa.example.invalid is a placeholder, not approved DNS.

Dedicated QA runtime/DB/owner/capability/LOGIN, approved SELECT-only factual
reader or fixtures, private storage/scanner and trusted TLS reverse proxy.
No source collector/scheduler, production credential reuse or Mart write path.
EnterpriseIdentityAdapter still requires a real reviewed verifier and durable
directory. OIDC trust contract is NOT token validation or provider registration.
No browser identity/roles authority. Independent reviewers and versioned grants
remain enforced in the existing domain and transaction/session guard.

Real enterprise callback/session/logout and frontend/backend startup integration
must be reviewed for the selected environment. Existing public cockpit serve and
dev-only QA test server/proxy cannot be used as production shortcuts. No real QA
activation entrypoint/provider/frontend has been enabled by this bundle.

## Security and readiness findings

| Finding | Disposition |
|---|---|
| Writer helper did not reject PUBLIC/default grants or schema ownership | E3 corrected, negative PG fixtures PASS; role/database-owner audits fail closed |
| Dedicated QA DB conflicted with legacy Cockpit anchor requirement | Explicit dedicated mode, exact DB and Mart-anchor protection; no fake legacy tables |
| Unbounded request/upstream text buffers | E5 bounded raw-byte reads, whole-operation abort/deadline; actual Next proxy checks PASS |
| Attachment reads before size bound, process-crash private orphans | E4 size-first atomic/private storage, read-only reconciliation; no automatic deletion |
| Missing/outage scanner | Quarantine and delivery denial; real scanner/deadline approval pending |
| Git-free preflight image could not prove release | E6 follow-up exact SHA/public-code checksums and extra/missing/tampered file denial |
| Enterprise directory/IdP/private infrastructure unavailable | Explicit activation blockers; no fixture identity promoted |
| Actual QA startup and production-mode frontend transport | Separately reviewed integration REQUIRED; default-off boundaries preserved |

No confirmed source-write/auth bypass was reproduced in these bounded checks.
This is focused engineering/negative acceptance, not a certification of live
infrastructure or a new exhaustive security scan. Schema/DB/table ownership,
PUBLIC/default/inherited grants and intended table privileges are audited.
RLS is not claimed: service authorization owns per-asset isolation; DB credential
is privileged and never exposed to end users. DBA must independently inspect
function/extension privileges and service principal scope before activation.

## Automated preflight and release proof

Strict private JSON (owner-only, regular file, no symlink, bounded size); unknown
fields/source credentials/typed coercion denied. No dotenv or implicit DSN.
Default command reads source/config only. Optional DB audit restricted to explicit
loopback *_test fixture; no migration/grants. Logs contain only reason codes.

Actual CLI rehearsal at d3a7d43: exact release/feature gates/names PASS;
identity trust, session policy, storage and declared approvals BLOCKED;
exit2 as expected, source GET0 /operational writes0. A complete synthetic config
can pass PREPARATION while real QA remains NO_GO/DECLARED_NOT_VERIFIED.

94 public-code artifacts bind the actual SHA with checksums. Manifest includes
Python/SQL/package inventory; not secrets or operational config. Git-free image
can verify the explicit manifest without network. Integrity is not signed build
provenance/approval: exact image digest and approval record remain required.
Container/service starts, image build and real-host commands were not executed.

## Disposable integrated acceptance

Actual loopback HTTPS→trusted fixture session→PostgreSQL workflow:
context→inspection draft/submission→independent review→frozen Engineering Case
→NADI recommendation/review→local follow-up/audit. UNKNOWN remains unknown;
quality not health/freshness; units/timestamps preserved; WO reference informational.

Re-created ASGI application/listener and reopened connections retain DB records;
fixture restarts on a new loopback port, not an enterprise process/IdP recovery
claim. Concurrent quota permits one blob/metadata/audit. Revocation/provider
failure denies access, concurrency/CAS and cross-asset tests retained.

Private custom pg_dump/catalog/checksum of fixture DB, restore into a unique
disposable clone, compare full current/revision/audit/receipt/ledger fingerprints;
restore opaque blob/checksum and deny tamper. Source fixture rows unchanged.
Clone and private dump are disposed; no operational backup/restore/DDL.

Browser real Next→HTTP→PostgreSQL rerun25checkpoints, reload durability and
390/768/1365 responsive layouts PASS. Output separated from Bundle D evidence.
Screens remain disclosed synthetic QA workbench, not approved engineer UAT/forms.

## Final test evidence

| Suite | PASS | FAIL | SKIP |
|---|---:|---:|---:|
| Cockpit full (after release-binding follow-up) | 661 | 0 | 0 |
| Maximo Collector | 181 | 0 | 0 |
| PI Collector incl11Timescale | 191 | 0 | 0 |
| Data contracts | 14 | 0 | 0 |
| Frontend assertions37+25+38+10+8+9 | 127 | 0 | 0 |
| Browser workflow/responsive | 25 | 0 | 0 |

Product safety29files, TypeScript, Next production build, links/JSON/Compose/
diff-check PASS. Targeted results: identity47; database10; attachment17;
HTTP/session25; integrated recovery14; release/preflight9. Inherited regression
methods contribute to these counts; do not sum overlapping runs as unique cases.

Commands (component working directory, managed isolated environment):
- `python -m unittest discover -s tests -q` for Cockpit/Maximo/PI/contracts.
- Cockpit uses explicit loopback postgresql+psycopg *_test application/engineering/
  Mart DSNs; no legacy fallback. PI migration DSN targets isolated pi_runtime_test.
- `python -m unittest test_bundle_e_rehearsal -v`.
- `npm run check:engineering && npm run check:phase2 && npm run check:workflow &&
  npm run check:http-qa && npm run check:bounded-http && npm run check:bounded-proxy &&
  npm run check:product-safety`; `npx tsc --noEmit`; `npm run build`.
- `python tests/qa/browser.py` with explicit disposable output and loopback preview.
- `git diff --check`, JSON/reference validation and Compose config --quiet.

Initial fixture issues (incorrect file write working directory, teardown schema,
negative-test column name, TS typed byte arrays, restart port reuse) were fixed
and rerun; initial failures are not called skips/PASS. Historical Python/ASGI/
fixture ResourceWarnings remain; cancellation/pool tests verify checked-out0.
Self-signed TLS bypass applies only to local disposable HTTPS tests.

CI checkpoints51–58 completed SUCCESS. [E7](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/37899292944)
and [release binding](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/37899971535)
run exact implementation commits. Inspect PR59 exact final head separately.
Scoped CI includes PG/session/recovery/contracts/frontend, not full661 or
Timescale/browser; those were run locally. Real IdP, approved scanner backend,
real QA host/TLS/UAT and actual image build NOT RUN, not claimed passing suites.

## GO / NO-GO and activation blockers

**NO-GO** until:
1. Approved actual host/DNS/network/TLS/private ingress and release image provenance.
2. Selected enterprise IdP, registration, reviewed verifier/callback/logout,
   durable versioned directory and grant/revocation/deprovisioning audit.
3. Approved dedicated DB and separate owner/capability/LOGIN credentials;
   on-host migration/permission/backup audit, no production reuse.
4. Reviewed real QA startup/frontend integration; never relax existing dev gates.
5. Approved storage/scanner/encryption/quota/retention/legal-hold/reconciliation.
6. Approved engineer/reviewer/admin onboarding, canonical scopes/independence.
7. [PdM method field approval](manual-pdm-engineer-input.md), smoke/UAT sign-off.
8. Explicit per-action operator deployment/provisioning authorization.

## Prepared approval request — NOT an authorization

Request first QA deployment only after senior review/merge and decisions above.
Scope must name approved QA host/origin/DB/roles, exact source/image, accountable
operator, approved identity/storage/runtime adapters, private backup/rollback and
UAT accounts. Authorize only reviewed QA components; no collectors, Mart writes,
PI/Maximo/CEMS GET, history, WO changes or Phase1 mutation. Stop on release/schema/
identity/privilege/storage/source-safety drift; disable QA ingress and revoke
runtime authority, preserve immutable records. No self-authorization or retries.

## Safety and roadmap

Task-attributable production PI/Maximo/CEMS GET0, source writes0, WO changes0,
real QA/production DB writes/DDL0, deployment/restart0, Engineering operational
activation0, Phase1 evidence/mapping/signal/journal/cursor changes0. Local test
DB/file writes, temporary previews and clone restore are authorized disposable
rehearsals, not real QA. No real secrets read/acquired/exported/committed.

Phase1 CURRENT/PARTIAL, unchanged. Phase2 QA preparation CANDIDATE/PARTIAL.
Next: senior review of stack and external decisions; only then an environment-
bound deployment approval. This task does not start the next development bundle.
