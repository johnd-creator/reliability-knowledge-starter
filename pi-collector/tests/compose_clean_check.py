"""Validate managed Compose in a clean fixture without source/network operations.

Run from pi-collector: python tests/compose_clean_check.py
Requires Docker Compose CLI only; does not start containers or load real env.
"""
import json,os,subprocess,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE={'PI_WEB_API_BASE_URL','PI_USERNAME','PI_PASSWORD','PI_TOKEN','PI_TIMEOUT_SECONDS',
        'PI_RATE_LIMIT_SECONDS','PI_MAX_RESPONSE_BYTES','PI_VERIFY_TLS'}
with tempfile.TemporaryDirectory() as directory:
    clean=Path(directory)
    (clean/'compose.yaml').write_bytes((ROOT/'compose.yaml').read_bytes())
    # Synthetic values only, never load the existing private operational file.
    sample=(ROOT/'.env.platform.example').read_text()
    sample += '\nPI_USERNAME=fixture-user\nPI_PASSWORD=fixture-only\nPI_SNAPSHOT_INTERVAL_SECONDS=420\n'
    (clean/'.env.platform').write_text(sample)
    environment={'PATH':os.environ['PATH'],'HOME':str(clean),'COMPOSE_DISABLE_ENV_FILE':'1'}
    result=subprocess.run(['docker','compose','--env-file','.env.platform','-f','compose.yaml',
                           '--profile','pi-collection','--profile','pi-maintenance','config','--format','json'],
                          cwd=clean,env=environment,capture_output=True,text=True,check=True)
    services=json.loads(result.stdout)['services']
    worker=services['pi-worker'];assert not worker.get('env_file')
    assert worker['environment']['PI_USERNAME']=='fixture-user'
    assert worker['environment']['PI_PASSWORD']=='fixture-only'
    assert worker['environment']['PI_SNAPSHOT_INTERVAL_SECONDS']=='420'
    assert worker['command'][-1]=='420'
    assert worker['profiles']==['pi-collection']
    assert '--pause-seconds' in worker['command'] and 'backfill' not in worker['command']
    for name,service in services.items():
        if name!='pi-worker':assert not SOURCE & set(service.get('environment',{})),name
    assert services['pi-api']['environment']['PI_SNAPSHOT_INTERVAL_SECONDS']=='420'
    assert not (clean/'pi-collector/.env').exists() and not (clean/'.pi-collector.env').exists()
print('Clean managed Compose: PASS; worker-only source env, no collector/home dotenv; non-default pause 420 preserved; no source/container operations.')
