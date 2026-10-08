# NADI-P1-FRESH-001D-DIAG-01 — Coal Flow A source failure

## Verdict

**PARTIAL. Historical root cause: UNKNOWN. Observability gap: CONFIRMED.**

The failed one-run authorization was consumed. This investigation makes no PI
or Maximo source request, does not reproduce the failure live, and does not
deploy candidate code. Phase 1 remains CURRENT/PARTIAL.

Baseline main and deployed API/operator release:
`a07d683663f8e805fe6e4076f6a67a01f8521787`, confirmed as PR #25's merged commit.
The serving release remains clean and unchanged. Candidate diagnostics live on
`codex/nadi-p1-fresh-001d-diag-01` and are for review only.

## Retained incident evidence

Authorization: `NADI-P1-FRESH-001D-OWNER-20261008`; accountable project operator:
Fauzi. Attempt: `001d-coal-flow-20261008`.

Journal: STARTED `2026-10-08T09:38:10.092974Z`, FAILED
`2026-10-08T09:38:11.508768Z`, phase HANDOFF, reason SOURCE_UNAVAILABLE,
source_gets=1. No ACQUIRED or WRITER_STARTED event exists for this attempt.
There is no pending or uncertain Mart writer. No replay occurred.

Private receipt version 1.0 confirms used=1, maximum=5 and checksum matching the
handoff. Handoff has one selected signal result SOURCE_UNAVAILABLE, evidence
null and collector_last_success_at null. Its exact approved plan and canonical
batch schema were already validated. No new source value or quality flags exist.

Pinned launcher SHA256 remains:
`41090b6749306c30fce494ac13f69907f8bd3f302cc5a3ba0e4b8aec88a0f093`.
Executable is an operator-owned private script with absolute pinned paths and
managed source-only configuration loading. The receipt proves the child CLI
ran; launcher/configuration initialization failure is not the observed stage.

Original report, journal, receipt, handoff, launcher and before/after evidence
were fingerprinted privately; their bytes, permissions and modification
timestamps are preserved. No private artifacts, source URLs or credentials are
included in this document. Existing application/container logs supplied no
manual-attempt diagnostic marker. Host CLI output was discarded by the launcher
boundary; the Collector catches the exception before returning its handoff.

## Failure stage and GET accounting

```text
cockpit condition refresh
  → checked local launcher
  → picollector condition-evidence
  → source-only managed config / typed approved plan
  → GovernedSourceBoundary.get_evidence_snapshot
  → get_attribute → list_attributes → get_element
  → budget wrapper for GET /elements/{explicit_element_ref}
  → PiClient.request / get_json OR immediate element/Database-link validation
  → caught exception → SOURCE_UNAVAILABLE handoff and counted receipt
  → refresh rejection before Mart writer
```

The last confirmed source-stage milestone is the **first counted AF Element
metadata operation**. The exception can be in transport/HTTP handling or the
first element identity/Database-link validation. The database GET, direct
attribute list, attribute metadata GET and snapshot were not reached.

| Accounting | Historical observation |
|---|---|
| Budget-admitted GET attempts | 1 |
| HTTP transport calls recorded | NOT_OBSERVABLE |
| Requests actually transmitted on the network | NOT_OBSERVABLE |
| Responses received / HTTP status | NOT_OBSERVABLE |
| Confirmed successful source responses | none retained; this is not proof of zero responses |
| Automatic retries | none: configured adapters retry total=0; no loop/retry in this path |
| Diagnostic-task live PI / Maximo GETs | 0 / 0 |

The counter increments after the request-shape/origin guard, before the
underlying client request. It counts attempted operations, including failures;
it is not a server receipt or packet counter. No second five-GET budget exists.

## Candidate failure categories

| Candidate | Classification | Evidence / remaining limit |
|---|---|---|
| Launcher invocation / arguments | RULED_OUT | Pinned executable, completed child, valid typed handoff and count receipt |
| Managed source configuration loading | RULED_OUT as an initialization failure | Source-only loader completed before the counted operation; complete Basic auth configuration; no manual dotenv fallback. Credential correctness is not inferred. |
| URL syntax/origin/root guard rejection | RULED_OUT for first budget admission | Resolution guard completed before used became 1. Endpoint identity matches worker. REST endpoint response/availability remains NOT_OBSERVABLE. |
| Authentication / authorization | NOT_OBSERVABLE | No retained HTTP status; Basic mode is not proof of credentials or AF access permissions |
| TLS validation | NOT_OBSERVABLE | Both verify TLS; public CA bundle identical. Historical TLS outcome absent. |
| Network / DNS / routing / timeout | NOT_OBSERVABLE | Host and container namespaces differ; no historical transport outcome retained |
| First AF identity / Database-link validation | NOT_OBSERVABLE | A first 200 response with inconsistent identity/link also yields used=1; later lineage stages were not reached |
| Request budget / method guard rejection | RULED_OUT | Receipt maximum=5, used=1; permitted first Element GET; later budget exhaustion cannot explain this count |
| HTTP response / JSON shape / size | NOT_OBSERVABLE | Status/body discarded; several errors produce identical receipt |
| Loss of safe failure category | CONFIRMED | Broad exception catch only emits SOURCE_UNAVAILABLE; no private error code survives |

