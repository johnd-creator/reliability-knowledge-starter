"""Disposable password-login browser fixture. No operational bootstrap/default accounts."""
import os, sys, json, secrets
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_bundle_c_integration import BundleCIntegrationTest
from test_bundle_d_http import RealHttpQaTest
from src.api.engineering_qa import create_qa_app
from src.services.local_authentication import LocalIdentityProvider
from src.domain.engineering import Role
import uvicorn
if os.environ.get("NADI_DISPOSABLE_QA_ACK") != "fixture-only":
    raise RuntimeError("explicit disposable fixture acknowledgement required")
class BrowserFixture(BundleCIntegrationTest):
    application_engine = RealHttpQaTest.application_engine
fixture=BrowserFixture();fixture.setUp()
fixture.authority.origins=frozenset({"https://localhost:13035"})
provider=LocalIdentityProvider(fixture.store,clock=lambda:fixture.now)
admin_password=secrets.token_urlsafe(24)
admin=provider.bootstrap(username="fixture-operator",password=admin_password,assets={fixture.asset},operator_ref="isolated-test")
grant=provider.current_grant(admin)
accounts={"asset":fixture.asset}
for name,role in (("engineer",Role.AUTHOR),("reviewer",Role.REVIEWER)):
    password=secrets.token_urlsafe(24)
    user=provider.create_account(grant,username="fixture-"+name,password=password,roles={role},assets={fixture.asset},require_change=False)
    accounts[name]={"username":"fixture-"+name,"password":password,"user_id":user}
path=Path(os.environ["NADI_LOCAL_TEST_ACCOUNTS"])
if path.parent.parent != Path("/tmp") or not path.parent.name.startswith("nadi-"):
    raise RuntimeError("private disposable fixture directory required")
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,"w") as f:json.dump(accounts,f)
fixture.provider=provider;fixture.authority.provider=provider
app=create_qa_app(authority=fixture.authority,cases=fixture.cases,inspections=fixture.inspections,
    recommendations=fixture.recommendations,context=fixture.context,environment="development")
try:uvicorn.run(app,host="127.0.0.1",port=13036,log_level="warning")
finally:fixture.tearDown();path.unlink(missing_ok=True)
