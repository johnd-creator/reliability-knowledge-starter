# NADI-UX-V2-CONTROLLER-RECOVERY-01

2026-10-18. Offline implementation qualified. Draft PR and exact-head CI evidence
are recorded in the PR and final handoff. No runtime activation authorized.

## Baselines and cause

- Main: c7930694187b61ffa6dae90e6a14938e7564c3e7.
- Unmodified open Draft [PR102](https://github.com/johnd-creator/reliability-knowledge-starter/pull/102): 260c4f9f5f9a17aea3b36476ca4a0e202069e19d (D).
- Both serving development sources: dirty 7daab3a62866f19b30fb45462a94bafff8795dc5 (A).
- Installed controller: fef7bccd61d3d6a5dd184f2fff94453242ff2056, unchanged.
- This branch: codex/nadi-ux-v2-controller-recovery-01, from verified main.

Five committed contract leaves differ between A and D, under reliability-cockpit:
src/api/application_session.py, src/api/engineering_qa.py,
src/services/local_authentication.py, web/lib/api.ts and
web/components/useQaRecords.ts. Their actual working bytes already match D:
trusted self identity, authentication readiness, bounded username lookup,
401/403 handling and expired-session UX. Comparing only A therefore rejects
the working implementation. Admitting dirty bytes as an ordinary clean checkout
would conceal uncommitted work and leave rollback unable to reconstruct runtime.

The approved architecture remains **Option C → Option B**: qualify controller
delivery first; separately authorize a paired frontend/backend upgrade later.
LOCAL_PAIRED_SOURCE_ACTIVE and frontend-only selection refusal remain unchanged.

## Source preservation and recovery

The implementation remains inside the established four-file release:
SealedSource lives in deploy/development/local_development.py; the existing
installer and release hash protocol still verify all four files. CLI additions
are local-preserve, local-prepare-recovery, exact recovery receipt approvals for
paired preflight/select, and an existing-session acceptance proof.

Five identities remain distinct:

| Identity | Meaning |
|---|---|
| A | Original committed HEAD, branch/detached state and Git provenance |
| Local work | Index fingerprint, status and actual dirty/untracked file content |
| Outgoing runtime | Original root/A, launcher/controller/config/accounts hashes and both process owners |
| D | Explicit reviewed clean V2 candidate, currently PR102 HEAD |
| R | Private clean recovery commit representing exact outgoing working files |

An exclusive owner-private archive outside source contains a SHA256-approved
manifest and content-addressed objects. It records file bytes, length, SHA256,
Git blob identity, permission bits, UID, tracked deletions, nonignored untracked
files, index fingerprint, HEAD/branch/origin/common directory and runtime identity.
Double scans reject concurrent changes. Later approvals recheck hashes and source.
Existing destinations are never overwritten.

The boundary is Git-tracked and nonignored untracked regular source files.
Ignored caches/dependencies/private runtime state are not a source backup.
Dotenv source files, frontend dotenv dependencies, private key/dump paths,
symlinks, hardlinks, traversal, unresolved indexes, foreign owners and unsafe modes
are refused. Existing ignored backend config remains separately protected runtime
state; it is never copied into R or GitHub. Filename rules cannot detect an
arbitrary secret inside ordinary source: archives remain private and must never
be pushed.

R is reconstructed file by file from approved objects into a new owner-private,
independent Git repository. Its synthetic commit has A as parent and exact
manifest tree; pushing and hooks are disabled. Snapshot objects are written only
inside R, never the shared application repository. The original Git object store
is a read-only alternate for base history: R is independently writable/restorable,
but is not a portable backup of all original Git history. Retain original base
objects. The receipt binds manifest digest, R root/commit/tree and private config.
Verification requires exact files/modes, clean status, parent/tree/origin/alternate
and push guard. Recovery never overwrites the original or concurrent edits.

Preparation locks lifecycle, validates outgoing ownership/readiness and binds the
seal to current release, processes, config and account hash. It prepares only R
and private config/receipt. Preflight preserves clean candidate/repository guards,
all 20 compatibility surfaces, package dependency sections, installed dependency
lock fingerprints, pinned Node, trusted TLS, existing database container/port and
read-only schema/ledger checks. For this path it additionally compares D with R,
whose committed bytes now represent actual outgoing source. Ordinary unrelated
repositories still fail the original repository guard.

Selection validates an existing private session proof before backup or stopping,
then during acceptance/recovery readiness. No session enters the seal. Account/
config hashes, database identity and schema/ledger must remain equal. A fresh,
readable private backup is required before either stop; it is never automatically
restored. The previous config hash intentionally belongs to outgoing/recovery config.

Double preflight and final source/process verification precede cutover. Only the
development pair may stop. Failure permits one bounded restart of R against the
same store. R reports its synthetic SHA plus original provenance, never clean A.
All extant unit/listener owners are checked before either recovery stop.
Failed recovery records FAILED without a successful recovery event or pointer
publication. An unresolved stopping journal blocks retry pending explicit review;
a failed event alone does not prove recovery. Never delete journals to bypass it.

## Qualification evidence

Private evidence remains in /tmp/nadi-controller-recovery-01/, outside GitHub;
the full earlier 341-file audit and blocked-preview preservation remain intact.

The real outgoing source was sealed and reconstructed offline: **1,213 source
files verified**, including dirty/untracked bytes and modes, independent private
Git objects and disabled pushing. Original source is unchanged. This seal is
marked offline, not lifecycle approval; future installed code must reseal with
fresh runtime identity.

Hermetic recovery/controller regressions: **152 tests pass, zero skips**
(52 new plus 100 existing). Combined affected backend/auth/Reports/Integration/PdM
contracts: **186 run, 182 pass, four optional PostgreSQL tests skipped locally**.
CI runs those PostgreSQL cases in an isolated database. Local pinned-Node-22
frontend contracts passed: global authentication 16, local login 16, Integration
22, Reports 26, PdM input 16 and workbook 48 checks. Coverage includes
dirty/untracked/deleted/binary files, modes, corruption/missing archives, traversal/
symlinks, concurrent changes, provenance/release/receipt mismatch, dependencies,
contracts, account/config/session drift, locks, interrupted transitions, database/
backup refusal, first- and second-service startup failure, failed bounded recovery,
and refusal before service mutation. Process/store boundaries are simulated.

Independent actual-file Git blob comparisons match D across **20/20 surfaces**:
96 backend source files, five QA fixtures, six application migrations, 51 canonical
contract files and the remaining comparator paths, zero mismatches. The production comparator also passed all 20 surfaces against the actual reconstructed
R commit and D. Package dependency/devDependency/engine/override sections also match. This is bounded
source compatibility, not runtime acceptance or business-data freshness.
No backend application patch or source-level database migration is needed;
live ledger compatibility remains a future gate.

Non-interference: 1,213 original source files, 69 private controller/runtime/
account/backup files, both service identities and all 35 Docker container
identities/states/ports unchanged. Frontend PID 21538/API parent PID 21536 retain
original start identities and zero restarts. Trusted-CA HTTPS login, PdM and
development-health probes returned 200. No application write, login/logout,
session creation, source collection, migration/restore, service restart or
controller install was performed. This is action/identity preservation evidence,
not a frozen row-by-row audit of a store other users may continue using.

## Exact source reconciliation

The private 341-file matrix remains authoritative. Of 165 local changed/untracked
paths, 149 already match D. All eight overlapping dirty paths are dispositioned
below; seven already match main. No Mode A application behavior requires a separate
carry-forward patch. Replaying the dirty patch onto D would duplicate integrated
changes. The 16 residuals are fully dispositioned; selecting D means using reviewed
candidate bytes later, never changing the active original source now.

Paths are relative to reliability-cockpit, except DEV-LOG.md.

| Residual file | Disposition and retained behavior |
|---|---|
| DEV-LOG.md | Preserve local history privately; reconcile append-only claims separately. D has later integrated/V2 history. |
| docs/NADI-AUTH-FOUNDATION-01.md | Preserve historical local plan; integrated report is candidate documentation. No runtime behavior to port. |
| web/app/globals.css | D retains Phase 2 styles and adds Reports/Integration; future visual acceptance required. |
| web/app/layout.tsx | Active equals main; D appends enterprise styles after approved login/global imports. |
| web/components/CaseForm.tsx | Active equals main; D retains validation/draft recovery, adds busy save/grouped actions. |
| web/components/CaseWorkspace.tsx | Active equals main; D retains filters/CAS/roles/draft ownership, adds loaded-page search/review emphasis. |
| web/components/PdmCenter.tsx | Active equals main; D retains discard/readiness gates, adjusts navigation and advanced filters. |
| web/components/PdmHistory.tsx | Active equals main; D retains exact-time/source-unit queries/raw plots, discloses comparability guidance. |
| web/components/PdmMeasurementForm.tsx | Active equals main; D retains validation/units/null/zero/evidence, groups acquisition context/busy save. |
| web/eslint.config.mjs | D retains auth/app/lib coverage and adds Reports/Integration. |
| web/lib/login-navigation.ts | D allowlist adds Reports/Integration; external/callback rejection retained. |
| web/next-env.d.ts | Preserve original generated primary-dev reference; select D source, allow reviewed runtime regeneration. No cache patch. |
| web/package.json | D scripts/lint order; dependency sections match. Locked install required. |
| web/scripts/global-auth-check.mjs | D retains auth assertions and adds Reports/Integration/exact public-asset checks. |
| web/scripts/localization-check.mjs | Active equals main; D approved token/test wording retains fixture/auth contracts. |
| web/scripts/phase2-login-header-check.mjs | D retains core routes, adds Reports/Integration return-route tests. |

Documentation/generated differences stay archived; unrelated local work stays
untouched. No extra application integration worktree/backend patch is necessary
from this bounded reconciliation. Controller delivery and D independently depend
on the same verified main. Future activation must review both deliveries and name
an exact application SHA; no moving branch or UI cherry-pick into this PR.

## Remaining requirements and risks

The [paired-upgrade runbook](NADI-UX-V2-PAIRED-UPGRADE-RUNBOOK.md) is prepared and
**not executed**. Senior review and explicit exact-controller delivery approval
precede installation. Separate explicit local activation approval must name D,
manifest/receipt/R, the two development services and existing retained store.
Installation approval alone does not authorize selection; this task permits neither.

Recheck CI, source/process/controller integrity, accounts/existing session, TLS,
dependencies, fresh backup and retained schema/ledger. Concurrent edits/reload
replacement, expired session/certificate, missing base objects, generated source
drift, dependency/store changes or unresolved journals fail closed.
No live rollback is certified by simulation. On failure report actual units/
listeners/source; do not infer health from a pointer. Read-only retained-record
and session-policy comparisons, Mode A runtime checks and PO visual/UAT acceptance
remain future prerequisites.
