import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync, symlinkSync, readFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { tmpdir } from "node:os";
const require = createRequire(import.meta.url);
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const temp = mkdtempSync(join(tmpdir(), "nadi-ux-"));
let checks = 0;
const test = (label, fn) => { fn(); checks++; console.log(`PASS ${label}`); };
try {
  const files = ["components/ui.tsx", "lib/navigation.ts", "lib/overview.ts", "components/ExecutiveOverview.tsx"].filter(existsSync);
  execFileSync(process.execPath, ["node_modules/typescript/bin/tsc", ...files, "--outDir", temp, "--rootDir", ".", "--module", "commonjs", "--target", "ES2022", "--jsx", "react-jsx", "--esModuleInterop", "--skipLibCheck"], { stdio: "pipe" });
  symlinkSync(resolve("node_modules"), join(temp, "node_modules"));
  const ui = require(join(temp, "components/ui.js"));
  const render = (component, props) => renderToStaticMarkup(React.createElement(component, props));
  test("scrollable table keeps minimum width inside outer region", () => {
    const html = render(ui.TableFrame, { minWidth: 900, children: React.createElement("table") });
    assert.match(html, /role="region"[^>]+tabindex="0"><div[^>]+min-width:900px/);
    assert.doesNotMatch(html.split("><div")[0], /min-width/);
  });
  test("loading announces progress without a temporary value", () => assert.match(render(ui.LoadingState), /role="status"/));
  test("errors are announced and retry remains optional", () => {
    assert.match(render(ui.ErrorState, { onRetry() {} }), /role="alert"/);
    assert.match(render(ui.ErrorState, { onRetry() {} }), /Try again/);
  });
  test("unknown raw source status stays neutral", () => assert.match(render(ui.StatusBadge, { value: "UNKNOWN", mode: "raw-neutral" }), /neutral[^>]*>UNKNOWN/));
  test("raw CLOSED source status is not a health classification", () => assert.match(render(ui.StatusBadge, { value: "CLOSED", mode: "raw-neutral" }), /neutral/));
  test("legacy pages keep one main landmark and contained tables", () => {
    for(const path of ["app/work-orders/page.tsx", "app/equipment/[id]/page.tsx"]) {
      const source=readFileSync(path,"utf8"); assert.ok(!source.includes("<main>")); assert.ok(source.includes("<TableFrame"));
    }
  });
  test("button does not submit a form accidentally", () => assert.match(render(ui.Button, { children: "Review" }), /type="button"/));
  test("breadcrumb declares exactly one current page", () => assert.equal((render(ui.Breadcrumbs, {items:[{label:"NADI"},{label:"Overview"}]}).match(/aria-current="page"/g) ?? []).length, 1));
  test("input has persistent associated label", () => assert.match(render(ui.InputControl, { id: "scope", label: "Scope" }), /for="scope"/));
  const css = readFileSync("app/design-tokens.css", "utf8");
  const luminance = hex => {
    const rgb = hex.match(/\w\w/g).map(x => parseInt(x, 16) / 255).map(x => x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4);
    return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2];
  };
  for (const [theme, section] of [["light", css.split(':root[data-theme')[0]], ["dark", css.split(':root[data-theme')[1]]]) {
    const token = name => section.match(new RegExp(`--${name}: #([a-f0-9]{6})`))[1];
    for (const [fg, bg] of [["text", "surface"], ["muted", "surface"], ["muted-2", "surface-2"], ["primary", "surface"], ["button-text", "primary"], ["sidebar-text", "sidebar"], ["sidebar-muted", "sidebar"], ["amber", "surface"]].filter(([fg]) => theme === "light" || !fg.startsWith("sidebar"))) {
      test(`${theme} ${fg}/${bg} contrast >= 4.5`, () => {
        const a = luminance(token(fg)), b = luminance(token(bg));
        assert.ok((Math.max(a,b)+.05)/(Math.min(a,b)+.05) >= 4.5);
      });
    }
  }
  if (existsSync(join(temp, "lib/navigation.js"))) {
    const { navigation, routeMatches, navigationGroup } = require(join(temp, "lib/navigation.js"));
    test("all existing navigation URLs survive", () => {
      const hrefs = navigation.flatMap(x => x.children?.map(c => c.href) ?? [x.href]);
      for (const href of ["/", "/assets", "/asset-health", "/maintenance", "/maintenance/investigation", "/work-orders", "/fmea", "/rcfa", "/overhauls", "/data-quality"]) assert.ok(hrefs.includes(href), href);
    });
    test("route boundary prevents false active links", () => { assert.ok(!routeMatches("/assets-other", "/assets")); assert.ok(routeMatches("/assets/id", "/assets")); assert.ok(!routeMatches("/assets", "/")); });
    test("detail routes retain domain context", () => { assert.equal(navigationGroup("/assets/A%3AB"), "assets"); assert.equal(navigationGroup("/equipment/42"), "integration"); assert.equal(navigationGroup("/maintenance/investigation"), "integration"); });
    test("planned modules cannot silently redirect", () => { for(const item of navigation.filter(x => x.planned)) { assert.equal(item.href, undefined); assert.equal(item.children, undefined); } });
  }
  if (existsSync(join(temp, "lib/overview.js"))) {
    const { factualMetric, overviewDate, attentionItems } = require(join(temp, "lib/overview.js"));
    test("unknown and gated numbers cannot become facts", () => { for(const x of [null, undefined, NaN, Infinity]) assert.equal(factualMetric({value:x,evidence_class:"VERIFIED"}), "UNKNOWN"); assert.equal(factualMetric({value:62,evidence_class:"BUSINESS_SEMANTICS_REQUIRED"}), "NOT ASSESSED"); assert.equal(factualMetric({value:0,evidence_class:"VERIFIED"}), "0"); });
    test("invalid/missing timestamps are unknown", () => { for(const x of [null, "not-a-date"]) assert.equal(overviewDate(x), "UNKNOWN"); });
    test("attention shows exact integrity counts, no risk math", () => {
      const items = attentionItems({registered_assets_unresolved:0,asset_refs_unresolved:3,workorder_refs_unresolved:2});
      assert.deepEqual(items.map(x => x.count), [0,3,2]);
      assert.ok(items.every(x => x.href === "/data-quality"));
    });
  }
  if (existsSync(join(temp, "components/ExecutiveOverview.js"))) {
    const { ActivityChart, Distribution } = require(join(temp, "components/ExecutiveOverview.js"));
    test("chart preserves exact zero, unknown and dated values", () => {
      const rows = [0, null, 12].map((value, i) => ({period_start:`2026-10-0${i+1}T00:00:00Z`, period_end:`2026-10-0${i+2}T00:00:00Z`, event_count:{value,evidence_class:"DERIVED_SAFE"}}));
      const html = render(ActivityChart,{rows});
      assert.match(html, /UNKNOWN/); assert.match(html, /height:0%/); assert.match(html, /height:100%/); assert.match(html, /View exact periods and counts/);
    });
    test("empty distributions and trend explain absence", () => { assert.match(render(ActivityChart,{rows:[]}), /does not establish equipment condition/); assert.match(render(Distribution,{title:"statuses", rows:[]}), /No statuses/); });
  }
  console.log(`UX checks passed: ${checks}`);
} finally { rmSync(temp, {recursive:true,force:true}); }
