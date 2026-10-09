# NADI-D-INTEGRATION-01 — final senior review and merge preparation

## Verdict, baseline and scope

**PASS — READY for an explicitly authorized development-candidate merge.**
No merge executed. Operational activation **BLOCKED**. Phase1 **CURRENT/PARTIAL**;
Phase2 integrated QA **CANDIDATE/PARTIAL**, not production-ready.

Main verified before/after review: `e836710d1984af7a4bfb739bad0bfbbb96d544ca`.
Original expected candidate: `f33d8a3ad59e9cbb3c40012f0beed2603684e6a8`.
PR44–50 were OPEN/MERGEABLE with exact expected bases and linear incremental
ancestry. Original workspace/spreadsheet, other worktrees, accepted runtime,
private config, Phase1 journals/evidence and collectors preserved.

Review included the15 changed source/config surfaces, all32 changed files,
existing ADRs, security/acceptance reports and activation manifest. GraphAugust24
missed new symbols; exact frozen source was read. Original immutable diff scan
retains its own result; post-review corrections are separately tested, not
misrepresented as the original scanned tree. A secondary correction follow-up
review was unavailable; parent code review and functional regression completed.

## Findings and disposition

| ID / severity | Exact original location | Evidence / decision |
|---|---|---|
| D-01 MAJOR functional acceptance | `src/services/application_identity.py:267–279` at f33d8a3 | Cancel during entry skipped lease exit and blocked ASGI loop ~0.299s. Reproduced with local dependency; corrected6f66ecd in PR48, propagated normally. No external attacker-triggered cancellation established; not a confirmed public security exploit. |
| D-02 MINOR resource hardening | `web/app/api/engineering-qa/[...path]/route.ts:12–17` | Request is buffered before1MiB check; upstream response is buffered without byte cap. Follow-up before operational exposure: bounded streaming request/response. Merge may proceed because QA is explicitly development-only and targets disposable loopback backend. |
| D-03 ACCEPTED LIMITATION / activation gate | `src/repositories/application_migrations.py:48–62` | PUBLIC/default UPDATE survives writer grants; schema-owner writer can drop schema. Reproduced in isolated PG and rolled back. Helper is not a complete provisioning audit. Existing docs require separate schema owner and PUBLIC/default/service-membership review; operational provisioning remains blocked until independently corrected/audited. |
| D-04 ACCEPTED LIMITATION / activation gate | `src/services/attachments.py:58,82–87` | Process death or put-after-write failure leaves a private orphan; retrieval with no metadata returns NOT_FOUND. Private file read precedes size/checksum check. Production storage, reconciliation/retention, scanner and HTTP delivery headers remain unimplemented/unmounted. |
| D-05 ACCEPTED LIMITATION / external gate | enterprise provider/directory contract | Real signature/claims/replay verification, atomic directory guard and bounded provider/DB deadlines require enterprise integration approval. Fixture identity is not production SSO. |

No unresolved BLOCKER or MAJOR in the development candidate. No auth/source-write
bypass was established. No applicable SECURITY.md existed. The sealed original
security diff review reports no confirmed reportable vulnerability; this does not
certify production infrastructure or erase the reproduced functional finding.

## Correction and stacked history

PR48 fix `6f66ecda3059f2feaa11c1ce6d4aef4715a22766` shields entry and cleanup,
exits on the same worker, survives repeated cancellation, avoids synchronous
shutdown on the event loop, bounds active async leases (default8, configurable1–64),
and sanitizes provider outage responses. It does not invent a freshness SLA.
No-op retry/source call is added. Provider/DB waits must still be bounded by the
approved integration; Python cannot forcibly stop an arbitrary blocked provider.

PR49 normal forward merge `d889b2a` includes the fix; CI correction
`c03e57c3da5219e8090d193f9ccd8b88951acf92` adds the10new tests to scoped backend CI.
PR50 normal forward merge `fabe5cf` preserves the D7 handoff. Final docs PR head
identifies the complete reviewed candidate. No rebase, force push or main merge.
PR44–47 unchanged; PR48–50 intentionally advance for authorized corrections.

## Session and database acceptance

10new tests pass: cancellation entry, repeated cancellation exit, same-thread
cleanup, responsive event loop, bounded worker admission, entry failure/body
exception cleanup, sanitized provider outage, actual PG cancellation with zero
checked-out connections, same-session serialization, revocation racing with an
application write, and sanitized pool timeout with recovery. Tests are grouped
into10test methods; individual assertions exceed that count.

Revocation waits for the authorized transaction/guard then blocks subsequent
access. Expiry/forged identity/CSRF/independent review and stale-revision tests
remain passing. Provider failure never yields an authorized principal.

DisposablePG privilege probe confirms10relations with intended table grants,
zero sequences, audit UPDATE/DELETE/TRUNCATE/ALTER denied42501, unsafe LOGIN/
inherited-role/table-owner targets refused, safe service LOGIN membership,
wrong DB/checksum/missing-table drift refused. PUBLIC/default/schema-owner hazards
above remain mandatory activation checks, not silently reported safe. Owning Mart
and application identities remain separate; application cannot fall back to Mart.
Backup/restore remains the prior isolated drill; no operational backup/DDL.

