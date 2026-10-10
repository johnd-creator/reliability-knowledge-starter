"""Mounted exclusively in authenticated development QA factory."""
from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.human_records import build_record_router
from src.api.engineering import Change, ReasonRequest
from src.domain.advisory import AdvisoryDraft
from src.domain.engineering import EngineeringError


def build_advisory_router(service, *, enabled=False, trusted_principal_dependency=None):
    return build_record_router(service, prefix='/v1/engineering/advisories', draft_model=AdvisoryDraft,
        extra_actions={'PUBLISH': ReasonRequest, 'WITHDRAW': ReasonRequest}, enabled=enabled,
        trusted_principal_dependency=trusted_principal_dependency)


def build_inbox_router(service, *, enabled=False, trusted_principal_dependency=None):
    router = APIRouter(prefix='/v1/engineering/inbox')
    if not enabled or not service.enabled or trusted_principal_dependency is None:
        return router
    def invoke(fn):
        try:
            return fn()
        except EngineeringError as error:
            raise HTTPException(error.status, detail={'code': error.code}) from None
    @router.get('')
    def listing(offset: int = Query(0, ge=0, le=10000), limit: int = Query(25, ge=1, le=100), actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.inbox(actor, offset=offset, limit=limit))
    @router.get('/{record_id}')
    def detail(record_id: str, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.recipient_get(actor, record_id))
    @router.post('/{record_id}/acknowledge')
    def acknowledge(record_id: str, body: Change, actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.acknowledge(actor, record_id, body.request_id, body.expected_revision))
    return router
