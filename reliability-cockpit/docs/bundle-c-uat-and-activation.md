# Bundle C UAT and activation handoff

**Non-operational candidate. No deployment or production migration authorized.**
Phase1 remains CURRENT/PARTIAL. Phase2 candidate is tested; product acceptance and
activation are BLOCKED until the following independent gates have accountable approval.

## Activation blockers and owners

| Gate | Required evidence / accountable owner | Current status |
|---|---|---|
| Enterprise identity | Identity/security owner selects real provider; trusted server assertion validation, stable subject, asset directory, role version/revocation and no browser authority | BLOCKED; contracts/fixture provider only |
| Session bootstrap | Reviewed server-side login callback, secure cookie/session, explicit origins/CSRF, bounded lifetime and durable revocation/audit; no public fixture login | BLOCKED; factory contracts tested |
| Existing application store | Platform owner proves existing legacy Cockpit store identity, separate from canonical Mart; reader/writer/service/session roles, controlled grants and backup | BLOCKED; disposable fixtures only |
| Application migration ownership | Reviewed checksum ledger/status/apply/rollback procedure for existing application migrations002/003/004; wrong-store fail-closed preflight | BLOCKED; these files are not auto-run or a production migration runner |
| PdM method fields | Responsible PdM engineers approve each method version, required/optional fields, instrument/context metadata, units and reviewer qualifications | ENGINEER_FIELDS_PENDING; no invented method thresholds |
| Reviewer/PIC/team directories | Asset scopes and independent review policy; responsibility/delegation evidence, reviewer reassignment/escalation rules | BLOCKED; injected fixtures only |
| Attachments | Private storage, allowlisted content validation/scanning, ownership/retention, download authorization and confidentiality | BLOCKED; metadata only, actual upload disabled |
| Operational UI integration | Reviewed trusted backend transport, exact contract translation, session handling and real approved local records; never browser actor/role authority | BLOCKED; development browser-memory demo only |
| Operational UAT | Engineer/security/owner sign-off of the matrix below and explicit deployment approval | PENDING |
| New source coverage | Domain-specific source owner approval, exact endpoint/fields/scope/budget and canonical mapping; separate authorized collection task | PENDING; manifest is proposal only |

Do not weaken source identity or freshness gates to clear any blocker. This bundle
does not reopen Phase1 evidence, signal approvals, mappings, source acquisition or
temporary freshness-policy approvals/checkpoints/expiry.

## Engineer field decisions

Use [the six-method engineer input packet](manual-pdm-engineer-input.md). For every
method record procedure/version owner, original quantities/units, measurement-point
identity, nullable/required context, calibration/timezone, reviewer qualification,
retention/confidentiality and delegated recording policy. Proposals for vibration,
IR, MCSA, tribology, DGA and Other remain proposals. A generic measurement value or
unknown observation never implies a normal result, technical limit or health score.

## Candidate UAT matrix

| Workflow | Acceptance evidence |
|---|---|
| Select registered asset | Authorized canonical identity, same-asset local context; unknown classification explicit; source/collection/projection times distinct |
| Partial/unavailable data | Pagination and coverage visible; missing/unmapped/invalid/unavailable not represented as healthy or successful collection |
| Inspect | Choose method/version; preserve null/zero/text/boolean, original unit/time/context; observations distinct from hypotheses; no file upload |
| Submit | Validate generic data envelope; DRAFT → SUBMITTED, no automatic approval; creator/inspector attributed from trusted principal |
| Independent review | SUBMITTED → UNDER_REVIEW; reviewer cannot be creator/contributor/PIC; approve/return/reject with reason; reviewed evidence read-only |
| Revision/conflict | Returned/rejected revisions preserve audit; stale editor receives REVISION_CONFLICT; unsaved input retained, no overwrite |
| Engineering Case | Explicit frozen approved inspection references plus canonical evidence; hypotheses remain human interpretation; independent case decision |
| Recommendation | Approved same-asset case + supporting evidence required; reviewed revision pin preserved; bounded action/PIC/date; existing WO informational |
| Follow-up | Local planned/in-progress/completed report; independent verification requires frozen evidence; no maintenance execution/WO closure implied |
| Action Board | Scoped actual local workflow statuses, overdue dates and unresolved evidence; no manufactured operating statistics or scoring |
| Trust/security | Forged browser roles ignored; revoked session, wrong origin/CSRF, foreign assets and invalid provider records denied; no source or Mart writes |
| UI/accessibility | Keyboard controls, visible labels/focus/errors, screen reader context, desktop/mobile navigation, no horizontal page overflow; real engineer UAT still required |

Candidate evidence is in [integrated acceptance](bundle-c-integrated-acceptance.md).
Browser-local reviewer simulation is not operational authorization. Backend fixture
acceptance separately uses server-issued sessions and an independent reviewer.

## Migration, provisioning and rollback proposal

1. Keep operational APIs unmounted while reviewing the complete C1–C7 stack.
2. Inventory and privately back up the **existing application database**, never the
   canonical Mart for this application work. Verify expected existing schema anchors.
3. Review a deliberate application migration ledger/runner and checksums for
   migrations002 Engineering,003 identity and004 human records. Status must be
   non-destructive; explicit apply must fail closed. Never use Mart or legacy
   blanket initialization to create these application relations.
4. Provision least privilege: transactional current-record/session tables may get
   explicitly scoped writer rights; audit/events/receipts get SELECT/INSERT only.
   Readers SELECT only. No superuser, ownership, source credentials, Mart writer,
   DELETE/TRUNCATE or runtime DDL. Test grants and wrong-database protections.
5. Bundle C adds JSON document fields/workflows; it introduces **no additional SQL
   migration** and executes no production migration. ManualInspection1.1 preserves
   reading legacy1.0 IN_REVIEW. Cases/recommendations retain IN_REVIEW. Legacy
   recommendations without reviewed-case pins remain readable but cannot advance
   approval/follow-up until deliberately revised and resubmitted.
6. Before any future activation, complete identity, directories, field approvals,
   secure storage policy and UAT. Request explicit operational deployment authority.
7. Rollback proposal: disable/unmount application routes and revoke application
   sessions/writer grants; return to reviewed prior application release. Preserve
   all application records, immutable revision/audit history and accepted source
   evidence. Do not down-migrate, delete records, restore over current evidence or
   rewind Maximo cursors. If a rollback reader cannot parse1.1 records, retain a
   compatible reviewed reader or disable reads; never erase accepted records to
   accommodate old code. No rollback executed by this bundle.

Next recommended bundle: enterprise identity/bootstrap and deliberate application
provisioning contracts, followed by engineer field validation and operational UAT.
Expanded Maximo collection remains a separate approval track. Maximo/PI remain
STRICTLY source READ-ONLY; recommendations never create/change/close a Maximo WO.
