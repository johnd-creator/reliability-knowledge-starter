"""Explicit isolated factory only; never imported by operational create_app."""
from src.services.application_identity import csrf_for_session
from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import Field
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import EngineeringError
class SessionProof(EvidenceModel):
    proof: str = Field(min_length=1,max_length=8192)
def build_session_router(authority,*,enabled=False,resume_csrf=False):
    router=APIRouter(prefix='/v1/engineering/session')
    if not enabled:return router
    def fail(error):raise HTTPException(error.status,detail={'code':error.code}) from None
    @router.post('')
    def establish(body:SessionProof,request:Request,response:Response):
        if request.headers.get('origin') not in authority.origins:
            raise HTTPException(403,detail={'code':'ORIGIN_DENIED'})
        try:
            token,csrf=authority.establish(body.proof);authority.set_cookie(response,token)
            return {'csrf_token':csrf}
        except EngineeringError as error:fail(error)
    @router.get('')
    def current(request:Request,response:Response):
        try:
            token=request.cookies.get(authority.COOKIE)
            csrf=csrf_for_session(token) if resume_csrf and isinstance(token,str) and 40<=len(token)<=128 else None
            with authority.lease(token,renew_csrf=csrf) as actor:
                response.headers['Cache-Control']='no-store'
                result={'subject':actor.principal_id,'roles':sorted(actor.roles),'asset_ids':sorted(actor.asset_ids)}
                if resume_csrf:result['csrf_token']=csrf
                return result
        except EngineeringError as error:fail(error)
    @router.post('/logout')
    def logout(request:Request,response:Response):
        token=request.cookies.get(authority.COOKIE)
        try:
            # Release row lease before the independent revocation transaction.
            with authority.lease(token,method='POST',origin=request.headers.get('origin'),csrf=request.headers.get('x-csrf-token'),content_type=request.headers.get('content-type')) as actor:pass
            authority.revoke(actor,token)
            response.delete_cookie(authority.COOKIE,path='/',secure=True,httponly=True,samesite='strict')
            response.headers['Cache-Control']='no-store';return {'status':'REVOKED'}
        except EngineeringError as error:fail(error)
    return router
