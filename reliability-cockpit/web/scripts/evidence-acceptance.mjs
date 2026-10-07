// Render the actual React read views using synthetic API documents, with no network.
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
const webRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const require = createRequire(resolve(webRoot,"package.json"));
const ts = require("typescript");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const input = JSON.parse(readFileSync(0,"utf8"));
function load(name) {
  const source=readFileSync(resolve(webRoot,"components",name+".tsx"),"utf8");
  const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,target:ts.ScriptTarget.ES2022}}).outputText;
  const module={exports:{}};
  new Function("require","module","exports",js)(require,module,module.exports);
  return module.exports.default;
}
const trust=renderToStaticMarkup(React.createElement(load("IntegrationStatusView"),{data:input.integration}));
const evidence=renderToStaticMarkup(React.createElement(load("ConditionEvidenceView"),{data:input.condition}));
if (!trust.includes("Verified mapping assets") || !trust.includes("Projected condition assets")) throw new Error("coverage absent");
if (!evidence.includes("Signal evidence does not determine equipment health")) throw new Error("health boundary absent");
for (const forbidden of ["Authorization", "PI_PASSWORD", "http://pi-source", "healthy asset"]) {
  if ((trust+evidence).includes(forbidden)) throw new Error("unsafe display");
}
process.stdout.write(JSON.stringify({trust,evidence}));
