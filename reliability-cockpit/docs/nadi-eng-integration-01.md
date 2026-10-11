# NADI-ENG-INTEGRATION-01 — Login and Engineering QA integration

## Boundary and verified inputs

The PO authorizes integration and testing of PR67/68 in QA, without merging them
or activating production/global authentication. The integration-specific attachment
was not accessible; I0–I4 below map the explicit user directive to auditable gates.

- Latest main: `cc90fc73bea6ae399383d8538035c6454dc7e65a`, fetched and rechecked.
- PR67 Login: `8658c2fbd00bb78f1d8ee2b4462ccece4200a30e`, OPEN, prior exact CI PASS.
- PR68 Engineering: `e60ad78620b6f4e34959731090f8f248a35b6414`, OPEN, prior exact CI PASS.
- Previous serving: `01434fb26a29ba726fe59f663ca96d95bfd43c01`.
- Branch: `codex/nadi-eng-integration-01`, new isolated worktree from latest main.
- Functional browser SHA: `e4be4d0543b48e730b9f5695573cb2bf4fd6f14f`.
- Final exact release/serving SHA and CI are verified independently in PR/task handoff;
  an evidence commit cannot embed its own hash. No merge/approval inferred.

## Milestones

| Gate | Result | Evidence |
| --- | --- | --- |
| I0 — Baseline / preservation | PASS | Existing source/worktrees, loopback QA store, private backup and full clone restore |
| I1 — Integration | PASS | Local exact-head merges preserve PR67/68 ancestry and all functionality; semantic conflict resolution |
| I2 — QA regression / E2E | PASS | Frontend203 assertions, TypeScript/lint/build, backend161 PostgreSQL tests, contracts14; actual persistent workflow51 and Login96; A102/B129 |
| I3 — Preview / rollback | PASS | Official singleHTTPS3000 cutover; pre-cutover session survives; live source rollback to01434fb; expanded schema/data retained |
| I4 — Delivery | Local review PASS; release verification separate | New integration PR, exact-head CI and final serving SHA checked after push; no automatic merge |

[Evidence/screenshots](evidence/nadi-eng-integration-01/README.md) distinguish real
persistent synthetic QA from browser presentation fixtures. Integrated product login
adds a focused real-authentication boundary regression; its final run is in release evidence.

## Integration strategy and actual conflicts

Exact PR67 was merged locally first, then exact PR68, preserving commit ancestry.
This does not merge either GitHub PR. Seven files required semantic resolution:

- DEV-LOG.md: append both chronological Login and Engineering histories.
- PRD.md and docs/design/NADI-UI-SPEC.md: preserve Login presentation boundaries
  and Engineering Case/Advisory/Inbox requirements and implementation checkpoints.
- plans/NADI-ROADMAP.md: keep Phase0–5, independent freshness/PdM/UAT gates,
  Bundle C checkpoint and Engineering track; remove only duplicated obsolete heading.
- globals.css: retain separate scoped Login and Engineering styles and full hashes.
- eslint.config.mjs: union both feature file scopes, unchanged accessibility rules.
- package.json: union lint scope and retain both Login and Engineering checks;
  existing Engineering CI calls check:ux, now including Login checks.

No runtime dependencies added. Login components equal PR67; backend/services,
launcher, Case and Advisory presentation equal PR68. Existing routes, authentication,
RBAC, CSRF, session policies, concurrency/idempotency and source ownership remain intact.
No DDL or persistent migration is executed by Integration-01.

## Distinct review and corrections

| Severity | Finding | Resolution / retest |
| --- | --- | --- |
| High integration regression risk | Selecting one package/lint/CSS side would drop Login checks or Engineering coverage/styles | Semantic union;203 frontend assertions/lint/build PASS; all product and factual browser regressions PASS |
| Medium verification error | Full-row session equality flagged ordinary last_seen_at update | Compared baseline private dump: all58session IDs and authority/policy fields retained; only monotonic last_seen_at allowed, as existing lease code specifies |
| Low test labeling | Inbox-only absence of draft button does not prove all reviewer write policy | Narrow assertion wording to Inbox control exposure; server role/security tests remain independent |
| Low harness readiness | Temporary restore initially started before database readiness; container inventory raced --rm removal | Retry full restore after readiness; exclude exactly the two owned disposable test containers from permanent inventory; full clone/data/schema PASS |
| Low tool invocation | Extra ESLint call from root lacked config | Scoped npm lint already PASS; browser harness Node syntax verified; no application issue |

Review inspected source directly because graph coverage for new Engineering symbols
was stale/missing (2026-08-24 generation); no completeness inference from graph.
Production build emits the existing Next ESLint-plugin advisory; lint/type/build succeed.
Broad hermetic backend regression732 tests PASS with227 expected disposable-PG-only
skips, separately supplemented by the161 real disposable PostgreSQL CI tests with
zero skips; these counts overlap and must not be summed as unique tests.

Visual review: navy/green V1, existing logo and Login accessibility preserved;
Case/Advisory/Inbox readable at1440/768/390, internal table scroll and complete
provenance wrapping, explicit UNKNOWN/NOT ASSIGNED and synthetic boundaries.
Small-screen registers retain horizontal scrolling rather than clipping full detail.
No invented condition, health score, severity or operational delivery is introduced.

## Preservation and controlled rollback

Existing target remains `nadi_live_dev_test`, owner `nadi_dev_fixture`, PostgreSQL
loopback15443, application-owned QA store. Expanded kind CHECK still permits
INSPECTION/RECOMMENDATION/ADVISORY/ADVISORY_ACK; revision CHECK and five migration
entries unchanged. Three QA accounts/grants/passwords unchanged; normal sign-in
updated_at only. All original records, sessions, Advisory/ACK audit and five reference
PNG hashes/workbook remain. Thirty-five original container IDs/start times unchanged.
Only QA API/primary frontend were restarted by the launcher; no collector/API/DB restart.
QA owner privilege remains existing elevated bootstrap privilege: production least
privilege/organizational identity readiness is not asserted.

Before and after workflow private launcher backups were made. The preflight backup
was fully restored into a disposable PostgreSQL16 and matched all rows/schema.
The active database was never overwritten. Actual source rollback demonstrated
01434fb can read both old fixtures and the new Advisory with the same Secure session.

Use [official reset runbook](nadi-dev-reset-01.md): status, backup, stop, switch exact
reviewed SHA, start --preview-ref exact SHA. On every switch inspect clean state,
restore only the known autogenerated Next type-path change, check exact source/backend/
launch SHA and both backends. Keep expanded schema after Advisory/ACK exist; never
narrow constraint or delete records to force rollback. Preserved source01434fb and
both dependency worktrees remain available. No second permanent frontend.

## Remaining acceptance gates

Senior/PO visual approval, actual engineer UAT, real organizational recipients,
real channels/custody/operational rollout and approved PdM definitions remain PENDING.
Global authentication and Phase3 intelligence are not activated. PR67, PR68 and
integration PR must remain unmerged until separately authorized.
Phase1 independent review11Oct21:45WIB, PO checkpoint12Oct20:00WIB and hard expiry
13Oct00:00WIB remain separate, unchanged; operator-review outcome UNKNOWN here.
No policy is extended/reset or operational action performed by this integration.
