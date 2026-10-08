"""Case lifecycle; identities and canonical references supplied by server adapters."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Protocol
from uuid import uuid4

from sqlalchemy import select, func, or_
from src.domain.engineering import (EngineeringCase, CaseDraft, CaseStatus, CaseEvent,
    Principal, Role, EngineeringError, InvestigationNote, ReviewDecision, EvidenceReference, EvidenceKind)
from src.repositories.engineering import CaseRow


class EvidenceCatalog(Protocol):
    def registered(self, asset_id: str) -> bool: ...
    def resolve(self, asset_id: str, kind: EvidenceKind, record_id: str,
                mode: str, linked_by: str, linked_at: datetime) -> EvidenceReference: ...


class CaseService:
    def __init__(self, repository, evidence_catalog: EvidenceCatalog, directory, *, enabled=False, clock=None):
        self.repo, self.catalog, self.directory = repository, evidence_catalog, directory
        self.enabled = enabled
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def gate(self, actor):
        if not self.enabled:
            raise EngineeringError("FEATURE_DISABLED", 404)
        if not isinstance(actor, Principal):
            raise EngineeringError("AUTHENTICATION_REQUIRED", 401)
        if not actor.roles or len(actor.asset_ids) > 1000:
            raise EngineeringError("FORBIDDEN", 403)

    def authorize(self, actor, asset_id, case=None, reviewer=False):
        self.gate(actor)
        if asset_id not in actor.asset_ids:
            raise EngineeringError("NOT_FOUND", 404)
        if reviewer:
            if Role.REVIEWER not in actor.roles or (case and actor.principal_id in {case.created_by, case.assigned_engineer}):
                raise EngineeringError("INDEPENDENT_REVIEWER_REQUIRED", 403)
        elif Role.AUTHOR not in actor.roles or (case and actor.principal_id not in {case.created_by, case.assigned_engineer}):
            raise EngineeringError("FORBIDDEN", 403)

    def visible(self, actor, case):
        self.gate(actor)
        if not case or case.canonical_asset_id not in actor.asset_ids or (
            Role.REVIEWER not in actor.roles and actor.principal_id not in {case.created_by, case.assigned_engineer}):
            raise EngineeringError("NOT_FOUND", 404)
        return case

    def assignment(self, asset, assignee):
        if assignee is not None:
            principal = self.directory(assignee)
            if not isinstance(principal, Principal) or Role.AUTHOR not in principal.roles or asset not in principal.asset_ids:
                raise EngineeringError("INVALID_ASSIGNEE", 422)

    def get(self, actor, case_id):
        self.gate(actor)
        return self.repo.transact(lambda c: self.visible(actor, self.repo.get(c, case_id)))

    def list(self, actor, *, asset_id=None, status=None, offset=0, limit=25):
        self.gate(actor)
        if not 1 <= limit <= 100 or not 0 <= offset <= 10000:
            raise EngineeringError("INVALID_PAGINATION", 422)
        def read(c):
            doc = CaseRow.document
            where = [doc["canonical_asset_id"].as_string().in_(actor.asset_ids)]
            if Role.REVIEWER not in actor.roles:
                where.append(or_(doc["created_by"].as_string() == actor.principal_id,
                                 doc["assigned_engineer"].as_string() == actor.principal_id))
            if asset_id is not None:
                where.append(doc["canonical_asset_id"].as_string() == asset_id)
            if status is not None:
                where.append(doc["status"].as_string() == CaseStatus(status).value)
            total = c.execute(select(func.count()).select_from(CaseRow).where(*where)).scalar_one()
            rows = c.execute(select(doc).where(*where).order_by(doc["updated_at"].as_string().desc(), CaseRow.case_id)
                .offset(offset).limit(limit)).scalars()
            items = [EngineeringCase.model_validate(row) for row in rows]
            return dict(items=items, total=total, offset=offset, limit=limit, has_more=offset+len(items)<total)
        return self.repo.transact(read)

    def history(self, actor, case_id, offset=0, limit=50):
        self.gate(actor)
        if not 0 <= offset <= 10000 or not 1 <= limit <= 100:
            raise EngineeringError("INVALID_PAGINATION", 422)
        def read(c):
            self.visible(actor, self.repo.get(c, case_id))
            return self.repo.history(c, case_id, offset, limit)
        return self.repo.transact(read)

    def live_evidence(self, actor, case_id, reference_id):
        case = self.get(actor, case_id)
        ref = next((r for r in case.evidence if r.reference_id == reference_id), None)
        if ref is None:
            raise EngineeringError("EVIDENCE_NOT_FOUND", 404)
        if ref.mode == "FROZEN_SNAPSHOT":
            return ref
        resolved = self.checked_reference(case.canonical_asset_id, ref.kind, ref.record_id,
                                          ref.mode, actor.principal_id, self.clock())
        return resolved.model_copy(update={"reference_id": ref.reference_id, "linked_by": ref.linked_by, "linked_at": ref.linked_at})

    def checked_reference(self, asset, kind, record_id, mode, actor_id, now):
        ref = self.catalog.resolve(asset, kind, record_id, mode, actor_id, now)
        if not isinstance(ref, EvidenceReference) or (ref.canonical_asset_id, ref.kind, ref.record_id, ref.mode) != (asset, kind, record_id, mode):
            raise EngineeringError("EVIDENCE_IDENTITY_INVALID", 422)
        if (ref.linked_by, ref.linked_at) != (actor_id, now):
            raise EngineeringError("EVIDENCE_PROVENANCE_INVALID", 422)
        return ref

    def command(self, actor, action, payload, request_id, *, case_id=None, expected_revision=0):
        self.gate(actor)
        actions = {"CREATE", "UPDATE", "NOTE", "LINK", "SUBMIT", "REVIEW", "REVISE", "REOPEN"}
        if action not in actions or not isinstance(payload, dict):
            raise EngineeringError("INVALID_COMMAND", 422)
        if (action == "CREATE" and (case_id is not None or expected_revision != 0)) or (action != "CREATE" and (not case_id or type(expected_revision) is not int or expected_revision < 1)):
            raise EngineeringError("INVALID_REVISION", 422)
        required = {"NOTE": {"text"}, "LINK": {"kind", "record_id", "mode"}, "SUBMIT": set(), "REVIEW": {"decision", "reason"}, "REVISE": {"reason"}, "REOPEN": {"reason"}}
        if action in required and set(payload) != required[action]:
            raise EngineeringError("INVALID_CONTRACT", 422)
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", request_id or ""):
            raise EngineeringError("INVALID_REQUEST_ID", 422)
        fingerprint = sha256(json.dumps(dict(action=action, payload=payload, case_id=case_id,
            expected_revision=expected_revision), sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        def write(c):
            current = self.repo.get(c, case_id) if case_id else None
            draft = CaseDraft.model_validate(payload) if action == "CREATE" else None
            asset = draft.canonical_asset_id if draft else self.visible(actor, current).canonical_asset_id
            self.authorize(actor, asset, current, reviewer=action in {"REVIEW", "REOPEN"})
            replay = self.repo.receipt(c, actor.principal_id, request_id, fingerprint)
            if replay is not None:
                return replay
            if not self.catalog.registered(asset):
                raise EngineeringError("ASSET_NOT_REGISTERED", 422)
            now = self.clock()
            reason = payload.get("reason") if action not in {"CREATE", "UPDATE"} else None
            if action == "CREATE":
                self.assignment(asset, draft.assigned_engineer)
                data = dict(**draft.model_dump(mode="json"), case_id="case:"+str(uuid4()),
                    created_at=now, updated_at=now, created_by=actor.principal_id, revision=1)
            else:
                if current.revision != expected_revision:
                    raise EngineeringError("REVISION_CONFLICT")
                data = current.model_dump(mode="json")
                data.update(revision=current.revision+1, updated_at=now)
                if action in {"UPDATE", "NOTE", "LINK", "SUBMIT"} and current.status != CaseStatus.DRAFT:
                    raise EngineeringError("INVALID_TRANSITION")
                if action == "UPDATE":
                    draft = CaseDraft.model_validate(payload)
                    if draft.canonical_asset_id != asset:
                        raise EngineeringError("ASSET_IMMUTABLE", 422)
                    self.assignment(asset, draft.assigned_engineer)
                    data.update(draft.model_dump(mode="json"))
                elif action == "NOTE":
                    note = InvestigationNote(note_id="note:"+str(uuid4()), text=payload["text"], actor=actor.principal_id, created_at=now)
                    if not note.text.strip():
                        raise EngineeringError("INVALID_NOTE", 422)
                    data["notes"] = [*current.notes, note]
                elif action == "LINK":
                    kind = EvidenceKind(payload["kind"])
                    ref = self.checked_reference(asset, kind, payload["record_id"], payload["mode"], actor.principal_id, now)
                    if any((r.kind, r.record_id) == (ref.kind, ref.record_id) for r in current.evidence):
                        raise EngineeringError("DUPLICATE_EVIDENCE")
                    data["evidence"] = [*current.evidence, ref]
                elif action == "SUBMIT":
                    data["status"] = CaseStatus.IN_REVIEW
                elif action == "REVIEW":
                    if current.status != CaseStatus.IN_REVIEW:
                        raise EngineeringError("INVALID_TRANSITION")
                    if not payload["reason"].strip():
                        raise EngineeringError("REVIEW_RATIONALE_REQUIRED", 422)
                    decision = ReviewDecision(reviewer=actor.principal_id, decision=payload["decision"], rationale=payload["reason"], decided_at=now)
                    data.update(status=decision.decision, review=decision)
                elif action in {"REVISE", "REOPEN"}:
                    required = CaseStatus.REJECTED if action == "REVISE" else CaseStatus.APPROVED
                    if current.status != required or not reason or not reason.strip():
                        raise EngineeringError("INVALID_TRANSITION")
                    data.update(status=CaseStatus.DRAFT, review=None)
                else:
                    raise EngineeringError("UNSUPPORTED_ACTION", 422)
            case = EngineeringCase.model_validate(data)
            changed = tuple(k for k, v in case.model_dump(mode="json").items()
                if not current or v != current.model_dump(mode="json")[k])
            event = CaseEvent(case_id=case.case_id, revision=case.revision, previous_revision=expected_revision,
                actor=actor.principal_id, action=action, occurred_at=now, changed_fields=changed, reason=reason)
            self.repo.save(c, case, event, expected_revision, actor.principal_id, request_id, fingerprint)
            return case
        return self.repo.transact(write)
