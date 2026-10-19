"""Read-only exact Cockpit coverage against an independently verified own fixture."""
import argparse,dataclasses,json,os,re,stat,sys
from pathlib import Path
from unittest.mock import patch

def parse_arguments(argv=None):
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('context',type=Path)
 parser.add_argument('--source',type=Path,required=True)
 return parser.parse_args(argv)

def validate_context(ctx,context_path,source):
 private=context_path.parent
 info=private.lstat();file_info=context_path.lstat()
 if (private.parent!=Path('/tmp') or not private.name.startswith('nadi-f03-restore-') or
     not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode & 0o077 or
     not stat.S_ISREG(file_info.st_mode) or file_info.st_uid!=os.getuid() or file_info.st_mode & 0o077):
  raise ValueError('unverified private context')
 fixture=Path(ctx['item']['directory'])
 fixture_info=fixture.lstat()
 if (fixture.parent!=Path('/tmp') or not fixture.name.startswith('nadi-f03-restore-') or
     fixture.resolve()!=fixture or not stat.S_ISDIR(fixture_info.st_mode) or
     fixture_info.st_uid!=os.getuid() or fixture_info.st_mode & 0o077 or
     Path(ctx['item']['socket']).resolve()!=fixture/'socket' or
     str(ctx['item']['port']) not in ('16521','16522') or
     not re.fullmatch('[0-9]+',ctx['item']['system_id'])):
  raise ValueError('unverified fixture identity')
 if Path(ctx['component']).resolve()!=source/'reliability-cockpit':raise ValueError('source component mismatch')
 if Path(ctx['output']).resolve().parent!=private:raise ValueError('output must remain in private evidence directory')
 if not re.fullmatch('[a-z][a-z0-9_]{1,62}',ctx['schema']):raise ValueError('unreviewed fixture schema')

def main(argv=None):
 args=parse_arguments(argv)
 context_path=args.context.resolve();ctx=json.loads(context_path.read_text())
 private=Path(ctx['item']['directory'])
 component=Path(ctx['component']).resolve()
 validate_context(ctx,context_path,args.source.resolve())
 sys.dont_write_bytecode=True
 for key in tuple(os.environ):
  if key.startswith(('PG','MAXIMO_','NADI_','RELIABILITY_','COCKPIT_')) or key.endswith(('_DSN','_TOKEN','_PASSWORD','_SECRET')) or key in ('DATABASE_URL','GH_TOKEN'):os.environ.pop(key)
 os.environ['PYTHON_DOTENV_DISABLED']='1'
 import psycopg
 from sqlalchemy.engine import URL
 from sqlalchemy import event,text
 from f03_restore_rehearsal import guard_postgres
 def audit(event,args):
  if event in ('socket.connect','socket.getaddrinfo','socket.sendto','socket.sendmsg','subprocess.Popen','os.system'):raise AssertionError('unexpected worker I/O')
 sys.addaudithook(audit)
 with guard_postgres([(ctx['item']['socket'],ctx['item']['port'])],('nadi_lock_fixture','nadi_lock_reader'),('nadi_lock_disposable',)) as blocked_io,patch('dotenv.load_dotenv',return_value=False),patch('dotenv.main.load_dotenv',return_value=False):
  with psycopg.connect(host=ctx['item']['socket'],port=ctx['item']['port'],user='nadi_lock_fixture',dbname='nadi_lock_disposable',connect_timeout=3) as c:
   assert c.execute('SELECT system_identifier::text FROM pg_control_system()').fetchone()[0]==ctx['item']['system_id']
   assert Path(c.execute('SHOW data_directory').fetchone()[0]).resolve()==private/'data'
   assert c.execute('SHOW listen_addresses').fetchone()[0]==''
  sys.path.insert(0,str(component))
  from src.config import MartDbConfig
  from src.repositories.mart_database import MartDatabase
  from src.repositories.projection_coverage import ProjectionCoverageReader,BoundedRead,CoverageLimits,catalog_signature
  url=URL.create('postgresql+psycopg',username='nadi_lock_reader',database='nadi_lock_disposable',query={'host':ctx['item']['socket'],'port':str(ctx['item']['port'])})
  db=MartDatabase(MartDbConfig(url.render_as_string(hide_password=False)))
  @event.listens_for(db.engine,'connect')
  def path(connection,_):
   from psycopg import sql
   connection.execute(sql.SQL('SET search_path TO {}').format(sql.Identifier(ctx['schema'])));connection.commit()
  try:
   with db.read_snapshot() as session:
    signature=catalog_signature(BoundedRead(session,CoverageLimits()))
   original_rows=BoundedRead.rows
   def observed_rows(self,statement,*args,**kwargs):
    observed=original_rows(self,statement,*args,**kwargs)
    if ctx.get('reported_version_override') and statement=="SELECT current_setting('server_version_num') AS version":
     return [{'version':ctx['reported_version_override']}]
    return observed
   with patch.object(BoundedRead,'rows',new=observed_rows):
    snapshot=ProjectionCoverageReader(db,enabled=True,expected_database='nadi_lock_disposable').read()
   assert not blocked_io,'blocked external I/O attempt'
   result={'signature':signature,'snapshot':dataclasses.asdict(snapshot),'reported_version_override':ctx.get('reported_version_override')}
  finally:db.engine.dispose()
 Path(ctx['output']).write_text(json.dumps(result,indent=2,default=str)+'\n');Path(ctx['output']).chmod(0o600)
 print(json.dumps(result,default=str))

if __name__=='__main__':
 main()
