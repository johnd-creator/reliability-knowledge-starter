"""Offline unittest runner: deny live network/DB; never load private dotenv files."""
import os,sys,unittest,json
from unittest.mock import patch
from pathlib import Path
root=Path(__file__).resolve().parents[1]
os.chdir(root);sys.path[:0]=[str(root),str(root/'tests')]
for key in list(os.environ):
    if key.startswith(('MAXIMO_','PG','NADI_','RELIABILITY_')) or key=='DATABASE_URL':os.environ.pop(key)
from sqlalchemy.engine import Engine
original_connect=Engine.connect
blocked=[]
def deny(*a,**k):
    blocked.append('UNEXPECTED_EXTERNAL_IO')
    raise AssertionError('UNEXPECTED_EXTERNAL_IO')
def guarded_connect(engine,*a,**k):
    if engine.url.get_backend_name()=='sqlite' and engine.url.database in (None,'',':memory:'):
        return original_connect(engine,*a,**k)
    return deny()
with patch('socket.socket.connect',deny),patch('socket.create_connection',deny),patch('sqlalchemy.engine.Engine.connect',guarded_connect),patch('src.config.load_dotenv',return_value=False):
    suite=unittest.defaultTestLoader.discover('tests') if len(sys.argv)==1 else unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
data={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),'blocked_external_io':len(blocked),'success':result.wasSuccessful() and not blocked}
print(json.dumps(data));sys.exit(not data['success'])
