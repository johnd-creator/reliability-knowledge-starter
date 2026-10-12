import assert from "node:assert/strict";
import {createRequire} from "node:module";
import {readFileSync} from "node:fs";
const require=createRequire(import.meta.url),path=require.resolve("../next.config.js"),before=process.env.NODE_ENV;
try{
 for(const mode of ["development","production"]){
  process.env.NODE_ENV=mode;delete require.cache[path];const config=require(path);
  if(mode==="production")assert.equal(config.webpack,undefined);
  else{
   const compiler={cache:{type:"filesystem"},plugins:["keep-existing-plugins"]};
   assert.equal(config.webpack(compiler,{dev:true}),compiler);assert.equal(compiler.cache,false);
   assert.deepEqual(compiler.plugins,["keep-existing-plugins"]);
   const productionCompiler={cache:{type:"filesystem"}};config.webpack(productionCompiler,{dev:false});assert.deepEqual(productionCompiler.cache,{type:"filesystem"});
  }
 }
 const controller=readFileSync("../../deploy/development/frontend_preview.py","utf8");
 assert.match(controller,/max-old-space-size=2048/);assert.doesNotMatch(controller,/__NEXT_DISABLE_MEMORY_WATCHER|expose-gc|optimize-for-size/);
 console.log("Development memory checks PASS: dev filesystem cache disabled; production/HMR/heap safeguards preserved");
}finally{if(before===undefined)delete process.env.NODE_ENV;else process.env.NODE_ENV=before;delete require.cache[path];}
