# NADI Phase 2 Bundle B — umbrella evidence

Baseline: latest verified main `02e887c56057611f112b7b652ba9a9aee8b382ea`,
PR29 MERGED on 8 October 2026; corrected head `67dcb4d` included.
Phase 1 remains CURRENT/PARTIAL; Phase 2 candidate, operational activation OFF.

Original workspace and existing worktrees preserved, including an unrelated
untracked spreadsheet. A fresh isolated worktree is used. PRs are a dependency
stack: review/merge in checkpoint order, never automatically. No concurrent branch
or private runtime evidence is overwritten. Historical Phase-1 GOV03 monitoring
expiry/review remains the accountable operator's duty; this bundle changes no
policy, service, credential, journal, lock, cursor, mapping or measurement.

## Checkpoints

| Checkpoint | Candidate scope | Verdict |
|---|---|---|
| B1 | ADR007, source-boundary policy, local coverage/dependency/threat review | PASS — source-free architecture evidence |
| B2 | Trusted identity/session/RBAC adapter | IN PROGRESS |
| B3 | Local factual intelligence improvements / collection proposal | IN PROGRESS |
| B4 | Manual inspection envelope / methods / isolated lifecycle | IN PROGRESS |
| B5 | Recommendations / existing WO references / audit | IN PROGRESS |
| B6 | Development-only five-screen concept foundation | IN PROGRESS |
| B7 | Integrated regression/security/handoff | IN PROGRESS |

Baseline test: Cockpit `python -m unittest discover -s tests -q`: 396 run,
276 pass, 120 skip. PostgreSQL fixtures not configured; no new operational DB.
Existing SQLite ResourceWarnings are visible, not hidden as a clean leak audit.
Final fixture/test evidence and PR links are added at B7.

## Dependency and threat review

Accepted contracts use Pydantic, SQLAlchemy, FastAPI; web is Next15/React19/TS.
Reuse existing dependencies; no invented enterprise IdP SDK, new collector or
source credential path. Browser actor/roles/assets remain untrusted. Protect
session fixation, revocation, CSRF/origin, IDOR, self-review, audit tampering,
lost updates, unsafe attachments and interpretation-as-fact. Production bootstrap,
provider validation, identity directory, retention/quota and restricted writer
provisioning are activation blockers. This is a scoped design assessment, not a
claim of dependency-CVE clearance or operational penetration testing.

Safety target: source writes0, unapproved production GET0, operational DB/DDL0,
deployment/restart0, Engineering activation0, Phase-1 evidence mutation0.
