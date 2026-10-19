# NADI source integration and future paired lifecycle

Updated 2026-10-19. This runbook reconciles the earlier V2 upgrade proposal with
observed development runtime. Source integration through GitHub does not deploy
or restart the laptop. Current authority covers candidate commit/push and normal
merge after review and CI; it excludes runtime, collector, database, auth and
session changes.

## Verified development baseline

Read-only observation at **2026-10-19 11:52 UTC**:

| Surface | Observed identity |
|---|---|
| Main before source integration | `c7930694187b61ffa6dae90e6a14938e7564c3e7` |
| HTTPS3000 frontend source | PR104 `fc33515a3cd0ec4bd9fad81c59e65babe397c2b3` |
| Development API source/current SHA | Same PR104 head |
| Installed four-file controller | PR103 `1ec93d6f3507321617903d169451d77fdcc1216e` |
| API bootstrap SHA | Same PR103 head |
| Serving source directory | `.nadi-dev/ux-experience-live-01-app` |
| Retained development fixture | `nadi_local_dev_01_test`, DISPOSABLE_TEST / DEVELOPMENT |
| Runtime listeners | HTTPS `[::1]:3000`; development API `127.0.0.1:13036` |
| Existing containers | 35 identities/states unchanged across review |

Controller files matched the installed manifest and immutable PR103 Git blobs,
allowing only the established ROOT installation substitution. API health proved
transport readiness, not an existing user's authenticated session or source
freshness. No login/logout, session-proof extraction or retained-record writes
were used for this observation.

The serving source has the existing generated
`reliability-cockpit/web/next-env.d.ts` modification. The separate runtime control
checkout remains `feature/pi-governed-source-adapter` at `0c800dac1da6ef863afdb193021176fe7feac073`,
with modified `compose.dev.yaml` and untracked `23496711.xls`. Preserve all three;
neither checkout is the source-integration workspace.

## Source integration scope

See [the integration plan](NADI-UI-INTEGRATION-103-102-104.md). PR103 is independent
of PR102; PR104 descends from PR102. Preserve all original heads through merge
ancestry, retain both DEV-LOG histories, qualify the exact combined head with
disposable PostgreSQL in CI, then use the normal PR merge flow. Recheck main and
required checks immediately before merge. Do not bypass protection/review rules,
force-push or treat individual PR checks as combined qualification.

After merge, run the existing NADI Engineering candidate workflow on main. It
supports workflow_dispatch and asserts the checked-out SHA. Require terminal
backend/frontend success for the final main SHA, and verify the original heads
are ancestors of main. Source PR status and CI outcomes are independent of
preview visibility. Do not reinstall the controller or select an application
source merely because its commits have reached main.

## Earlier paired upgrade recipe is historical

The [original PR103 runbook](https://github.com/johnd-creator/reliability-knowledge-starter/blob/1ec93d6f3507321617903d169451d77fdcc1216e/reliability-cockpit/docs/NADI-UX-V2-PAIRED-UPGRADE-RUNBOOK.md)
was written before the observed controller103/application104 runtime. Its
PR102 application target, `7daab3a` outgoing source and `fef7bcc` controller
baseline are historical. Do not replay its installation, sealing, selection or
rollback commands against the current runtime. The installer also contains an
explicit historical active-root guard; changing SHA variables alone does not
make that installation recipe applicable.

Historical source seals, receipts, backups and session proofs are bound to exact
source/controller/process/store identities. Their existence grants no authority
to reuse them, reset source or delete journals. Preserve their private files.

## Separate authority for any future lifecycle operation

A future runtime task must first re-inventory actual Git dirty state, exact
frontend/API/controller/bootstrap SHAs, units/listeners and competing workers,
container/volume identities, existing store/schema/ledger, TLS/dependency pins
and permitted session policy without exposing secrets. Stop if the baseline moved.

It must review the desired exact application/controller commit and compatibility
against the actual outgoing source. A dirty source requires fresh source-only
preservation and independently verified recovery under the reviewed controller;
never use destructive checkout/reset/clean/stash. Retain base objects needed by
read-only recovery alternates. Do not substitute databases, restore data or apply
migrations as part of source selection.

Any authenticated acceptance proof must use a separately authorized operator
workflow and an existing session, remain owner-private outside source, and never
be printed. HTTP 200 or a transport health check is insufficient evidence of
session/role/asset policy or retained-record preservation.

Only a separate explicit approval naming the exact target SHA, actual baseline,
private preservation/recovery digests, retained store, allowed unit restarts and
one bounded recovery can authorize paired activation. Exclude collector, source,
schema/account/policy changes. Preserve journals and stop on failed recovery or
unresolved transition; never blindly retry startup.

Product Owner acceptance of the existing development appearance is retained.
Engineer method/threshold/UAT approval, F03 operational NO-GO and Phase1 mapping
and freshness gates remain independent and are not advanced by source merge.
