// Disposable processes only. In-process inspector has no listening TCP port.
const fs = require('node:fs');
const v8 = require('node:v8');
const inspector = require('node:inspector');
const {PerformanceObserver} = require('node:perf_hooks');
const out = process.env.NADI_PROBE_DIR;
if (out) {
  const append = (kind, row) => fs.appendFileSync(`${out}/${kind}-${process.pid}.jsonl`, JSON.stringify({at:Date.now(), pid:process.pid, ppid:process.ppid, ...row})+'\n', {mode:0o600});
  const sample = (reason='timer') => append('heap', {reason, title:process.title, ...process.memoryUsage(), heapLimit:v8.getHeapStatistics().heap_size_limit, spaces:v8.getHeapSpaceStatistics(), resources:process.getActiveResourcesInfo()});
  sample('startup');
  setInterval(sample, 5000).unref();
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
