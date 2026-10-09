"""Real browser→Next proxy→fixture backend→PostgreSQL acceptance."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
output=Path(os.environ.get('NADI_QA_BROWSER_OUTPUT','/tmp/nadi-d5-browser'))
if output.parent!=Path('/tmp') or not output.name.startswith('nadi-'):raise RuntimeError('disposable browser output only')
output.mkdir(exist_ok=True)
asset='asset:MAXIMO:MXASSET:BSR:IP:SYNTHETIC-A'
# Read exact fixture identity from the canonical test definition, not inferred.
import ast
source=ast.parse((Path(__file__).resolve().parents[1]/'test_asset_af_mapping_admin.py').read_text())
asset=next(ast.literal_eval(n.value) for n in source.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ASSET_ID' for t in n.targets))
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True);page=browser.new_page(ignore_https_errors=True,viewport={'width':1365,'height':1000})
 page.goto('https://localhost:13035/engineering/qa');page.get_by_role('heading',name='Engineering backend workspace').wait_for()
 def login(proof):
  page.get_by_label('Verified test proof').fill(proof)
  with page.expect_response(lambda r:'/api/engineering-qa/session' in r.url and r.request.method=='GET') as reply:page.get_by_role('button',name='Establish session',exact=True).click()
  assert reply.value.status==200
  page.get_by_text('Subject:',exact=False).wait_for();results.append('trusted session '+proof)
 def command(module,record,action,body):
  page.get_by_label('Module',exact=True).select_option(module)
  page.get_by_label('Record ID (empty to create)').fill(record)
  page.get_by_label('Action',exact=True).select_option(action)
  page.get_by_label('Canonical command JSON').fill(json.dumps(body))
  with page.expect_response(lambda r:'/api/engineering-qa/'+module in r.url and r.request.method in {'POST','PUT'}) as reply:page.get_by_role('button',name='Send controlled command').click()
  assert reply.value.status in {200,201},reply.value.text();row=reply.value.json();results.append(module+':'+(action or 'create'));return row
 def step(module,row,action,fields={},actor=None):
  if actor:login(actor)
  ident=row.get('record_id',row.get('case_id'));return command(module,ident,action,{'request_id':module+'-'+action+'-'+str(row['revision']),'expected_revision':row['revision'],**fields})
 login('qa-engineer-proof');page.get_by_label('Canonical asset',exact=True).fill(asset)
 with page.expect_response(lambda r:'asset-context' in r.url) as reply:page.get_by_role('button',name='Read asset context').click()
 assert reply.value.status==200;results.append('authorized asset context')
 inspection=command('inspections','','',{'request_id':'browser-inspection','draft':{'canonical_asset_id':asset,'method':'VIBRATION','method_version':'proposal-1','inspector_ref':'author','inspected_at':'2026-10-09T00:00:00Z','measurements':[{'quantity':'velocity','value':None,'unit':'mm/s'}],'observations':['Browser fixture observation'],'interpretations':['Human hypothesis']}})
 inspection=step('inspections',inspection,'submit')
 inspection=step('inspections',inspection,'begin_review',{'reason':'Independent review'},'qa-reviewer-proof')
 inspection=step('inspections',inspection,'review',{'decision':'APPROVED','reason':'Reviewed fixture'})
 login('qa-engineer-proof')
 case=command('cases','','',{'request_id':'browser-case','draft':{'canonical_asset_id':asset,'title':'Fixture investigation','problem_statement':'Human observation requires investigation','investigation':{'hypotheses':['Human hypothesis']}}})
 case=step('cases',case,'evidence',{'kind':'MANUAL_INSPECTION','record_id':inspection['record_id'],'mode':'FROZEN_SNAPSHOT'})
 case=step('cases',case,'submit')
 case=step('cases',case,'review',{'decision':'APPROVED','reason':'Independent case review'},'qa-reviewer-proof')
 login('qa-engineer-proof')
 rec=command('recommendations','','',{'request_id':'browser-recommendation','draft':{'canonical_asset_id':asset,'case_ref':case['case_id'],'rationale':'Reviewed observation','proposed_action':'Local follow-up only','evidence_selections':[{'kind':'MANUAL_INSPECTION','record_id':inspection['record_id']}]}})
 rec=step('recommendations',rec,'submit')
 rec=step('recommendations',rec,'review',{'decision':'APPROVED','reason':'Independent proposal review'},'qa-reviewer-proof')
 rec=step('recommendations',rec,'followup',{'status':'PLANNED','reason':'Local fixture follow-up'},'qa-engineer-proof')
 page.get_by_role('button',name='Load records').click();page.wait_for_timeout(500)
 for width in (390,768,1365):
  page.set_viewport_size({'width':width,'height':1000});page.screenshot(path=str(output/f'qa-{width}.png'),full_page=True)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'overflow {width}'
  results.append('responsive '+str(width))
 page.reload();login('qa-engineer-proof');page.get_by_label('Module',exact=True).select_option('recommendations')
 with page.expect_response(lambda r:'/recommendations?' in r.url) as reply:page.get_by_role('button',name='Load records').click()
 assert reply.value.status==200 and reply.value.json()['total']==1;results.append('durable records after browser reload')
 browser.close()
(output/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps({'passed':len(results),'results':results}))
