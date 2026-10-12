// Separate disposable causal diagnostic, NOT a Next/application remediation.
// Never run inside a serving worker. No networking, DB, inspector or forced GC.
const fs=require('node:fs'),Module=require('node:module'),v8=require('node:v8');
const [mode,bundle,duration='60']=process.argv.slice(2);
if(process.version!=='v22.23.1'||!['plain','flight'].includes(mode)||!/^\d+$/.test(duration)||Number(duration)>300)throw Error('Invalid diagnostic runtime/arguments');
if(mode==='flight') {
  const original=Module._extensions['.js'];
  Module._extensions['.js']=function(module,filename) {
    if(filename!==bundle)return original(module,filename);
    const code=fs.readFileSync(filename,'utf8');
    const needle='pendingOperations=new Map,lastRanAwait=null';
    if(code.split(needle).length!==2)throw Error('Locked Flight shape not recognized');
    // Expose only the already-rooted debug Map. Do not change its callbacks,
    // pruning, links or eviction. No installed dependency file is written.
    module._compile(code.replace(needle,'pendingOperations=(globalThis.__NADI_DIAGNOSTIC_OPERATIONS=new Map),lastRanAwait=null'),filename);
  };
  require(bundle);
  Module._extensions['.js']=original;
}
function graph() {
  const map=globalThis.__NADI_DIAGNOSTIC_OPERATIONS;
  if(!map)return {map_size:null,nodes:null,truncated:false};
  const seen=new Set(),todo=Array.from(map.values());let maxPreviousDepth=0;
  while(todo.length&&seen.size<500000) {
    const node=todo.pop();if(!node||typeof node!=='object'||seen.has(node))continue;
    seen.add(node);todo.push(node.previous,node.awaited);
  }
  // Bound depth measurement separately; never dereference WeakRefs or owners.
  let sampled=0;
  for(const node of map.values()) {
    if(sampled++>=32)break;let n=node,depth=0;const chain=new Set();
    while(n&&typeof n==='object'&&!chain.has(n)&&depth<500000){chain.add(n);depth++;n=n.previous;}
    maxPreviousDepth=Math.max(maxPreviousDepth,depth);
  }
  return {map_size:map.size,nodes:seen.size,truncated:todo.length>0,max_previous_depth_sample:maxPreviousDepth};
}
let running=true,iterations=0;const start=Date.now();
(async function disposableLongLivedAwaitContext(){
  while(running) {
    await new Promise(resolve=>setImmediate(resolve));
    await Promise.resolve();await Promise.resolve();await Promise.resolve();iterations++;
  }
})();
const timer=setInterval(()=>{
  const heap=process.memoryUsage(),elapsed=(Date.now()-start)/1000;
  const metadata=graph();
  fs.writeSync(1,JSON.stringify({mode,elapsed,iterations,...heap,heapLimit:v8.getHeapStatistics().heap_size_limit,...metadata})+'\n');
  // A diagnostic stop, not a framework safeguard change. The normal V8 limit
  // remains enabled. Avoid deliberately exhausting a busy development host.
  if(elapsed>=Number(duration)||heap.heapUsed>512*1024*1024||metadata.truncated){running=false;clearInterval(timer);}
},1000);