## Attachment and HTTP boundary acceptance

19attachment checks pass (15forensic +4repository tests): cross-asset denial,
traversal/symlink, filename/type/magic/size, scanner quarantine, checksum, missing
file, audit/commit compensation, actual child process death/private orphan. Audit
must commit before retrieval is returned. No operational upload route. HTTP
retrieval headers cannot be accepted until a reviewed delivery adapter exists.

9executable Next proxy groups and10factory checks pass, using actual Next request/
response classes and loopback fixture: production/default-off, opt-in,7invalid
URL targets, unsafe paths, header filtering, cookie/cache, method/size and redirects.
Only cookie/origin/content-type/CSRF forwarded; actor/roles/source credentials are
not forwarded. QA factory requires development + local PG *_test + identical
injected writer engine. Production create_app remains unmounted.

8additional actual Next→backend checks pass: bootstrap200, forged CSRF403,
wrong origin403, cross-asset/forged-role404, Maximo mutation route404, logout200,
revoked/forged cookie401. HTTPS verification bypass belongs only to the disposable
self-signed local fixture; operational TLS behavior was not modified.

## Integrated regression and CI

Final full regression after correction: Cockpit610 PASS/0FAIL/0SKIP (76.238s),
Maximo181 PASS/0FAIL/0SKIP, PI191 PASS/0FAIL/0SKIP (all11isolated Timescale tests),
contracts14 PASS/0FAIL/0SKIP. Frontend110 assertions,29product-safety files,
TypeScript/build/diff-check PASS.11actual HTTPS/PostgreSQL tests are included in
full Cockpit acceptance. Browser25checkpoints repeated through Next/backend/PG:
inspection→independent review→frozen Case→review→recommendation→follow-up;
reload persistence and390/768/1365 responsive checks, desktop/mobile visual QA PASS.

Exact commands are in [quality evidence](bundle-d-quality.md). Initial runs used
implicit psycopg2 DSNs and failed fixture setup (PI missing driver; Mart composed
SQL driver mismatch). They are retained as failed environment attempts. Explicit
postgresql+psycopg fixture DSNs repaired setup; final suites above pass. Existing
Python/ASGI deprecation and legacy fixture ResourceWarnings were observed; new
session PG cleanup assertions verify checked-out connections return to zero.
No skipped external integration (IdP/production storage/UAT) is called PASS.

Original D6/D7 GitHub runs37887690942 /37888334023 completed both jobs SUCCESS.
Corrected PR49 run[37892980855](https://github.com/johnd-creator/reliability-knowledge-starter/actions/runs/37892980855)
completed SUCCESS at exactc03e57c, including new session tests. Final PR50 checks
must be inspected at its final docs head before authorization. Scoped CI does
not include full610suite, browser or Timescale; those are local fixture acceptance.

## Controlled merge plan — not executed

Sequence: **44→45→46→47→48→49→50**, method **merge commit**.
Request explicit operator authorization only after final exact-head CI/ancestry
checks. Main currently unprotected; no branch-protection rule was bypassed or
changed. Empty reviewDecision is not an approval; operator review remains required.

For each future step:

1. Fetch main, require the expected SHA from the previous step; stop on unexpected
   baseline movement, conflict, required-check/review change or failed gate.
2. Read exact PR head and incremental tree against its accepted predecessor.
3. Merge with --merge and exact head match; never admin-bypass or force main.
4. Fetch resulting main; verify merge parent1 is prior main, parent2 is exact
   candidate, all prior ancestors preserved, incremental tree occurs once.
5. Retarget next PR to main. Re-evaluate effective diff/ancestry/mergeability,
   required reviews/checks and route-default-off/source-read-only invariants.
6. After final merge, verify expected candidate tree, history, regression gates
   and deployment impact. Do not deploy, migrate, mount routes or start collectors.

If gating differs, STOP and report BLOCKED. Rollback/recovery is a separately
reviewed revert plan preserving immutable records, not history rewrite or DB reset.

## Activation gates and safety

Real enterprise identity/directory/deadlines, separate migration-owner/runtime
writer provisioning (including PUBLIC/default/inherited/schema/DB ownership),
private storage/scanner/recovery/retention/delivery, approved PdM fields, final UI
UAT and explicit deployment authorization remain BLOCKED. QA JSON workbench is
not final engineer forms or a production Action Board.

Task-attributable production PI/Maximo/CEMS GET0; source mutations0; Maximo WO
create/update/approve/status/close0; production DB/DDL0; deployment/restart0;
Engineering operational activation0; Phase1 evidence/mapping/signal/journal/cursor
mutation0. Disposable fixtures/temporary previews are separate authorized tests
and stopped after acceptance. Original workspace/spreadsheet/config preserved.

Phase1 **CURRENT/PARTIAL** unchanged, Phase2 **QA CANDIDATE/PARTIAL**.
Next: explicit operator authorization for this exact stack merge only; activation
requires a separate enterprise/provisioning/PdM/UAT review and authorization.
