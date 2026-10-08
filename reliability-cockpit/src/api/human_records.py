"""Test-only router factories. Production application does not import this module."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import create_model, ValidationError
from src.api.engineering import Change, ReviewRequest, ReasonRequest
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import EngineeringError
from src.domain.manual_inspection import InspectionDraft


def build_record_router(service, *, prefix, draft_model, enabled=False, trusted_principal_dependency=None, extra_actions=None):
    router = APIRouter(prefix=prefix, tags=["human-record-candidate"])
    if not enabled or not service.enabled or trusted_principal_dependency is None:
        return router
    create_request = create_model(service.kind + "Create", __base__=EvidenceModel,
                                  request_id=(str, ...), draft=(draft_model, ...))
    update_request = create_model(service.kind + "Update", __base__=Change, draft=(draft_model, ...))

    def invoke(operation):
        try:
            return operation()
        except EngineeringError as error:
            raise HTTPException(error.status, detail={"code": error.code}) from None
        except (ValidationError, ValueError, KeyError, TypeError):
            raise HTTPException(422, detail={"code": "INVALID_CONTRACT"}) from None

    @router.get("")
    def listing(offset: int = Query(0, ge=0, le=10000), limit: int = Query(25, ge=1, le=100),
                actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.list(actor, offset=offset, limit=limit))

    @router.get("/{record_id}")
    def detail(record_id: str, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.get(actor, record_id))

    @router.get("/{record_id}/history")
    def history(record_id: str, offset: int = Query(0, ge=0, le=10000), limit: int = Query(50, ge=1, le=100),
                actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.history(actor, record_id, offset=offset, limit=limit))

    def create(body, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.command(actor, "CREATE", body.draft.model_dump(mode="json"), body.request_id))
    create.__annotations__["body"] = create_request
    router.add_api_route("", create, methods=["POST"], status_code=201)

    def update(record_id: str, body, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.command(actor, "UPDATE", body.draft.model_dump(mode="json"), body.request_id,
            record_id=record_id, expected_revision=body.expected_revision))
    update.__annotations__["body"] = update_request
    router.add_api_route("/{record_id}", update, methods=["PUT"])

    def mutation(action, model):
        def endpoint(record_id: str, body, actor=Depends(trusted_principal_dependency)):
            payload = body.model_dump(mode="json", exclude={"request_id", "expected_revision"})
            return invoke(lambda: service.command(actor, action, payload, body.request_id,
                record_id=record_id, expected_revision=body.expected_revision))
        endpoint.__annotations__["body"] = model
        endpoint.__name__ = service.kind.lower() + "_" + action.lower()
        return endpoint
    actions = {"SUBMIT": Change, "REVIEW": ReviewRequest, "REVISE": ReasonRequest, "REOPEN": ReasonRequest}
    actions.update(extra_actions or {})
    for action, model in actions.items():
        router.add_api_route("/{record_id}/" + action.lower(), mutation(action, model), methods=["POST"])
    return router


def build_inspection_router(service, **kwargs):
    return build_record_router(service, prefix="/v1/engineering/inspections", draft_model=InspectionDraft, **kwargs)
