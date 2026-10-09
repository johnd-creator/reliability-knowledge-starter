"""Real loopback HTTPS socket + disposable PostgreSQL, not TestClient/mock HTTP."""
import os,socket,threading,time,tempfile,subprocess
from pathlib import Path
from datetime import timedelta
import requests,uvicorn
from sqlalchemy import text
from test_engineering_qa import QaFactoryTest
from src.api.engineering_qa import create_qa_app
from src.services.identity_adapter import EnterpriseIdentityAdapter
from src.domain.engineering import EngineeringError

class SocketClient:
 def __init__(self,url):
  self.url=url;self.session=requests.Session();self.session.verify=False
  self.cookies=self.session.cookies
 def request(self,method,path,**kwargs):return self.session.request(method,self.url+path,timeout=15,**kwargs)
 def close(self):self.session.close()

class RealHttpQaTest(QaFactoryTest):
 def application_engine(self):
  from sqlalchemy import create_engine
  from sqlalchemy.engine import make_url
  from src.repositories.application_migrations import ApplicationMigrator
  url=make_url(os.environ['NADI_APPLICATION_TEST_DSN'])
  if url.host not in {'127.0.0.1','localhost'} or not url.database.endswith('_test'):raise RuntimeError('disposable local fixture only')
  engine=create_engine(url)
  with engine.begin() as c:c.exec_driver_sql('DROP SCHEMA public CASCADE; CREATE SCHEMA public')
  ApplicationMigrator(engine,expected_database=url.database,isolated=True).apply()
  return engine

 def setUp(self):
  super().setUp()
  # Test-only proofs map into already-scoped server directory; never in app code.
  directory=self.provider
  class Verifier:
   def subject(self,proof):
    if proof not in {'author','reviewer'}:raise EngineeringError('AUTHENTICATION_REQUIRED',401)
    return proof
  self.authority.provider=EnterpriseIdentityAdapter(Verifier(),directory)
  app=create_qa_app(authority=self.authority,cases=self.cases,inspections=self.inspections,recommendations=self.recommendations,context=self.context,environment='development')
  self.tls=tempfile.TemporaryDirectory();root=Path(self.tls.name)
  subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(root/'key.pem'),'-out',str(root/'cert.pem'),'-days','1','-subj','/CN=localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  os.chmod(root/'key.pem',0o600)
  self.sock=socket.socket();self.sock.bind(('127.0.0.1',0));self.port=self.sock.getsockname()[1]
  self.server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=self.port,ssl_keyfile=str(root/'key.pem'),ssl_certfile=str(root/'cert.pem'),log_level='critical'))
  self.thread=threading.Thread(target=lambda:self.server.run(sockets=[self.sock]),daemon=True);self.thread.start()
  for _ in range(200):
   if self.server.started:break
   time.sleep(.01)
  if not self.server.started:raise RuntimeError('fixture server startup failed')
  self.client.close();self.client=SocketClient('https://127.0.0.1:'+str(self.port))
  self.credentials={}
  for name in ('author','reviewer'):
   response=self.client.request('POST','/v1/engineering/session',json={'proof':name},headers={'Origin':'https://nadi.example.invalid'})
   self.assertEqual(response.status_code,200,response.text)
   self.credentials[name]=(self.client.cookies.get(self.authority.COOKIE),response.json()['csrf_token']);self.client.cookies.clear()
 def tearDown(self):
  self.client.close();self.server.should_exit=True;self.thread.join(10);self.sock.close();self.tls.cleanup();super().tearDown()
 def test_records_survive_connection_reopen_and_conflict(self):
  row=self.create_inspection()
  from sqlalchemy import create_engine
  other=create_engine(self.engine.url)
  with other.connect() as c:self.assertEqual(c.scalar(text('SELECT count(*) FROM nadi_human_record')),1)
  other.dispose()
  submitted=self.step('inspections',row,'submit')
  replay=self.step('inspections',row,'submit');self.assertEqual(replay,submitted)
  self.call('POST','inspections/'+row['record_id']+'/submit',{'request_id':'stale-new-request','expected_revision':1},expected=409)
 def test_forged_session_no_source_mutation_endpoints(self):
  self.client.cookies.set(self.authority.COOKIE,'x'*43)
  self.assertEqual(self.client.request('GET','/v1/engineering/cases').status_code,401)
  for path in ('/maximo/workorders','/v1/engineering/maximo/workorders','/v1/engineering/pi/write'):
   self.assertEqual(self.client.request('POST',path,json={}).status_code,404)
