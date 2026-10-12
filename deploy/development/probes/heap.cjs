// Disposable processes only. In-process inspector has no listening TCP port.
const fs = require('node:fs');
const v8 = require('node:v8');
const inspector = require('node:inspector');
const {PerformanceObserver} = require('node:perf_hooks');
const out = process.env.NADI_PROBE_DIR;
if (out) {
  if(process.env.NADI_PROBE_FLIGHT_PATH) {
    const Module=require('node:module'),original=Module._extensions['.js'];
    Module._extensions['.js']=function(module,filename) {
      if(filename!==process.env.NADI_PROBE_FLIGHT_PATH)return original(module,filename);
      const code=fs.readFileSync(filename,'utf8'),needle='pendingOperations=new Map,lastRanAwait=null';
      const hash=require('node:crypto').createHash('sha256').update(code).digest('hex');
      if(hash!=='f5642afec1b380029730444582c0af19300709dcb586f91c96cb002fc8bffddb')throw Error('Unknown locked Flight bytes');
      if(code.split(needle).length!==2)throw Error('Unknown locked Flight shape');
      // Read-only access to an already-live hook root, disposable worker only.
      module._compile(code.replace(needle,'pendingOperations=(globalThis.__NADI_DIAGNOSTIC_OPERATIONS=new Map),lastRanAwait=null'),filename);
    };
  }
  const append = (kind, row) => fs.appendFileSync(`${out}/${kind}-${process.pid}.jsonl`, JSON.stringify({at:Date.now(), pid:process.pid, ppid:process.ppid, ...row})+'\n', {mode:0o600});
  const sample = (reason='timer') => append('heap', {reason, title:process.title, ...process.memoryUsage(), heapLimit:v8.getHeapStatistics().heap_size_limit, spaces:v8.getHeapSpaceStatistics(), resources:process.getActiveResourcesInfo()});
  sample('startup');
  setInterval(sample, 5000).unref();
  if(process.env.NADI_PROBE_FLIGHT_PATH)setInterval(()=>{
    const map=globalThis.__NADI_DIAGNOSTIC_OPERATIONS;
    if(!map)return;
    const seen=new Set(),owners=new Set(),todo=Array.from(map.values()),tags={};
    let stacks=0,weakRefs=0;
    while(todo.length&&seen.size<500000) {
      const n=todo.pop();if(!n||typeof n!=='object'||seen.has(n))continue;
      seen.add(n);todo.push(n.previous,n.awaited);tags[n.tag]=(tags[n.tag]??0)+1;
      if(n.owner)owners.add(n.owner);if(Array.isArray(n.stack))stacks+=n.stack.length;
      if(n.promise instanceof WeakRef)weakRefs++;
    }
    append('flight',{mapSize:map.size,ancestryNodes:seen.size,truncated:todo.length>0,owners:owners.size,stackFrames:stacks,weakRefs,tags});
  },120000).unref();
  new PerformanceObserver(list => {
    for (const e of list.getEntries()) append('gc', {kind:e.detail.kind, duration:e.duration, start:e.startTime, ...process.memoryUsage()});
  }).observe({entryTypes:['gc']});
  const session = new inspector.Session();
  session.connect();
  const post = (method, params={}) => new Promise((resolve,reject) => session.post(method,params,(e,r)=>e?reject(e):resolve(r)));
  let busy=false, saved=0;
  post('HeapProfiler.startSampling',{samplingInterval:512*1024}).then(() => {
    setInterval(async () => {
      if(busy)return; busy=true;
      try {
        const {profile}=await post('HeapProfiler.getSamplingProfile');
        const data=JSON.stringify(profile);
        // Bound raw profiles to 64 MiB/process; don't retain profiles in memory.
        if(saved+Buffer.byteLength(data)<=64*1024*1024) {
          fs.writeFileSync(`${out}/alloc-${process.pid}-${Date.now()}.heapprofile`,data,{mode:0o600});
          saved+=Buffer.byteLength(data);
        }
        append('profiler',{bytes:Buffer.byteLength(data),saved});
      } catch(e) {append('profiler',{error:e.name});}
      finally {busy=false;}
    },120000).unref();
  }).catch(e=>append('profiler',{error:e.name}));
}
