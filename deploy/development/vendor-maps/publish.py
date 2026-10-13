"""Publish numeric, sanitized trial evidence; never copies raw profiles/journals."""
import argparse,csv,json
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('summary',HERE/'summarize.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('candidate');p.add_argument('output');a=p.parse_args()
out=Path(a.output);out.mkdir(parents=True,exist_ok=True);summaries={}
for value in [a.baseline,a.candidate]:
 root=Path(value).resolve()
 if not str(root).startswith('/tmp/nadi-fix06-private/') or not (root/'result.json').exists():raise ValueError('Completed private trial required')
 s=module.summarize(root);summaries[s['mode']]=s
 (out/(s['mode']+'.json')).write_text(json.dumps(s,indent=2)+'\n')
with (out/'timelines.csv').open('w',newline='') as file:
 writer=csv.writer(file,lineterminator='\n');writer.writerow(['variant','seconds','heap_mib','rss_mib','external_mib','major_gc_observer'])
 for mode,s in summaries.items():
  for r in s['timeline']:writer.writerow([mode,r['seconds'],r['heap_mib'],r['rss_mib'],r['external_mib'],False])
  for r in s['major_gc_timeline']:writer.writerow([mode,r['seconds'],r['heap_mib'],'','',True])
(out/'comparison.json').write_text(json.dumps({mode:{k:v for k,v in s.items() if k not in ['timeline','major_gc_timeline','allocation_profiles']} for mode,s in summaries.items()},indent=2)+'\n')
