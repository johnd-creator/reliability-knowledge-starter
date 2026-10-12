// Private, bounded diagnostics in disposable FIX-05 workers only; no TCP inspector.
const fs=require('node:fs'),v8=require('node:v8'),path=require('node:path');
const out=process.env.NADI_RETAINER_DIR,mode=process.env.NADI_RETAINER_MODE;
if(!out||!out.startsWith('/tmp/nadi-fix05-private/')||fs.realpathSync(out)!==out)throw Error('Private disposable directory required');
process.umask(0o077);
const MIB=1048576,append=(kind,row)=>fs.appendFileSync(`${out}/${kind}-${process.pid}.jsonl`,JSON.stringify({at:Date.now(),pid:process.pid,ppid:process.ppid,...row})+'\n',{mode:0o600});
if(mode==='node-source-map-off'){const original=process.setSourceMapsEnabled.bind(process);process.setSourceMapsEnabled=enabled=>{append('source-map-request',{requested:enabled});original(false);};original(false);}
if(mode==='graph'){
 const Module=require('node:module'),original=Module._extensions['.js'];
 Module._extensions['.js']=function(module,filename){
  if(filename!==process.env.NADI_RETAINER_FLIGHT)return original(module,filename);
  const code=fs.readFileSync(filename,'utf8'),needle='pendingOperations=new Map,lastRanAwait=null';
  if(require('node:crypto').createHash('sha256').update(code).digest('hex')!=='f5642afec1b380029730444582c0af19300709dcb586f91c96cb002fc8bffddb'||code.split(needle).length!==2)throw Error('Locked Flight mismatch');
  module._compile(code.replace(needle,'pendingOperations=(globalThis.__NADI_DIAGNOSTIC_OPERATIONS=new Map),lastRanAwait=null'),filename);
 };
 setInterval(()=>{
  const map=globalThis.__NADI_DIAGNOSTIC_OPERATIONS;if(!map)return;
  const seen=new Set(),todo=Array.from(map.values());
  while(todo.length&&seen.size<500000){const n=todo.pop();if(!n||typeof n!=='object'||seen.has(n))continue;seen.add(n);todo.push(n.previous,n.awaited);}
  append('graph',{entries:map.size,nodes:seen.size,truncated:todo.length>0});
 },120000).unref();
}
if(['sampled','graph'].includes(mode)){
 const session=new(require('node:inspector').Session)();session.connect();
 const post=(method,params={})=>new Promise((resolve,reject)=>session.post(method,params,(e,r)=>e?reject(e):resolve(r)));
 let busy=false,saved=0;
 post('HeapProfiler.startSampling',{samplingInterval:512*1024}).then(()=>{
  setInterval(async()=>{if(busy)return;busy=true;try{
   const {profile}=await post('HeapProfiler.getSamplingProfile'),data=JSON.stringify(profile);
   if(saved+Buffer.byteLength(data)<=64*MIB){fs.writeFileSync(`${out}/alloc-${process.pid}-${Date.now()}.heapprofile`,data,{mode:0o600});saved+=Buffer.byteLength(data);}
  }finally{busy=false;}},120000).unref();
 });
}
const {PerformanceObserver}=require('node:perf_hooks');
new PerformanceObserver(list=>{for(const e of list.getEntries())append('gc',{kind:e.detail.kind,duration:e.duration,...process.memoryUsage()});}).observe({entryTypes:['gc']});
const sample=()=>append('heap',{...process.memoryUsage(),heapLimit:v8.getHeapStatistics().heap_size_limit,spaces:v8.getHeapSpaceStatistics(),code:v8.getHeapCodeStatistics(),nativeSourceMaps:process.sourceMapsEnabled,resources:process.getActiveResourcesInfo()});
sample();setInterval(sample,5000).unref();
let capturing=false;
setInterval(()=>{
 const file=out+'/capture-request.json';if(capturing||!fs.existsSync(file))return;
 const request=JSON.parse(fs.readFileSync(file));if(request.pid!==process.pid)return;
 if(![6].includes(request.step)||request.stage!=='SYNTHETIC_CHECKPOINT')throw Error('Invalid snapshot request');
 capturing=true;fs.unlinkSync(file);
 const available=Number(fs.readFileSync('/proc/meminfo','utf8').match(/MemAvailable:\s+(\d+)/)[1])*1024;
 const memory=Number(fs.readFileSync('/sys/fs/cgroup'+fs.readFileSync('/proc/self/cgroup','utf8').trim().split('::')[1]+'/memory.current'));
 const used=process.memoryUsage().heapUsed;
 if(process.env.NADI_RETAINER_CAPTURE==='gc'){
  if(used>550*MIB||memory>1300*MIB||available<1200*MIB){fs.writeFileSync(out+`/capture-${request.step}.json`,JSON.stringify({refused:true,policy:'GC_ONLY',reason:'GC_RESOURCE_PREFLIGHT',heap:used,cgroup:memory,available}),{mode:0o600});return;}
  const start=Date.now(),codeBefore=v8.getHeapCodeStatistics();
  try{
   const objectCount=v8.queryObjects(Object,{format:'count'}); // Node-supported, experimental; forces full GC, no object values exposed.
   fs.writeFileSync(out+`/capture-${request.step}.json`,JSON.stringify({refused:false,policy:'QUERY_OBJECTS_FULL_GC_NO_SNAPSHOT',elapsed_ms:Date.now()-start,pid:process.pid,object_count_current_realm:objectCount,pre_heap:used,post_heap:process.memoryUsage().heapUsed,memory:process.memoryUsage(),code_before:codeBefore,code_after:v8.getHeapCodeStatistics(),nativeSourceMaps:process.sourceMapsEnabled}),{mode:0o600});sample();capturing=false;
  }catch(error){fs.writeFileSync(out+`/capture-${request.step}.json`,JSON.stringify({refused:true,reason:'GC_API_ERROR'}),{mode:0o600});}return;
 }
 if(used>550*MIB||memory>1300*MIB||available<3000*MIB){fs.writeFileSync(out+`/capture-${request.step}.json`,JSON.stringify({refused:true,reason:'SNAPSHOT_RESOURCE_PREFLIGHT',heap:used,cgroup:memory,available}),{mode:0o600});return;}
 const target=out+`/checkpoint-${request.step}.heapsnapshot`,fd=fs.openSync(target,'wx',0o600),start=Date.now();let bytes=0,failed=false;const digest=require('node:crypto').createHash('sha256');
 try{
  const stream=v8.getHeapSnapshot(); // Snapshot forces collection and blocks; shared across controls.
  stream.on('data',chunk=>{bytes+=chunk.length;if(bytes>384*MIB){failed=true;stream.destroy(Error('SNAPSHOT_BYTE_BUDGET'));return;}fs.writeSync(fd,chunk);digest.update(chunk);});
  stream.on('error',()=>{failed=true;});
  stream.on('close',()=>{fs.closeSync(fd);fs.writeFileSync(out+`/capture-${request.step}.json`,JSON.stringify({refused:failed,bytes,elapsed_ms:Date.now()-start,pid:process.pid,pre_heap:used,post_heap:process.memoryUsage().heapUsed,sha256:failed?null:digest.digest('hex')}),{mode:0o600});sample();capturing=false;});
 }catch(e){fs.closeSync(fd);fs.writeFileSync(out+`/capture-${request.step}.json`,JSON.stringify({refused:true,reason:'CAPTURE_ERROR'}),{mode:0o600});}
},1000).unref();
