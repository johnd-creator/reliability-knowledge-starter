"""Disposable fixture server only; never an operational entry point."""
import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_bundle_d_http import RealHttpQaTest
from src.api.engineering_qa import create_qa_app
from src.services.identity_adapter import EnterpriseIdentityAdapter
from src.domain.engineering import EngineeringError
import uvicorn
if os.environ.get('NADI_DISPOSABLE_QA_ACK')!='fixture-only':raise RuntimeError('explicit disposable fixture acknowledgement required')
class BrowserFixture(RealHttpQaTest):
 def setUp(self):
  from test_bundle_c_integration import BundleCIntegrationTest
  BundleCIntegrationTest.setUp(self)
 def tearDown(self):
  from test_bundle_c_integration import BundleCIntegrationTest
  BundleCIntegrationTest.tearDown(self)
fixture=BrowserFixture();fixture.setUp()
fixture.authority.origins=frozenset({'https://localhost:13035'})
class Verifier:
 def subject(self,proof):
  if proof not in {'qa-engineer-proof','qa-reviewer-proof'}:raise EngineeringError('AUTHENTICATION_REQUIRED',401)
  return {'qa-engineer-proof':'author','qa-reviewer-proof':'reviewer'}[proof]
fixture.authority.provider=EnterpriseIdentityAdapter(Verifier(),fixture.provider)
app=create_qa_app(authority=fixture.authority,cases=fixture.cases,inspections=fixture.inspections,recommendations=fixture.recommendations,context=fixture.context,environment='development')
try:uvicorn.run(app,host='127.0.0.1',port=13036,log_level='warning')
finally:fixture.tearDown()
