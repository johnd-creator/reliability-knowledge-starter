// Measurement-only plugin for archived disposable copies, never the live build.
const fs=require('node:fs');
module.exports=class Probe {
  apply(compiler) {
    let count=0;
    compiler.hooks.done.tap('DisposableNadiHeapProbe',stats=>{
      fs.appendFileSync(process.env.NADI_PROBE_DIR+'/compilers.jsonl',JSON.stringify({at:Date.now(),pid:process.pid,name:compiler.name,count:++count,modules:stats.compilation.modules.size,cache:compiler.options.cache,errors:stats.hasErrors(),...process.memoryUsage()})+'\n',{mode:0o600});
    });
  }
};
