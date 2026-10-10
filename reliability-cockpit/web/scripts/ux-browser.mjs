// Read-only factual regression plus isolated browser response fixtures. Never resets a DB.
// Optional QA login reads an operator-owned private account file; no credentials are logged.
import assert from "node:assert/strict";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
const { chromium } = await import(process.env.NADI_PLAYWRIGHT_MODULE ? pathToFileURL(process.env.NADI_PLAYWRIGHT_MODULE).href : "playwright");
const base = process.env.NADI_PREVIEW_URL ?? "https://localhost:3000";
assert.equal(base, "https://localhost:3000", "Use only the reviewed localhost HTTPS frontend");
const out = resolve(process.env.NADI_BROWSER_OUTPUT ?? "/tmp/nadi-ux-browser");
mkdirSync(out, {recursive:true});
const fixture = JSON.parse(readFileSync("fixtures/executive-overview.json", "utf8"));
const checks = [], errors = [];
const check = (name, ok) => { assert.ok(ok, name); checks.push(name); console.log(`PASS ${name}`); };
const browser = await chromium.launch({headless:true});
// Known self-signed localhost certificate exception is confined to these disposable contexts.
const context = await browser.newContext({ignoreHTTPSErrors:true, viewport:{width:1440,height:1086}});
const page = await context.newPage();
page.on("pageerror", e => errors.push(e.message));
try {
  const status = await (await context.request.get(`${base}/api/development/status`)).json();
  check("both backends available and existing fixture identity", status.backend === "AVAILABLE" && status.factual_backend === "AVAILABLE" && status.database_identity === "nadi_live_dev_test" && !status.stale);
  check("clean exact preview SHA", /^[0-9a-f]{40}$/.test(status.sha) && status.dirty === false && status.sha === status.backend_sha && status.sha === status.launched_sha);
  for (const path of ["/", "/assets", "/asset-health", "/maintenance", "/maintenance/investigation", "/work-orders", "/fmea", "/rcfa", "/overhauls", "/data-quality", "/engineering", "/engineering/lab", "/engineering/workflow", "/engineering/local", "/login"]) {
    const responses = [];
    const onResponse = response => { if (response.url().includes("/api/cockpit/")) responses.push(response.status()); };
    page.on("response", onResponse);
    const response = await page.goto(base+path, {waitUntil:"networkidle"});
    check(`render ${path}`, response.status() === 200 && await page.locator("main").isVisible());
    check(`factual requests ${path}`, responses.every(code => code === 200));
    check(`visible status ${path}`, (await page.getByRole("complementary",{name:"Development environment status"}).innerText()).includes(status.sha));
    page.off("response", onResponse);
  }
  const assets = await (await context.request.get(`${base}/api/cockpit/v1/reliability/assets?limit=1`)).json();
  if (assets.items.length) {
    const id = assets.items[0].canonical_id;
    check("asset detail deep link", (await page.goto(`${base}/assets/${encodeURIComponent(id)}`,{waitUntil:"networkidle"})).status() === 200);
    check("asset detail exact canonical identity", (await page.locator("main").innerText()).includes(id));
    check("asset detail activates Asset Health", await page.getByRole("button",{name:"Asset Health",exact:true}).getAttribute("aria-expanded") === "true");
  }
  const equipment = await (await context.request.get(`${base}/api/cockpit/equipment?limit=1`)).json();
  const equipmentRows = Array.isArray(equipment) ? equipment : equipment.items ?? [];
  if(equipmentRows.length) check("equipment detail deep link", (await page.goto(`${base}/equipment/${encodeURIComponent(equipmentRows[0].id)}`, {waitUntil:"networkidle"})).status() === 200);
  await page.goto(base,{waitUntil:"networkidle"});
  for (const days of [7,90,30]) {
    await page.getByLabel("Maintenance activity window").selectOption(String(days));
    await page.locator(".executive-summary-grid").waitFor();
    const data = await (await context.request.get(`${base}/api/cockpit/v1/reliability/decision-overview?window_days=${days}`)).json();
    const values = await page.locator(".overview-stat-grid .stat-card > strong").allTextContents();
    const expected = [data.summary.registered_assets, data.summary.maintenance_activity_7d, data.summary.maintenance_activity_30d, data.summary.assets_active_30d, data.summary.maintenance_activity_90d, data.record_availability.asset_health_records].map(x => x.value.toLocaleString("id-ID"));
    check(`factual KPI values unchanged ${days}d`, JSON.stringify(values) === JSON.stringify(expected));
  }
  await page.getByRole("button",{name:"System Integration",exact:true}).focus();
  await page.keyboard.press("Enter");
  check("keyboard submenu expands", await page.getByRole("button",{name:"System Integration",exact:true}).getAttribute("aria-expanded") === "true");
  await page.getByRole("link",{name:"Maintenance Investigation",exact:true}).click();
  check("most specific route active", await page.getByRole("link",{name:"Maintenance Investigation",exact:true}).getAttribute("aria-current") === "page" && await page.getByRole("link",{name:"Maintenance",exact:true}).getAttribute("aria-current") === null);
  await page.getByRole("button",{name:"Collapse sidebar",exact:true}).click();
  check("collapsed navigation retains names", await page.getByRole("link",{name:"Executive Overview",exact:true}).isVisible());
  await page.getByRole("button",{name:"Expand sidebar",exact:true}).click();
  for (const width of [768,390]) {
    await page.setViewportSize({width,height:1000});
    await page.getByRole("button",{name:"Open navigation",exact:true}).click();
    const dialog = page.getByRole("dialog",{name:"NADI navigation panel"});
    check(`drawer opens ${width}`, await dialog.isVisible());
    await dialog.getByRole("button",{name:"System Integration",exact:true}).focus();
    await page.keyboard.press("Tab");
    check(`keyboard focus stays in drawer ${width}`, await page.evaluate(() => document.querySelector("#nadi-sidebar").contains(document.activeElement)));
    await dialog.locator('button:not([disabled]),a[href]').evaluateAll(nodes => nodes.filter(n => n.getClientRects().length).at(-1).focus());
    await page.keyboard.press("Tab");
    check(`focus trap wraps ${width}`, await page.evaluate(() => document.querySelector("#nadi-sidebar").contains(document.activeElement)));
    await page.keyboard.press("Escape");
    check(`escape closes and returns focus ${width}`, !await dialog.isVisible() && await page.getByRole("button",{name:"Open navigation",exact:true}).evaluate(n=>document.activeElement===n));
  }
  if(process.env.NADI_QA_ACCOUNT_FILE) {
    const accounts = JSON.parse(readFileSync(process.env.NADI_QA_ACCOUNT_FILE,"utf8"));
    await page.goto(base+"/login",{waitUntil:"networkidle"});
    await page.getByLabel("Username",{exact:true}).fill(accounts.engineer.username);
    await page.getByLabel("Password",{exact:true}).fill(accounts.engineer.password);
    await page.getByRole("button",{name:"Sign in",exact:true}).click();
    await page.waitForURL(base+"/engineering/local");
    await page.getByRole("heading",{name:"Trusted local session",exact:true}).waitFor();
    check("existing development login/session works", true);
    check("session retains Secure HttpOnly SameSite", (await context.cookies(base)).some(c=>c.secure&&c.httpOnly&&c.sameSite==="Strict"));
    for(const origin of ["http://localhost:3000","https://localhost:13035"]) {
      const response = await context.request.post(base+"/api/engineering-qa/auth/login",{headers:{Origin:origin},data:{username:accounts.engineer.username,password:accounts.engineer.password}});
      check(`untrusted origin remains rejected ${origin}`, response.status()===403);
    }
    if(process.env.NADI_PERSISTED_RECORD_FILE) {
      const expected=JSON.parse(readFileSync(process.env.NADI_PERSISTED_RECORD_FILE,"utf8"));
      for(const [resource,row] of [["inspections",expected.inspection],["cases",expected.c],["recommendations",expected.recommendation]]) {
        const response=await context.request.get(base+"/api/engineering-qa/"+resource+"/"+(row.record_id??row.case_id));
        check(`original persisted ${resource} unchanged`,response.status()===200&&JSON.stringify(await response.json())===JSON.stringify(row));
      }
    }
  }
  check("no uncaught browser exceptions", errors.length===0);
  // Separate context: only this browser intercepts reads for deterministic, publicly shareable screenshots.
  const visual=await browser.newContext({ignoreHTTPSErrors:true});
  const vp=await visual.newPage();
  let mode="data", pending;
  await vp.route("**/api/cockpit/v1/reliability/decision-overview?*",async route=>{
    if(mode==="loading") await new Promise(resolve=>{pending=resolve;});
    if(mode==="error") return route.fulfill({status:503,json:{detail:"UNAVAILABLE"}});
    const data=structuredClone(fixture);
    data.window_days=Number(new URL(route.request().url()).searchParams.get("window_days"));
    if(mode==="empty") { data.activity_concentration=[]; data.maintenance_activity=[]; data.status_distribution=[]; data.work_type_distribution=[]; }
    if(mode==="unknown") { data.summary.registered_assets={value:null,evidence_class:"DATA_NOT_AVAILABLE"}; data.summary.maintenance_activity_7d={value:62,evidence_class:"BUSINESS_SEMANTICS_REQUIRED"}; }
    return route.fulfill({json:data});
  });
  for(const width of [1440,768,390]) {
    await vp.setViewportSize({width,height:1086});
    await vp.goto(base,{waitUntil:"networkidle"});
    await vp.locator(".executive-summary-grid").waitFor();
    check(`no horizontal page overflow ${width}`,await vp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await vp.evaluate(()=>{const banner=document.createElement("p");banner.textContent="DEMO · SYNTHETIC UI REGRESSION FIXTURE — NO OPERATIONAL DATA";banner.style.cssText="padding:12px;border:2px solid #1d4ed8;font-weight:bold";document.querySelector("main").prepend(banner);});
    await vp.screenshot({path:resolve(out,`executive-${width}.png`),fullPage:true});
    const frame=vp.locator(".executive-summary-grid .table-frame");
    check(`table scroll stays inside panel ${width}`,await frame.evaluate(n=>n.clientWidth<=n.parentElement.clientWidth));
  }
  await vp.setViewportSize({width:1440,height:1086});
  await vp.goto(base,{waitUntil:"networkidle"});
  await vp.getByRole("button",{name:"Show all 7 assets"}).click();
  check("all activity rows remain accessible",await vp.locator(".executive-summary-grid tbody tr").count()===7);
  await vp.getByRole("button",{name:"Show top 5 assets"}).click();
  check("compact overview preserves five-row hierarchy",await vp.locator(".executive-summary-grid tbody tr").count()===5);
  await vp.getByText("View exact periods and counts",{exact:true}).click();
  check("chart has complete non-color data table",await vp.locator(".chart-values tbody tr").count()===12);
  mode="unknown"; await vp.reload({waitUntil:"networkidle"});
  check("unknown and gated metrics do not become zero or scores",await vp.locator(".stat-card > strong").nth(0).innerText()==="UNKNOWN"&&await vp.locator(".stat-card > strong").nth(1).innerText()==="NOT ASSESSED");
  mode="empty"; await vp.reload({waitUntil:"networkidle"});
  check("empty results preserve evidence caveat",await vp.getByText("An empty activity series does not establish equipment condition.").isVisible());
  mode="error"; await vp.reload({waitUntil:"networkidle"});
  check("safe error and retry remain usable",await vp.getByRole("alert").isVisible());
  mode="data"; await vp.getByRole("button",{name:"Try again",exact:true}).click();await vp.locator(".executive-summary-grid").waitFor();
  check("retry recovers supported factual view",true);
  mode="loading"; await vp.reload({waitUntil:"domcontentloaded"}); await vp.getByRole("status").filter({hasText:"Reading Executive Overview"}).waitFor();
  check("loading has no temporary KPI zero",await vp.locator(".stat-card").count()===0);
  mode="data";pending?.();await vp.locator(".executive-summary-grid").waitFor();
  await visual.close();
  writeFileSync(resolve(out,"browser-report.json"),JSON.stringify({status:"PASS",sha:status.sha,checks,errors,screenshots:"SYNTHETIC browser fixtures; no operational data"},null,2));
  console.log(`Browser checks passed: ${checks.length}`);
} finally { await context.close(); await browser.close(); }
