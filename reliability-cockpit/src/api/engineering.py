"""Disabled/test-only versioned contracts. Production create_app never mounts this.

A future reviewed bootstrap must supply trusted authentication, browser CSRF
protection, an application writer and asset-authorized local evidence adapters.
No environment/header identity construction and no database lookup here.
"""
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field, ValidationError
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import CaseDraft, CaseStatus, EvidenceKind, EngineeringError


class Change(EvidenceModel):
    request_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    expected_revision: int = Field(ge=1)


class CreateRequest(EvidenceModel):
    request_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    draft: CaseDraft


class UpdateRequest(Change):
    draft: CaseDraft


class NoteRequest(Change):
    text: str = Field(min_length=1, max_length=12000)


class LinkRequest(Change):
    kind: EvidenceKind
    record_id: str = Field(min_length=1, max_length=240, pattern=r"^[a-zA-Z0-9_.:-]+$")
    mode: Literal["LIVE_REFERENCE", "FROZEN_SNAPSHOT"]


class ReviewRequest(Change):
    decision: Literal["APPROVED", "REJECTED"]
    reason: str = Field(min_length=1, max_length=6000)


class ReasonRequest(Change):
    reason: str = Field(min_length=1, max_length=6000)


def build_router(service, *, enabled=False, trusted_principal_dependency=None):
    router = APIRouter(prefix="/v1/engineering", tags=["engineering-candidate"])
    # Enabling a flag cannot create an unauthenticated router.
    if not enabled or not service.enabled or trusted_principal_dependency is None:
        return router

    def invoke(operation):
        try:
            return operation()
        except EngineeringError as error:
            raise HTTPException(error.status, detail={"code": error.code}) from None
        except (ValidationError, ValueError, KeyError, TypeError):
            raise HTTPException(422, detail={"code": "INVALID_CONTRACT"}) from None

    @router.get("/cases")
    def cases(asset_id: str | None = Query(None, max_length=200), status: CaseStatus | None = None,
              offset: int = Query(0, ge=0, le=10000), limit: int = Query(25, ge=1, le=100),
              actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.list(actor, asset_id=asset_id, status=status, offset=offset, limit=limit))

    @router.get("/cases/{case_id}")
    def case(case_id: str, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.get(actor, case_id))

    @router.get("/cases/{case_id}/history")
    def history(case_id: str, offset: int = Query(0, ge=0, le=10000), limit: int = Query(50, ge=1, le=100), actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.history(actor, case_id, offset, limit))

    @router.get("/cases/{case_id}/evidence/{reference_id}")
    def evidence(case_id: str, reference_id: str, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.live_evidence(actor, case_id, reference_id))

    @router.post("/cases", status_code=201)
    def create(body: CreateRequest, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.command(actor, "CREATE", body.draft.model_dump(mode="json"), body.request_id))

    @router.put("/cases/{case_id}")
    def update(case_id: str, body: UpdateRequest, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.command(actor, "UPDATE", body.draft.model_dump(mode="json"), body.request_id,
                                              case_id=case_id, expected_revision=body.expected_revision))

    def mutation(action, model):
        # Explicit factories preserve concrete request model annotations for FastAPI.
        def endpoint(case_id, body, actor):
            payload = body.model_dump(mode="json", exclude={"request_id", "expected_revision"})
            return invoke(lambda: service.command(actor, action, payload, body.request_id,
                case_id=case_id, expected_revision=body.expected_revision))
        return endpoint

    @router.post("/cases/{case_id}/notes")
    def note(case_id: str, body: NoteRequest, actor=Depends(trusted_principal_dependency)):
        return mutation("NOTE", NoteRequest)(case_id, body, actor)

    @router.post("/cases/{case_id}/evidence")
    def link(case_id: str, body: LinkRequest, actor=Depends(trusted_principal_dependency)):
        return mutation("LINK", LinkRequest)(case_id, body, actor)

    @router.post("/cases/{case_id}/submit")
    def submit(case_id: str, body: Change, actor=Depends(trusted_principal_dependency)):
        return mutation("SUBMIT", Change)(case_id, body, actor)

    @router.post("/cases/{case_id}/review")
    def review(case_id: str, body: ReviewRequest, actor=Depends(trusted_principal_dependency)):
        return mutation("REVIEW", ReviewRequest)(case_id, body, actor)

    @router.post("/cases/{case_id}/revise")
    def revise(case_id: str, body: ReasonRequest, actor=Depends(trusted_principal_dependency)):
        return mutation("REVISE", ReasonRequest)(case_id, body, actor)

    @router.post("/cases/{case_id}/reopen")
    def reopen(case_id: str, body: ReasonRequest, actor=Depends(trusted_principal_dependency)):
        return mutation("REOPEN", ReasonRequest)(case_id, body, actor)

    return router
