"""GET-only source history through the existing session/asset authority."""
from fastapi import APIRouter, Depends, HTTPException, Query
from src.domain.engineering import EngineeringError


def build_source_history_router(service, *, trusted_principal_dependency):
    router = APIRouter(prefix='/v1/engineering/source-history', tags=['provisional-source-history'])
    def invoke(operation):
        try: return operation()
        except EngineeringError as error: raise HTTPException(error.status, detail={'code':error.code}) from None
    @router.get('/batches')
    def batches(limit:int=Query(10,ge=1,le=100),after:str=Query('',max_length=64),actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.batches(actor,limit=limit,after=after))
    @router.get('')
    def listing(limit:int=Query(25,ge=1,le=100), after:str=Query('',max_length=64),
                source_ref:str|None=Query(None,max_length=80), sheet_index:int|None=Query(None,ge=0,lt=10000),
                classification:str|None=Query(None,max_length=40), kind:str|None=Query(None,max_length=40),
                actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.listing(actor,limit=limit,after=after,source_ref=source_ref,sheet_index=sheet_index,classification=classification,kind=kind))
    @router.get('/{event_key}')
    def detail(event_key:str,offset:int=Query(0,ge=0,le=10000),limit:int=Query(25,ge=1,le=100),actor=Depends(trusted_principal_dependency)):
        return invoke(lambda: service.detail(actor,event_key,offset=offset,limit=limit))
    return router
