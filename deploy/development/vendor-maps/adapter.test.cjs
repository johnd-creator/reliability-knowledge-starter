'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {adapt,vendor}=require('./adapter.cjs');
test('default disabled returns identical config without loading dependencies',()=>{const config={};assert.equal(adapt(config,{},{}),config);assert.equal(adapt(config,{}, {NADI_FIX06_VENDOR_MAPS:'0'}),config);});
test('unrecognized flag refuses before mutation',()=>assert.throws(()=>adapt({}, {},{NADI_FIX06_VENDOR_MAPS:'true'}),/explicit flag/));
test('production opt-in refused',()=>assert.throws(()=>adapt({}, {dev:false},{NADI_FIX06_VENDOR_MAPS:'1',NODE_ENV:'production'}),/development only/));
test('official or unrelated root refused',()=>assert.throws(()=>adapt({}, {dev:true},{NADI_FIX06_VENDOR_MAPS:'1',NODE_ENV:'development'}),/disposable root/));
test('vendor path component only; application similar names remain mapped',()=>{for(const name of ['/x/node_modules/next/a.js','C:\\x\\node_modules\\react\\a.js'])assert(vendor.test(name));for(const name of ['/x/app/node_modules-guide.tsx','/x/my_node_modules/a.ts','/x/app/a.tsx','/x/app/a.tsx?alias=/node_modules/react/a.js'])assert(!vendor.test(name));});
// Real locked plugin constructor, synthetic config: refusals must precede mutation.
const fs=require('node:fs'),{createRequire}=require('node:module');
const deps=process.env.NADI_FIX06_TEST_DEPS;
if(deps && process.versions.node==='22.23.1') {
 const root=fs.mkdtempSync('/tmp/nadi-fix06-private/guard-')+'/runs/frontend/reliability-cockpit/web';fs.mkdirSync(root,{recursive:true});
 fs.writeFileSync(root+'/package.json','{}');fs.symlinkSync(fs.realpathSync(deps),root+'/node_modules');
 const local=createRequire(root+'/package.json'),Plugin=local('next/dist/build/webpack/plugins/eval-source-map-dev-tool-plugin').default;
 const bundled=local('next/dist/compiled/webpack/webpack');bundled.init();
 const before=process.cwd();process.chdir(root);
 const context={dev:true,webpack:bundled.webpack};const env={NODE_ENV:'development',NADI_FIX06_VENDOR_MAPS:'1',NADI_FIX06_DISPOSABLE_ROOT:root};
 const make=()=>({mode:'development',devtool:false,cache:false,name:'server',output:{devtoolModuleFilenameTemplate:'[absolute-resource-path]'},plugins:[new Plugin({moduleFilenameTemplate:'[absolute-resource-path]',shouldIgnorePath:()=>false})]});
 try {
  const c=make(),p=c.plugins[0],original=p.options;assert.equal(adapt(c,context,env),c);assert.equal(p.options.exclude,vendor);assert.equal(p.options.shouldIgnorePath,original.shouldIgnorePath);assert.equal(c.devtool,false);
  for(const mutate of [c=>c.plugins.push(c.plugins[0]),c=>c.plugins=[],c=>c.plugins[0].options.noSources=true,c=>c.plugins[0].options.exclude=/./,c=>c.plugins[0].newProperty=true,c=>c.devtool='source-map',c=>c.cache={},c=>c.mode='production',c=>c.plugins[0]=Object.assign({},c.plugins[0]),c=>c.output.devtoolModuleFilenameTemplate='changed']) {
   const c=make();mutate(c);const opts=c.plugins[0]?.options;assert.throws(()=>adapt(c,context,env),/VENDOR_MAP_REFUSED/);assert.equal(c.plugins[0]?.options,opts);
  }
  assert.throws(()=>adapt(make(),{...context,webpack:{}},env),/Webpack identity/);
  assert.throws(()=>adapt(make(),context,{...env,NEXT_RSPACK:'1'}),/acknowledgment/);
  assert.throws(()=>adapt(make(),context,{...env,NADI_FIX06_DISPOSABLE_ROOT:'/tmp/other'}),/acknowledgment/);
  const pkg=local('next/package.json'),version=pkg.version;pkg.version='unknown';
  try {assert.throws(()=>adapt(make(),context,env),/package next/);} finally {pkg.version=version;}
  const read=fs.readFileSync;fs.readFileSync=function(file,...args){if(String(file).endsWith('eval-source-map-dev-tool-plugin.js'))return Buffer.from('changed');return read(file,...args);};
  try {assert.throws(()=>adapt(make(),context,env),/fingerprint/);} finally {fs.readFileSync=read;}
  console.log('16 locked-plugin positive/refusal cases PASS');
 } finally {process.chdir(before);}
}
