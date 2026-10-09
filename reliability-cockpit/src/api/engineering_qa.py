"""Dependency-injected disposable QA app. Operational create_app never imports it."""
from fastapi import FastAPI
from src.api.application_session import build_session_router
from src.api.engineering import build_router
from src.api.human_records import build_inspection_router,build_recommendation_router
from src.api.asset_context import build_asset_context_router
from src.domain.engineering import EngineeringError

def create_qa_app(*,authority,cases,inspections,recommendations,context,environment):
 if environment!='development':raise EngineeringError('QA_ONLY',503)
 url=authority.engine.url
 if url.get_backend_name()!='postgresql' or url.host not in {'127.0.0.1','localhost'} or not (url.database or '').endswith('_test'):
  raise EngineeringError('DISPOSABLE_QA_DATABASE_REQUIRED',503)
 for service in (cases,inspections,recommendations):
  if service.repo.engine is not authority.engine:raise EngineeringError('QA_STORE_MISMATCH',503)
 from src.api.qa_limits import QaIngressLimits
 app=FastAPI(title='NADI disposable Engineering QA',docs_url=None,redoc_url=None)
 app.add_middleware(QaIngressLimits,max_bytes=1024*1024,deadline_seconds=15)
 from src.services.local_authentication import LocalIdentityProvider
 from src.api.local_authentication import build_local_login_router
 from fastapi.exceptions import RequestValidationError
 from fastapi.responses import JSONResponse
 @app.exception_handler(RequestValidationError)
 async def invalid_input(request,error):
  # FastAPI's default errors echo request inputs (possibly login passwords).
  return JSONResponse(status_code=422,content={'detail':{'code':'INVALID_REQUEST'}})
 if isinstance(authority.provider,LocalIdentityProvider):
  app.include_router(build_local_login_router(authority,enabled=True))
 dep=authority.dependency()
 for router in (build_session_router(authority,enabled=True,resume_csrf=isinstance(authority.provider,LocalIdentityProvider)),build_router(cases,enabled=True,trusted_principal_dependency=dep),build_inspection_router(inspections,enabled=True,trusted_principal_dependency=dep),build_recommendation_router(recommendations,enabled=True,trusted_principal_dependency=dep),build_asset_context_router(context,enabled=True,trusted_principal_dependency=dep)):app.include_router(router)
 @app.get('/health/live')
 def live():return {'status':'LIVE','scope':'DISPOSABLE_QA'}
 @app.get('/health/ready')
 def ready():
  from sqlalchemy import text
  from fastapi import HTTPException
  try:
   with authority.engine.connect() as c:c.scalar(text('SELECT 1'))
   return {'status':'READY','scope':'APPLICATION_CONNECTIVITY_ONLY'}
  except Exception:raise HTTPException(503,detail={'code':'QA_STORE_UNAVAILABLE'}) from None
 @app.middleware('http')
 async def private(request,call_next):
  response=await call_next(request);response.headers['Cache-Control']='no-store';response.headers['X-Content-Type-Options']='nosniff';return response
 return app
