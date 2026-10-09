"""Real NADI local login UI→Next→HTTP→disposable PostgreSQL. No secret output."""
import json,os,stat
from pathlib import Path
from playwright.sync_api import sync_playwright
path=Path(os.environ["NADI_LOCAL_TEST_ACCOUNTS"])
info=path.stat()
if info.st_uid!=os.geteuid() or info.st_mode&0o077 or path.is_symlink():raise RuntimeError("private fixture required")
accounts=json.loads(path.read_text())
output=Path(os.environ["NADI_QA_BROWSER_OUTPUT"])
if output.parent!=Path("/tmp") or not output.name.startswith("nadi-"):raise RuntimeError("disposable output only")
output.mkdir(exist_ok=True);results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=os.environ.get("NADI_TEST_BROWSER_EXECUTABLE"));page=browser.new_page(ignore_https_errors=True,viewport={"width":1365,"height":1000})
    page.goto("https://localhost:13035/login?expired=1")
    page.get_by_role("heading",name="NADI login",exact=True).wait_for()
    page.get_by_text("Your session expired or was revoked.",exact=False).wait_for();results.append("session expired feedback")
    page.get_by_label("Username",exact=True).fill("unregistered-fixture")
    page.get_by_label("Password",exact=True).fill(accounts["engineer"]["password"])
    page.get_by_role("button",name="Sign in",exact=True).click()
    page.get_by_role("alert").filter(has_text="Unable to sign in").wait_for();results.append("generic invalid credentials")
    def login(name,standalone=False):
        if standalone:page.goto("https://localhost:13035/login")
        else:
            buttons=page.get_by_role("button",name="Log out",exact=True)
            if buttons.count():
                with page.expect_response(lambda r:r.url.endswith("/session/logout")) as reply:buttons.click()
                assert reply.value.status==200
                results.append("logout revoked session")
        page.get_by_label("Username",exact=True).fill(accounts[name]["username"])
        page.get_by_label("Password",exact=True).fill(accounts[name]["password"])
        page.get_by_role("button",name="Show password",exact=True).click()
        assert page.get_by_label("Password",exact=True).get_attribute("type")=="text"
        page.get_by_role("button",name="Hide password",exact=True).click()
        page.get_by_role("button",name="Sign in",exact=True).click()
        page.get_by_role("heading",name="Trusted local session",exact=True).wait_for()
        results.append("local login "+name)
    login("engineer",True)
    asset=accounts["asset"]
    page.get_by_label("Canonical asset",exact=True).fill(asset)
    with page.expect_response(lambda r:"asset-context" in r.url) as reply:page.get_by_role("button",name="Read asset context").click()
    assert reply.value.status==200;results.append("authorized asset context")
    page.get_by_label("Record ID (empty to create)").fill("previous-subject-record")
    page.get_by_label("Canonical command JSON").fill('{"private_previous_subject":"fixture"}')
    # Only expiry is mocked. Both subjects authenticate against the real backend.
    def expired(route):route.fulfill(status=401,content_type="application/json",body='{"detail":"UNAUTHORIZED"}')
    page.route("**/api/engineering-qa/inspections?*",expired)
    page.get_by_role("button",name="Load records",exact=True).click()
    page.get_by_role("heading",name="Sign in to NADI",exact=True).wait_for()
    assert page.locator("pre").count()==0;results.append("expiry clears prior response")
    assert page.get_by_label("Record ID (empty to create)").input_value()==""
    assert page.get_by_label("Canonical command JSON").input_value()=="{}"
    results.append("expiry clears prior subject draft")
    page.unroute("**/api/engineering-qa/inspections?*",expired)
    login("reviewer")
    assert page.locator("pre").count()==0;results.append("new subject cannot see prior response")
    login("engineer")
    def command(module,record,action,body):
        page.get_by_label("Module",exact=True).select_option(module)
        page.get_by_label("Record ID (empty to create)").fill(record)
        page.get_by_label("Action",exact=True).select_option(action)
        page.get_by_label("Canonical command JSON").fill(json.dumps(body))
        with page.expect_response(lambda r:"/api/engineering-qa/"+module in r.url and r.request.method in {"POST","PUT"}) as reply:page.get_by_role("button",name="Send controlled command").click()
        assert reply.value.status in {200,201},"workflow response rejected"
        results.append(module+":"+(action or "create"));return reply.value.json()
    def step(module,row,action,fields=None):
        return command(module,row.get("record_id",row.get("case_id")),action,{"request_id":module+"-"+action+"-"+str(row["revision"]),"expected_revision":row["revision"],**(fields or {})})
    inspection=command("inspections","","",{"request_id":"local-browser-inspection","draft":{"canonical_asset_id":asset,"method":"VIBRATION","method_version":"proposal-1","inspector_ref":accounts["engineer"]["user_id"],"inspected_at":"2026-10-09T00:00:00Z","measurements":[{"quantity":"velocity","value":None,"unit":"mm/s"}],"observations":["Fixture manual observation"],"interpretations":["Human hypothesis"]}})
    inspection=step("inspections",inspection,"submit");login("reviewer")
    inspection=step("inspections",inspection,"begin_review",{"reason":"Independent review"})
    inspection=step("inspections",inspection,"review",{"decision":"APPROVED","reason":"Reviewed fixture evidence"})
    login("engineer")
    case=command("cases","","",{"request_id":"local-browser-case","draft":{"canonical_asset_id":asset,"title":"Fixture investigation","problem_statement":"Controlled human finding"}})
    case=step("cases",case,"evidence",{"kind":"MANUAL_INSPECTION","record_id":inspection["record_id"],"mode":"FROZEN_SNAPSHOT"})
    case=step("cases",case,"submit");login("reviewer")
    case=step("cases",case,"review",{"decision":"APPROVED","reason":"Independent finding"});login("engineer")
    rec=command("recommendations","","",{"request_id":"local-browser-rec","draft":{"canonical_asset_id":asset,"case_ref":case["case_id"],"rationale":"Reviewed evidence","proposed_action":"Local follow-up only","evidence_selections":[{"kind":"MANUAL_INSPECTION","record_id":inspection["record_id"]}]}})
    rec=step("recommendations",rec,"submit");login("reviewer")
    rec=step("recommendations",rec,"review",{"decision":"APPROVED","reason":"Independent proposal review"});login("engineer")
    step("recommendations",rec,"followup",{"status":"PLANNED","reason":"NADI local follow-up"})
    page.reload();page.get_by_role("heading",name="Trusted local session",exact=True).wait_for()
    page.get_by_label("Module",exact=True).select_option("recommendations")
    with page.expect_response(lambda r:"/recommendations?" in r.url) as reply:page.get_by_role("button",name="Load records").click()
    assert reply.value.status==200 and reply.value.json()["total"]==1;results.append("durable records and memory-only session resume")
    assert page.evaluate("Object.keys(localStorage).length+Object.keys(sessionStorage).length")==0
    results.append("no browser storage auth secrets")
    for width in (390,768,1365):
        page.set_viewport_size({"width":width,"height":1000})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"),"responsive overflow"
        page.screenshot(path=str(output/("local-workflow-"+str(width)+".png")),full_page=True);results.append("responsive "+str(width))
    page.get_by_role("button",name="Log out",exact=True).click();page.get_by_role("heading",name="Sign in to NADI",exact=True).wait_for()
    page.screenshot(path=str(output/"local-login-390.png"),full_page=True);results.append("final logout")
    browser.close()
(output/"results.json").write_text(json.dumps(results,indent=2));print(json.dumps({"passed":len(results),"results":results}))
