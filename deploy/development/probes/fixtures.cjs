// In-memory contract fixtures. No DSN, persistence, source requests or real users.
const http=require('node:http'),fs=require('node:fs');
const [web,port,backendSha]=process.argv.slice(2);
if(!/^13\d{3}$/.test(port))throw Error('Disposable QA must use a free 13xxx loopback port');
const fixture=JSON.parse(fs.readFileSync(web+'/fixtures/ux-bundle-b.json'));
const overview=JSON.parse(fs.readFileSync(web+'/fixtures/executive-overview.json'));
const now='2026-10-12T00:00:00Z',asset=fixture.asset.canonical_id;
const reviewed={reviewer:'demo-reviewer',decision:'APPROVED',decided_at:now,rationale:'QA SINTETIS, bukan izin pekerjaan'};
const row={case_id:'case:DEMO-001',title:'QA SINTETIS — Investigasi disposable',problem_statement:'Tidak ada sumber operasional',canonical_asset_id:asset,category:'INVESTIGATION',priority:'NORMAL',assigned_engineer:null,investigation:{observed_symptoms:[],operating_context:'QA SINTETIS',hypotheses:[],observations:[],open_questions:[],proposed_next_checks:[]},status:'APPROVED',revision:2,created_by:'demo-engineer',updated_at:now,review:reviewed,evidence:[],notes:[]};
const recommendation=fixture.recommendations[0];
const advisory={record_id:'advisory:DEMO-001',canonical_asset_id:asset,recommendation_ref:recommendation.record_id,summary:'QA SINTETIS — Pemberitahuan disposable',finding:'Bukan bukti plant',evidence_caveat:'UNKNOWN',audiences:['REVIEWER'],replaces:null,scope:'SYNTHETIC_QA_ONLY_NOT_WORK_AUTHORIZATION',status:'APPROVED',revision:4,created_by:'demo-engineer',updated_at:now,created_at:now,review:reviewed,availability:'IN_APP_QA_AVAILABLE',upstream:{case_id:row.case_id,case_revision:2,case_sha256:'a'.repeat(64),recommendation_id:recommendation.record_id,recommendation_revision:3,recommendation_sha256:'b'.repeat(64),case_reviewer:'demo-reviewer',recommendation_reviewer:'demo-reviewer',recommended_action:recommendation.proposed_action,rationale:recommendation.rationale,responsible_person_ref:null,responsible_team_ref:null,target_date:null,existing_work_order_ref:null,evidence:[]}};
advisory.publication={version:4,published_at:now,published_by:'demo-reviewer',snapshot:structuredClone(advisory)};
const inbox={...advisory.publication,availability:advisory.availability,current_revision:4,acknowledgement:{actor:'demo-author',updated_at:now,status:'ACKNOWLEDGED',meaning:'RECEIPT_ONLY_NOT_APPROVAL_OR_WORK_AUTHORIZATION'},follow_up_status:'PLANNED',viewed_status:'NOT_RECORDED'};
const page=items=>({items,total:items.length,offset:0,limit:25,has_more:false});
const meta=items=>({items,meta:{total:items.length,offset:0,limit:50,has_more:false}});
const sessions=new Set();let count=0;
http.createServer(async(req,res)=>{
  count++;const path=new URL(req.url,'http://127.0.0.1').pathname;
  const send=(status,json,headers={})=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store',...headers});res.end(JSON.stringify(json));};
  const fail=(status,code)=>send(status,{detail:{code}});
  if(path==='/health')return send(200,{status:'ok',fixture:'DISPOSABLE_SYNTHETIC'});
  if(path==='/development/status')return send(200,{environment:'DEVELOPMENT',database:'DISPOSABLE_TEST',database_identity:'IN_MEMORY_FIXTURE_NOT_nadi_live_dev_test',engineering:true,source_sha:backendSha});
  if(path==='/probe-count')return send(200,{count});
  if(path.startsWith('/v1/engineering/')) {
    const relative=path.slice('/v1/engineering/'.length);
    if(relative==='auth/login'&&req.method==='POST') {
      let data='';for await(const part of req){data+=part;if(data.length>4096)return fail(413,'BODY_LIMIT');}
      let input;try{input=JSON.parse(data);}catch{return fail(400,'INVALID');}
      if(input.username!=='DEMO_NOT_AN_ACCOUNT'||input.password!=='DEMO_NOT_A_CREDENTIAL')return fail(401,'AUTHENTICATION_REQUIRED');
      const token=require('node:crypto').randomBytes(24).toString('hex');sessions.add(token);
      return send(200,{authenticated:true},{'Set-Cookie':`probe_session=${token}; Path=/; HttpOnly; SameSite=Strict`});
    }
    const token=(req.headers.cookie??'').match(/(?:^|; )probe_session=([a-f0-9]+)/)?.[1];
    if(!sessions.has(token))return fail(401,'AUTHENTICATION_REQUIRED');
    if(req.method!=='GET')return fail(403,'DISPOSABLE_FIXTURE_READ_ONLY');
    if(relative==='session')return send(200,{subject:'demo-author',roles:['AUTHOR'],asset_ids:[asset],csrf_token:'DEMO_BROWSER_ONLY'});
    if(relative==='advisory-capability')return send(200,{persistence:'READY',scope:'SYNTHETIC_QA_ONLY'});
    const [kind,id,action]=relative.split('/').map(decodeURIComponent);
    const rows={cases:[row],recommendations:fixture.recommendations,inspections:fixture.inspections,advisories:[advisory],inbox:[inbox]}[kind];
    if(!rows)return fail(404,'NOT_FOUND');
    if(action==='history')return send(200,[{revision:1,actor:'demo-engineer',action:'CREATE',occurred_at:now,reason:'QA SINTETIS'}]);
    return send(200,id?rows.find(r=>(r.case_id??r.record_id??r.snapshot?.record_id)===id)??null:page(rows));
  }
  if(req.method!=='GET')return fail(405,'READ_ONLY');
  if(path.includes('decision-overview'))return send(200,overview);
  if(path==='/v1/reliability/assets')return send(200,meta([fixture.asset]));
  if(path.endsWith('/context'))return send(200,{asset:fixture.asset,maintenance:fixture.maintenance,fmea:[],health:[],overhauls:[],rcfa_relationship_status:'UNRESOLVED',relationship_health:{asset_refs_resolved:1,asset_refs_total:1}});
  if(path.endsWith('/health/latest'))return fail(404,'UNKNOWN');
  if(path.endsWith('/condition-evidence'))return send(200,{canonical_asset_id:asset,mapping_readiness:'UNMAPPED',statuses:['UNKNOWN'],expected_signals:0,latest_attempt_at:null,collector_last_success_at:null,items:[]});
  if(path.endsWith('/integration-status'))return send(200,{observed_at:now,coverage:{},components:[]});
  if(path.includes('/maintenance-events'))return send(200,meta(fixture.maintenance));
  if(path.endsWith('/assets/'+encodeURIComponent(asset)))return send(200,fixture.asset);
  // Do not return a list for a missing summary contract: use the app's honest
  // unavailable state instead of an invalid, invented DTO.
  return fail(503,'FIXTURE_CONTRACT_UNAVAILABLE');
}).listen(Number(port),'127.0.0.1',()=>console.log('Disposable fixture ready'));
