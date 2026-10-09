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
 app=FastAPI(title='NADI disposable Engineering QA',docs_url=None,redoc_url=None)
 dep=authority.dependency()
 for router in (build_session_router(authority,enabled=True),build_router(cases,enabled=True,trusted_principal_dependency=dep),build_inspection_router(inspections,enabled=True,trusted_principal_dependency=dep),build_recommendation_router(recommendations,enabled=True,trusted_principal_dependency=dep),build_asset_context_router(context,enabled=True,trusted_principal_dependency=dep)):app.include_router(router)
 @app.middleware('http')
 async def private(request,call_next):
  response=await call_next(request);response.headers['Cache-Control']='no-store';response.headers['X-Content-Type-Options']='nosniff';return response
 return app
