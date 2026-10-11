// Render actual read views from synthetic API documents; no network or persistent store.
import { readFileSync, mkdtempSync, symlinkSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import { dirname, resolve, join } from "node:path";
import { fileURLToPath } from "node:url";
const webRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const require = createRequire(resolve(webRoot,"package.json"));
const React = require("react"), { renderToStaticMarkup } = require("react-dom/server");
const input = JSON.parse(readFileSync(0,"utf8"));
const temp=mkdtempSync(join(tmpdir(),'nadi-evidence-'));
const copy=JSON.parse(readFileSync(resolve(webRoot,'lib/id-messages.json'),'utf8'));
try {
  const config=join(temp,'tsconfig.json');
  writeFileSync(config,JSON.stringify({compilerOptions:{outDir:temp,rootDir:webRoot,baseUrl:webRoot,paths:{"@/*":["./*"]},module:"commonjs",target:"ES2022",jsx:"react-jsx",esModuleInterop:true,skipLibCheck:true,resolveJsonModule:true,moduleResolution:"node"},files:['IntegrationStatusView','ConditionEvidenceView'].map(name=>resolve(webRoot,'components',name+'.tsx'))}));
  execFileSync(process.execPath,['node_modules/typescript/bin/tsc','--project',config],{cwd:webRoot,stdio:'pipe'});
  symlinkSync(resolve(webRoot,'node_modules'),join(temp,'node_modules'));
  const load=name=>require(join(temp,'components',name+'.js')).default;
  const trust=renderToStaticMarkup(React.createElement(load('IntegrationStatusView'),{data:input.integration}));
  const evidence=renderToStaticMarkup(React.createElement(load('ConditionEvidenceView'),{data:input.condition}));
  for(const key of ['Verified mapping assets','Projected condition assets'])if(!trust.includes(copy[key]??key))throw new Error('coverage absent');
  if(!evidence.includes(copy['. Signal evidence does not determine equipment health.']))throw new Error('health boundary absent');
  for(const forbidden of ['Authorization','PI_PASSWORD','http://pi-source','healthy asset'])if((trust+evidence).includes(forbidden))throw new Error('unsafe display');
  process.stdout.write(JSON.stringify({trust,evidence}));
} finally { rmSync(temp,{recursive:true,force:true}); }
