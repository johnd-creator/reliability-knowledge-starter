# E6 — operator-controlled QA deployment and recovery plan


**NADI-E-INTEGRATION-02 selection:** local username/password is initial QA auth.
Enterprise SSO/Entra/OIDC registration is an optional future path, not an initial
activation prerequisite. Local account custody/onboarding and existing host/DB/
TLS/storage/PdM/UAT/explicit deployment gates remain. See local-authentication-v1
and the final integration report; historical enterprise-specific evidence below
remains reusable, not initial-QA authorization.

Names proposed by operator-authorized naming: nadi-qa / nadi_qa_application /
nadi_qa_owner / nadi_qa_writer / nadi_qa_runtime. Real host, DNS, TLS, local administrator custody,
storage/scanner, network and accounts remain REQUIRED_OPERATOR_INPUT.
No deployment/provisioning is executed. Config template is NO-GO.

## Safe preparation commands

From exact source checkout:
`git rev-parse HEAD`, `git status --porcelain`, `git diff --check`.
Copy template into private owner-only JSON outside Git; never copy production
.env/platform/source keys. Source-free preflight:
`python -m src.qa.preflight --config <private-json>` (cockpit working directory).
It prints only gate/reason codes, no config values. No dotenv/default DSNs.
Optional `--audit-disposable-db` accepts only explicitly provided loopback *_test
DSN and SELECT-only catalog audit; no migration/grants. Never point at real QA.

For a Git-free preparation image, generate the ignored public-code binding only
from a clean exact-SHA checkout: `python -m src.qa.release --output
<private/.qa-release.json>`. Operator-approved image build copies it via the
ignored deploy/qa/.qa-release.json path. Preflight uses explicit
`--release-manifest /app/.qa-release.json` and checks the complete Python/SQL/
package artifact inventory/checksums. Extra/missing/tampered code is denied.
Checksum binding is not a signature or deployment approval: image digest/build
provenance must still be independently reviewed. No image build/start executed.

## Approval-required real-environment sequence — NOT EXECUTED

1. Platform owner approves exact QA host, ingress/network, pinned SHA/image digest,
   approvals scope and release manifest. Verify main/candidate provenance and
   clean dedicated release checkout before building or selecting any image.
2. Security/identity owner approves local account policy, private administrator
   provisioning, directory/onboarding/revocation and private QA-only DB references. No fixture
   verifier or disposable test server in real QA.
3. DBA approves exact dedicated DB/roles and executes reviewed E3 provisioning,
   private backup/catalog/checksum and migration status/apply. No Mart fallback.
4. Storage/security owner approves private encrypted root/backend/scanner,
   bounded protocol/deadlines, quota/retention/legal-hold and orphan recovery.
5. Independently audited runtime credentials pass canonical privilege audit.
   Factual fixtures default; real Mart reader separately SELECT-only approved.
6. Review real QA server factory and frontend login/proxy integration before
   start. Existing operational public server does not mount Engineering, and
   existing QA frontend is dev-only; do not relax NODE_ENV gates as a shortcut.
7. Explicit approval authorizes only reviewed QA start command on approved host.
   Supervisor binds private listener, trusted proxy CIDRs, no source/scheduler,
   no startup migration, approved pool/session limits and sanitized logs.
8. Smoke health/TLS/session/scopes/CSRF/inspection/review/CAS/recommendation/
   follow-up/revocation and revision/audit persistence using named UAT accounts.
   No WO mutation API and no source acquisition permitted.
9. Operator signs QA acceptance with actual host/DB/storage/local authentication evidence. Until
   then configuration declarations and disposable drills cannot produce GO.

## Stop and rollback

Stop on SHA drift, wrong DB/Mart anchor, unsafe privileges, failed/revoked
identity, missing scanner, storage tamper, missing audit, cross-asset exposure,
source request, unexpected migration/collector or secret disclosure.
Stop only the approved QA supervisor/ingress; revoke QA sessions/runtime grants.
Preserve records/blobs/ledger, isolate failure, reconcile under accountable DBA.
Do not restart source workers or restore over newer accepted evidence.
Restore drill is DB+blob manifest into disposable clone, compare fingerprints,
ledger and history and deny missing/corrupt content before re-opening.

## Secrets inventory (names/references only)

QA runtime DB credential; separate migration administrator; optional future IdP client assertion/
secret/private key only if later selected; approved private storage and scanner identities;
TLS private key; directory-service authority. Values remain in approved private
secret manager/files. No Maximo/PI/CEMS source keys or production reuse.
No browser secrets, passwords in command lines, raw cookies/proofs or DSNs in logs.
