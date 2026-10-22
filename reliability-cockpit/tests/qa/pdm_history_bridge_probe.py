"""Test-only injection into unchanged production factory, owned PostgreSQL only."""
from pathlib import Path
import os,json,sys
from unittest.mock import patch
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
T=Path(__file__).resolve().parents[3];D=T/'deploy/development/pdm_history_111/controller';sys.path.insert(0,str(D))
import local_fixture as fixture
root=Path(sys.argv[1]);cfg=json.loads(Path(os.environ['NADI_HISTORY_BRIDGE_CONFIG']).read_text())
engine=create_engine(os.environ['NADI_HISTORY_BRIDGE_TEST_DSN'],hide_parameters=True)
assert engine.url.host=='127.0.0.1' and engine.url.port not in {None,5432,15443} and engine.url.database.startswith('pdm_history_complete_bridge_') and engine.url.database.endswith('_test') and not engine.url.query
fixture.DB=engine.url.database
config={'source_root':str(root),'workflow_sha':'1ec93d6f3507321617903d169451d77fdcc1216e','accounts_file':cfg['accounts_file']}
mode = sys.argv[2] if len(sys.argv)>2 else 'normal'
if mode.startswith('compatibility') or mode=='startup-config-mismatch-denied':
 config['source_root']=cfg['old_source_root']
try:
 if mode!='normal':
  try:
   with patch.object(fixture,'load',return_value=config),patch.object(fixture,'engine_for',return_value=engine):
    special=fixture.compatibility() if mode.startswith('compatibility') else fixture.create_app()
  except RuntimeError as error:
   expected='LOCAL_FIXTURE_IMPORTED_SOURCE_MISMATCH' if mode=='startup-config-mismatch-denied' else 'EXPLICIT_FIXTURE_PREPARATION_REQUIRED'
   assert mode.endswith('denied') and str(error)==expected
   print(json.dumps({'outcome':'REFUSED','code':str(error)}));raise SystemExit(0)
  assert mode=='compatibility-only'
  print(json.dumps(special));raise SystemExit(0)
 with patch.object(fixture,'load',return_value=config),patch.object(fixture,'engine_for',return_value=engine):
  app=fixture.create_app()
 with TestClient(app,base_url='https://localhost:3000') as client:
  assert client.get('/health/ready').status_code==200
  assert client.get('/v1/engineering/inspections').status_code==401
  bad=client.post('/v1/engineering/auth/login',json={'username':'fixture-engineer','password':cfg['password']},headers={'Origin':'https://wrong.invalid'})
  assert bad.status_code==403
  good=client.post('/v1/engineering/auth/login',json={'username':'fixture-engineer','password':cfg['password']},headers={'Origin':'https://localhost:3000'})
  assert good.status_code==200,good.status_code
  assert client.get('/v1/engineering/session').status_code==200
  assert client.get('/v1/engineering/inspections?offset=0&limit=100').status_code==200
  current=client.get('/development/status').json();assert current['source_sha']==current['current_sha']
  source=client.get('/v1/engineering/source-history?limit=1')
  if current['source_sha']=='85e6bb61eb5cb724e436846b9bdeee31709dffd4':assert source.status_code==200 and source.json()['total']==cfg['expected_source_groups']
  else:assert source.status_code==404
 with patch.object(fixture,'load',return_value=config),patch.object(fixture,'engine_for',return_value=engine):probe=fixture.compatibility()
 app.state.fixture.pi.tearDown()
 print(json.dumps({'compatibility':probe,'startup':'PASS','authentication':'PASS','source_sha':current['source_sha'],'source_history':source.status_code,'live_connections':0}))
finally:engine.dispose()
