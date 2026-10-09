# C3 — manual inspection workflow candidate

New inspection contract1.1: DRAFT → SUBMITTED → UNDER_REVIEW →
APPROVED / RETURNED / REJECTED. Reviewer starts explicitly and is recorded;
the same independent reviewer makes the decision. Creator, inspector and every
contributor are excluded. RETURNED/REJECTED require REVISE before editing and
resubmitting; APPROVED can only reopen with an independent decision and reason.
No decision deletes earlier snapshots. Receipt replay and CAS use the existing
application repository transaction. Submitted records cannot silently change.

Legacy1.0 IN_REVIEW and approved records remain readable. New SUBMIT clients
must use BEGIN_REVIEW before deciding; this is an intentional candidate workflow
change, not a production migration. Status is in existing JSON documents, so no
new DDL is required. Schema id is1.1 and both historic1.0/new1.1 record versions
are represented. Existing recommendation/case lifecycle is unchanged here.

Generic submission requires at least one measurement or observation, not a
method-specific field/threshold. Unknown measurements/units/times are allowed
and never imply good equipment. Method fields remain ENGINEER_FIELDS_PENDING.
Attachments are existing bounded safe basename/type/size/checksum metadata;
storage/upload/download, source URLs and external fetch remain disabled.

APPROVED records can be read by engineers with the exact asset scope; drafts
remain owner/reviewer scoped. This does not grant mutation or independent-review
authority to a reader. Approved records may become a bounded frozen case evidence
snapshot: measurements preserve value/type/unit/time, observations and hypotheses
remain human content, reviewer/time/revision and SHA256 bind exact accepted
application content. The digest is not a signature or source identity proof.
`REGISTERED` canonical identity is explicitly different from VERIFIED PI mapping.
Only current server-directory identities resolve reviewed records; no browser
actor authority or live-reference promotion. History retains accepted snapshots
even if a later local revision reopens the record.

Production route factories remain default-off/unmounted. Enterprise identity,
writer/migration provisioning, engineer field approval and UAT remain blockers.
