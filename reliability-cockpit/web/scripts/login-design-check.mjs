import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,rmSync,symlinkSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
const require=createRequire(import.meta.url),React=require('react'),{renderToStaticMarkup}=require('react-dom/server');
const temp=mkdtempSync(join(tmpdir(),'nadi-login-'));let count=0;
const check=(name,fn)=>{fn();count++;console.log('PASS '+name);};
const navigation=require.resolve('next/navigation'),original=require.cache[navigation];
try{
 execFileSync(process.execPath,['node_modules/typescript/bin/tsc','components/LoginPage.tsx','components/LocalLogin.tsx','--outDir',temp,'--rootDir','.','--module','commonjs','--target','ES2022','--jsx','react-jsx','--esModuleInterop','--skipLibCheck','--resolveJsonModule','--moduleResolution','node'],{stdio:'pipe'});
 symlinkSync(resolve('node_modules'),join(temp,'node_modules'));
 require.cache[navigation]={id:navigation,filename:navigation,loaded:true,exports:{useRouter:()=>({push(){throw new Error('No navigation during presentation render');}})}};
 const Login=require(join(temp,'components/LocalLogin.js')).default,Page=require(join(temp,'components/LoginPage.js')).default;
 const render=(Component,props={})=>renderToStaticMarkup(React.createElement(Component,props));
 const html=render(Login),page=render(Page);
 check('existing official logo and product identity',()=>{assert.match(page,/logo_nadi/);assert.match(page,/NADI — Platform Analitik Keandalan Aset Pembangkit/);assert.match(page,/PLTU Banten 1 Suralaya/);});
 check('required credentials have labels and autofill semantics',()=>{assert.match(html,/for="[^"]+-username"/);assert.match(html,/autoComplete="username"/);assert.match(html,/autoComplete="current-password"/);assert.equal((html.match(/required=""/g)??[]).length,2);});
 check('empty form cannot submit and has explanatory help',()=>{assert.match(html,/disabled=""[^>]*>Masuk/);assert.match(html,/Nama pengguna dan kata sandi wajib diisi/);assert.match(html,/aria-describedby="[^"]+-help"/);});
 check('no preset identity or credentials',()=>{assert.equal((html.match(/value=""/g)??[]).length,2);assert.doesNotMatch(html,/defaultValue|demo-password|admin123/);});
 check('password visibility remains labeled and controlled',()=>{assert.match(html,/aria-controls="[^"]+-password"/);assert.match(html,/aria-pressed="false"/);assert.match(html,/Tampilkan kata sandi/);});
 check('expired feedback remains announced',()=>{assert.match(render(Login,{expired:true}),/role="status">Sesi Anda berakhir atau dicabut/);});
 check('multiple inline forms have distinct associated identifiers',()=>{const pairs=renderToStaticMarkup(React.createElement(React.Fragment,null,React.createElement(Login),React.createElement(Login)));const ids=[...pairs.matchAll(/ id="([^"]+)"/g)].map(x=>x[1]);assert.equal(new Set(ids).size,ids.length);});
 check('standalone login has no dashboard navigation and keeps QA boundary explicit',()=>{assert.doesNotMatch(page,/href="\/"|nadi-sidebar|nadi-topbar|nadi-development-status/);assert.match(page,/Layar pengembangan faktual tetap dapat diakses/);assert.match(page,/QA terisolasi/);});
 check('server-side QA-only login gate remains intact',()=>{const source=readFileSync('app/(authentication)/login/page.tsx','utf8');assert.match(source,/NODE_ENV!=="development"/);assert.match(source,/NADI_ENGINEERING_QA_ENABLED!=="true"/);assert.match(source,/notFound\(\)/);});
 check('root separates authentication from workspace structurally',()=>{const root=readFileSync('app/layout.tsx','utf8'),auth=readFileSync('app/(authentication)/layout.tsx','utf8'),workspace=readFileSync('app/(workspace)/layout.tsx','utf8');assert.doesNotMatch(root,/AppShell|DevelopmentStatus/);assert.doesNotMatch(auth,/AppShell|DevelopmentStatus/);assert.match(auth,/main-content/);assert.match(workspace,/AppShell/);assert.match(workspace,/DevelopmentStatus/);});
 console.log('Login presentation checks passed: '+count);
}finally{if(original)require.cache[navigation]=original;else delete require.cache[navigation];rmSync(temp,{recursive:true,force:true});}