No HTTP 401/403, certificate failure, routing failure or AF discrepancy is
asserted as the incident's actual cause. It is impossible to recover the lost
exception from these artifacts alone.

## Working worker versus manual refresh

| Dimension | Technical worker | Manual refresh |
|---|---|---|
| API endpoint | Same scheme, host, port and API root | Same; no raw source URL disclosed |
| Authority | Accepted Compose environment from platform with existing overrides | Explicit private platform source-only loader |
| Config mode | Existing legacy loader allowed; both local/home dotenv files absent | managed; no dotenv fallback |
| Authentication mode | Basic | Basic; credential values/principal equality were not inspected or hashed |
| TLS | verify=true | verify=true, default because explicit key absent |
| Timeout / spacing / cap | 30 seconds / ≥1 second / 1 MiB | same |
| HTTP dependencies | requests 2.34.2, urllib3 2.8.0, certifi 2026.7.22 | same |
| Runtime | Python 3.12.15 / OpenSSL 3.5.7 | Python 3.14.7 / OpenSSL 3.5.9 |
| Trust bundle | Public CA bytes identical | identical |
| Proxy / CA env overrides | None present; HOME exists, no .netrc | sanitized env; none present, no HOME forwarded |
| Session | trust_env=true; adapter retries=0 | same; isolated child source env |
| Network | Existing Docker bridge namespace | Host namespace |
| Endpoint class | streams/{registry_attribute}/value | elements/{explicit_element}, then governed lineage and one approved value |

The latest local stored-data evidence shows normal technical cycles completing
433/433 with zero errors. This proves the worker's stream-read path works in its
own context. It does not prove AF metadata permissions, successful lineage
validation, host reachability or the manual request's HTTP outcome. Consequently
worker health and this manual failure can coexist; an exact causal difference
cannot be selected from the retained evidence.

## Source-free reproduction

On immutable baseline code, eight mocked first-request cases—TLS, timeout,
connection, HTTP 401, HTTP 403, HTTP 503, unexpected JSON shape and incorrect
Element identity—all produced one counted GET and the same unavailable/null
handoff. The fixture knows responses exist for the HTTP/lineage examples and do
not exist for transport exceptions; the old receipt does not distinguish them.

All network transport is mocked. No DNS/authentication/source probe occurs.
Candidate tests further prove sanitized categories, no retries, five-GET bound,
sixth-request rejection before transport, receipt hash linkage, strict signal
identity matching, zero writer invocation and accepted evidence preservation.

## Candidate diagnostic correction

**Fix required: YES, for observability.** This is not a retroactive source repair.

PI client failures carry a typed allowlisted SourceFailureCode. The governed
handoff catch copies only this enum into a private diagnostic accumulator;
unknown errors become SOURCE_CAUSE_UNKNOWN. It never inspects exception strings,
causes, raw URLs, response bodies, sensitive headers or credential values.

The Collector `--diagnostics` option writes private **receipt v1.1**:

```json
{
  "contract_version": "1.1",
  "source_gets": 1,
  "max_source_gets": 5,
  "handoff_sha256": "<exact-private-handoff-checksum>",
  "source_failures": [{"signal_id": "<approved-signal-id>", "code": "SOURCE_TLS_FAILED"}]
}
```

This JSON is a synthetic example, not a diagnosis of the historical failure.

Allowed codes: SOURCE_AUTH_FAILED (401/403), SOURCE_TLS_FAILED, SOURCE_TIMEOUT,
SOURCE_CONNECT_FAILED, SOURCE_HTTP_ERROR, SOURCE_CONTRACT_INVALID,
SOURCE_BUDGET_EXHAUSTED, SOURCE_OPERATION_REJECTED, SOURCE_CAUSE_UNKNOWN.

The refresh consumer validates receipt version, exact fields, budget, handoff
checksum, unique failure signal IDs and exact unavailable-result membership.
It accepts only known codes, retains reason SOURCE_UNAVAILABLE and adds
source_failure_code to the private FAILED journal and sanitized CLI result.
Arbitrary strings or mismatched signal diagnostics fail closed. A cross-project
test checks the producer enum and consumer validation vocabulary agree.

Receipt v1.0 remains readable and default Collector output remains v1.0 without
the flag. Legacy unavailable receipts explicitly mean unknown cause. The
canonical evidence batch contract/schema, API, Mart schema, admission rules,
credential separation, request spacing, cap and five-GET maximum are unchanged.

The candidate runner asks its local Collector for --diagnostics. Both reviewed
operator tools must be promoted together before using that path. An older CLI
rejects the unknown flag before any source request; no silent fallback or retry
is added. No current launcher, executable, image or runtime has been changed.

