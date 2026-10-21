"""Offline planning only. Never connects to a database or runs an import."""
import argparse,json,sys
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.services.pdm_history_staging import write_plan

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',required=True,help='Private JSON array of path/source_ref objects')
    p.add_argument('--catalog',required=True);p.add_argument('--out',required=True);p.add_argument('--as-of',required=True)
    p.add_argument('--existing',help='Private exact event-key/record-id/rows inventory; no automatic overwrite')
    p.add_argument('--date-rules',help='Explicit source-hash/sheet/axis/locator/encoding/rationale rules')
    a=p.parse_args();read=lambda path:json.loads(Path(path).read_text()) if path else []
    manifest=write_plan(read(a.sources),a.catalog,a.out,as_of=date.fromisoformat(a.as_of),existing=read(a.existing),date_rules=read(a.date_rules) or {})
    print(json.dumps({'plan_id':manifest['plan_id'],'counts':manifest['counts'],'reason_counts':manifest['reason_counts'],'database_writes':0},sort_keys=True))

if __name__=='__main__':main()
