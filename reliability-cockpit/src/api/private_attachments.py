"""Explicit injected delivery only. No upload route or operational mount."""
from fastapi import APIRouter, Depends, HTTPException
from src.domain.engineering import EngineeringError
from src.services.attachment_recovery import attachment_response


def build_attachment_delivery_router(service, *, enabled=False, trusted_principal_dependency=None):
    router = APIRouter(prefix="/v1/engineering/attachments")
    if not enabled:
        return router
    if trusted_principal_dependency is None:
        raise ValueError("TRUSTED_ATTACHMENT_IDENTITY_REQUIRED")

    @router.get("/{attachment_id}")
    def deliver(attachment_id: str, actor=Depends(trusted_principal_dependency)):
        try:
            metadata, data = service.retrieve(actor, attachment_id)
            return attachment_response(metadata, data)
        except EngineeringError as error:
            raise HTTPException(error.status, detail={"code": error.code}) from None
    return router