Codes identify an error category, not packet transmission, equipment health,
freshness or automatic remediation. No scheduler or retry is introduced.

## Regression and tests

Accepted Coal Flow A value stays 53.48906326293945 Ton/h, NUMERIC; source
`2026-10-08T05:01:15.404006Z`, collected `2026-10-08T05:01:21.125301Z`, projected
`2026-10-08T05:02:50.342471Z`; quality true/false/false/false; collector success
NULL. Mapping VERIFIED=1 / PROPOSED=0; approved signal=1; latest/state=1/1.
Final read-only verification confirms all nine original artifacts (including
modification times), accepted pilot rows, all 23 container identities/images/
start times/restart counts and serving release source remain unchanged. NADI
health, factual overview, integration status and pilot condition evidence return
HTTP 200. The reader has no write/table ownership/admin privileges.

Normal background acquisition progressed independently: latest successful PI
cycle started `2026-10-08T10:04:12.674444Z`, finished
`2026-10-08T10:13:30.776422Z`, 433/433, errors=0; registry=490, active=433,
snapshots=433. Maximo latest observed incremental finished
`2026-10-08T10:17:39.271391Z`, 25 rows seen, errors=0; WO cursor present and
recovery floor remains `2026-08-21T03:56:54Z` with exactly one floor record.
Registered assets=845; both factual Mart projection states remain SUCCEEDED.
Reader remains SELECT-only. Original journal has only its prior dry-run and
failed live attempt. BFPT remains frozen; PI_AF_KKS_LOOKUP_UNRESOLVED stays open.

On the candidate checkout, using the existing isolated Python dependencies:

```bash
cockpit_python=/home/john-d/.codex/worktrees/nadi-p1-freshness-release/reliability-knowledge-starter/reliability-cockpit/.venv/bin/python
collector_python=/home/john-d/.codex/worktrees/nadi-p1-freshness-release/reliability-knowledge-starter/pi-collector/.venv/bin/python
# Run each command from its candidate subproject; imports use candidate src.
# reliability-cockpit: full suite, explicit disposable in-memory legacy DB
env -i PATH=/home/linuxbrew/.linuxbrew/bin:/usr/bin:/bin HOME=/home/john-d \
  COCKPIT_CONFIG_MODE=managed DATABASE_URL=sqlite:// \
  "$cockpit_python" -m unittest discover -s tests
# 316 tests: 231 PASS, 85 SKIP (78 opt-in PostgreSQL, 7 opt-in Compose).

# Run the seven skipped Compose cases without deployment
env -i PATH=/home/linuxbrew/.linuxbrew/bin:/usr/bin:/bin HOME=/home/john-d \
  COCKPIT_CONFIG_MODE=managed DATABASE_URL=sqlite:// NADI_COMPOSE_TESTS=1 \
  PYTHONPATH=tests "$cockpit_python" -m unittest test_runtime_wiring.ComposeRuntimeTest
# 7 tests: 7 PASS, 0 SKIP.

# pi-collector: full suite
env -i PATH=/usr/bin:/bin HOME=/home/john-d PI_CONFIG_MODE=managed \
  "$collector_python" -m unittest discover -s tests
# 191 tests: 180 PASS, 11 SKIP (optional DB/live integration flags unset).

git diff --check
```

Python paths and complete command/count logs are recorded privately. Existing
UI dependencies were reused via a temporary link in the candidate checkout only;
the link was removed after validation and is not committed.
One initial full run omitted the SQLite test DSN and two legacy smoke tests
attempted an unavailable default local DB; explicit in-memory configuration
corrected the test invocation. No operational DB was used or changed by tests.
No production source test flags are enabled. No operational schema migration is
executed. No code or fixtures rely on production credentials.

## Safety and next authorization

For this diagnostic task: PI GET=0, Maximo GET=0, source writes=0, condition
projection/approval/mapping mutation=0, registry/history/discovery=0, DDL=0,
service restart/deployment=0, DB reset/truncate/new DB=0, CEMS/NK changes=0.
Normal already-authorized background collectors continue independently.

Before another live refresh:

1. Review/merge the diagnostic PR if accepted; promote the matching operator
   tools under a separately authorized deployment and record exact release,
   executable and pinned launcher identities. Do not run candidate code here.
2. Verify the original journal and absence of pending writer/concurrent refresh,
   exact unique mapping/signal/baseline, accepted evidence and source config using
   source-free checks. Keep all freshness settings unset.
3. Obtain a new explicit owner authorization identifying accountable operator,
   one unique attempt/reference and total maximum source GETs. The previous
   authorization is spent; no retry or authentication probe is implied.
4. Use the authoritative private journal and code-only receipt. Stop on the first
   invalid/unavailable result, preserve accepted evidence, and do not retry.
   Replay is allowed only after a confirmed successful acceptance.

No additional engineering freshness threshold is justified by this failed
observation or forensic work.
