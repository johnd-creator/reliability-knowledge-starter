from playwright.sync_api import sync_playwright
import json
from pathlib import Path
import os
OUTPUT=Path(os.environ.get("NADI_TEST_ARTIFACT_DIR", "/tmp/nadi-bundle-c-browser"))
OUTPUT.mkdir(parents=True, exist_ok=True)
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    context=browser.new_context()
    blocked=[]
    context.route('**/*',lambda r:r.continue_() if r.request.url.startswith('http://127.0.0.1:13034/') else (blocked.append(True),r.abort()))
    page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    for path in ('workflow','lab'):
        response=page.goto('http://127.0.0.1:13034/engineering/'+path)
        assert response.status==200;checks.append(path+' blocked page200')
        assert not page.get_by_role('button',name='Save demo inspection draft').count();checks.append(path+' no editing controls')
        assert 'SYNTHETIC LOCAL DEMO' not in page.locator('main').inner_text();checks.append(path+' no demo activation')
    assert not blocked;checks.append('no external requests')
    assert not errors;checks.append('no browser exceptions')
    browser.close()
(OUTPUT / 'production-gate-results.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2))
print('Production UI gate acceptance:',len(checks),'PASS')
