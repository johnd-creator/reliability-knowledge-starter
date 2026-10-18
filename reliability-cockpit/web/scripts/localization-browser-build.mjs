// Creates a browser test bundle in /tmp. Does not start Next, a QA server, or another frontend.
import {createRequire} from 'node:module';
import {mkdtempSync,writeFileSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
const require=createRequire(import.meta.url),compiled=require('next/dist/compiled/webpack/webpack');compiled.init();
export async function browserBundle(entry="scripts/localization/entry.tsx"){
 const temp=mkdtempSync(join(tmpdir(),'nadi-id-browser-'));
 const tsLoader=join(temp,'ts-loader.cjs'),cssLoader=join(temp,'css-loader.cjs');
 writeFileSync(tsLoader,`const ts=require(${JSON.stringify(require.resolve('typescript'))});module.exports=function(source){return ts.transpileModule(source,{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022,esModuleInterop:true}}).outputText;};`);
 writeFileSync(cssLoader,`module.exports=function(source){const names=[...source.matchAll(/\\.([a-zA-Z][\\w-]*)/g)].map(m=>m[1]);return 'module.exports='+JSON.stringify(Object.fromEntries(names.map(n=>[n,n])))+';';};`);
 const compiler=compiled.webpack({mode:'development',devtool:false,plugins:[new compiled.webpack.DefinePlugin({'process.env':JSON.stringify({NODE_ENV:'development'})})],entry:resolve(entry),output:{path:temp,filename:'candidate.js'},resolve:{extensions:['.tsx','.ts','.js','.json'],modules:[resolve('node_modules'),'node_modules'],alias:{'@':resolve('.'),'next/navigation':resolve('scripts/localization/next-navigation.ts'),'next/link':resolve('scripts/localization/next-link.tsx'),'next/image':resolve('scripts/localization/next-image.tsx')}},module:{rules:[{test:/\.tsx?$/,exclude:/node_modules/,use:tsLoader},{test:/\.css$/,use:cssLoader}]},optimization:{minimize:false}});
 await new Promise((done,fail)=>compiler.run((err,stats)=>{compiler.close(()=>{});if(err)return fail(err);if(stats.hasErrors())return fail(new Error(stats.toString({all:false,errors:true})));done();}));
 return {temp,js:readFileSync(join(temp,'candidate.js')),css:['app/design-tokens.css','app/globals.css','app/login-refresh.css','app/engineering.css','components/EngineeringWorkflow.module.css','app/enterprise.css'].map(f=>readFileSync(f,'utf8').replace(/@import[^;]+;/g,'')).join('\n')};
}
