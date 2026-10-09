"""Explicit isolated candidate factory; never mounted by production create_app."""
from fastapi import APIRouter, Depends, HTTPException, Query
from src.domain.asset_context import UnifiedAssetContext
from src.domain.engineering import EngineeringError

def build_asset_context_router(service, *, enabled=False, trusted_principal_dependency=None):
    router = APIRouter(prefix="/v1/engineering/asset-context", tags=["asset-context-candidate"])
    if not enabled or not service.enabled or trusted_principal_dependency is None:
        return router
    @router.get("/{asset_id}", response_model=UnifiedAssetContext)
    def read(asset_id: str, offset: int = Query(0, ge=0, le=10000),
             limit: int = Query(25, ge=1, le=100), actor=Depends(trusted_principal_dependency)):
        try:
            return service.read(actor, asset_id, offset=offset, limit=limit)
        except EngineeringError as error:
            raise HTTPException(error.status, detail={"code": error.code}) from None
    return router
