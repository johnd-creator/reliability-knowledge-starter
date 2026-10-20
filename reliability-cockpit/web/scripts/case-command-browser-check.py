"""Manual provider/hook regressions. All HTTP is intercepted to a synthetic .invalid
origin; --bundle is browserBundle('scripts/recommendation/case-command-entry.tsx').
No listening server, real session, active runtime or source system is used.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--bundle', type=Path, required=True)
parser.add_argument('--chromium', type=Path, required=True)
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args()
bundle = args.bundle.read_text()
origin = 'https://case-command-fixture.invalid'
results = []

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, executable_path=str(args.chromium))
    try:
        def scenario(name, test):
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(5000)
            state = dict(writes=[], held=[], mode='hold', escaped=[])
            def route(request_route):
                request = request_route.request
                if request.url == origin + '/fixture':
                    request_route.fulfill(body='<html><div id="root"></div><script src="/candidate.js"></script></html>', content_type='text/html')
                elif request.url == origin + '/candidate.js':
                    request_route.fulfill(body=bundle, content_type='text/javascript')
                elif request.url.startswith(origin + '/api/engineering-qa/cases/case%3Afixture/') and request.method == 'POST':
                    state['writes'].append(dict(url=request.url, body=request.post_data_json, csrf=request.headers.get('x-csrf-token')))
                    if state['mode'] == 'hold':
                        state['held'].append(request_route)
                    else:
                        request_route.fulfill(status=503, json={'detail': {'code': 'QA_BACKEND_UNAVAILABLE'}})
                else:
                    state['escaped'].append(request.url)
                    request_route.abort()
            context.route('**/*', route)
            try:
                page.goto(origin + '/fixture')
                page.wait_for_function("document.querySelector('#case-primed').textContent==='true'")
                test(page, state)
                assert not state['escaped'], state['escaped']
                results.append(dict(name=name, result='PASS', writes=state['writes']))
                print('PASS', name)
            except Exception as exc:
                results.append(dict(name=name, result='FAIL', error=str(exc), writes=state['writes']))
                raise
            finally:
                context.close()

        def cache(page):
            return json.loads(page.locator('#case-cache').inner_text())

        def remount(page):
            page.evaluate('caseFixture.mount(false)')
            page.locator('#case-note').wait_for(state='detached')
            page.evaluate('caseFixture.mount(true)')
            page.locator('#case-note').wait_for()

        def start(page, kind='note'):
            page.locator('#case-'+kind).click()
            page.wait_for_function("JSON.parse(document.querySelector('#case-cache').textContent).busy===true")

        def finish(page, state, status=200):
            state['held'].pop().fulfill(status=status, json={'saved':True} if status==200 else {'detail':{'code':'SESSION_EXPIRED'}})
            page.wait_for_function("JSON.parse(document.querySelector('#case-results').textContent).length===1")

        def stale_identity(kind, status, patch):
            def test(page, state):
                assert cache(page)['recovery'] is None
                start(page, kind)
                assert cache(page)['intent'] is not None
                page.evaluate('(patch)=>caseFixture.ready(patch)', patch)
                page.wait_for_function("JSON.parse(document.querySelector('#case-cache').textContent).busy===false")
                assert cache(page)['intent'] is None
                finish(page, state, status)
                assert json.loads(page.locator('#case-results').inner_text()) == [None]
                assert page.evaluate('window.caseExpiredCalls||0') == 0
                assert page.locator('#case-subject').inner_text() == patch.get('subject','author')
                assert len(state['writes']) == 1
            return test
        for kind in ['note','linked']:
            for status in [200,401]:
                scenario(f'{kind}-no-recovery-new-subject-old-{status}-ignored',stale_identity(kind,status,{'subject':'other','csrf_token':'new-synthetic'}))
        for label, patch in [('role',{'roles':['AUTHOR','REVIEWER']}),('scope',{'asset_ids':['asset:qa','asset:other']})]:
            scenario(label+'-change-clears-pending-without-recovery',stale_identity('note',200,patch))

        def pending(page, state):
            start(page)
            first_id = cache(page)['intent']['id']
            remount(page)
            assert page.locator('#case-note').is_disabled()
            assert page.locator('#case-linked').is_disabled()
            assert cache(page)['intent']['id'] == first_id
            assert len(state['writes']) == 1
            finish(page,state)
            assert json.loads(page.locator('#case-results').inner_text()) == [{'saved':True}]
            assert cache(page)['busy'] is False
        scenario('durable-pending-lock-survives-editor-remount',pending)

        def revoked(state_name):
            def test(page,state):
                page.evaluate("caseFixture.keep('Private revoked draft')")
                start(page)
                page.evaluate('(state)=>caseFixture.revoke(state)',state_name)
                page.wait_for_function("JSON.parse(document.querySelector('#case-cache').textContent).busy===false")
                assert cache(page)['recovery'] is None and cache(page)['intent'] is None
                finish(page,state,401)
                assert json.loads(page.locator('#case-results').inner_text()) == [None]
                assert page.evaluate('window.caseExpiredCalls||0') == 0
            return test
        for state_name in ['expired','denied','disabled']:
            scenario('confirmed-'+state_name+'-clears-draft-and-pending',revoked(state_name))

        def transient(page,state):
            state['mode']='unavailable'
            page.evaluate("caseFixture.keep('Retained transient draft')")
            start(page)
            page.wait_for_function("JSON.parse(document.querySelector('#case-results').textContent).length===1")
            first_id=state['writes'][0]['body']['request_id']
            remount(page)
            page.evaluate("caseFixture.ready({csrf_token:'refreshed-synthetic'})")
            assert cache(page)['recovery']['draft']['title']=='Retained transient draft'
            assert cache(page)['intent']['id']==first_id
            page.locator('#case-note').click()
            page.wait_for_function("JSON.parse(document.querySelector('#case-results').textContent).length===2")
            assert state['writes'][1]['body']['request_id']==first_id
            assert state['writes'][1]['csrf']=='refreshed-synthetic'
        scenario('503-loading-remount-and-token-refresh-retain-draft-and-intent',transient)

        def changed_draft(page,state):
            page.evaluate("caseFixture.keep('Original in-flight draft')")
            start(page,'save')
            page.evaluate("caseFixture.keep('Newly changed draft')")
            finish(page,state)
            assert cache(page)['recovery']['draft']['title']=='Newly changed draft'
            assert cache(page)['busy'] is False
        scenario('old-success-clearSaved-cannot-erase-changed-new-draft',changed_draft)

        def cross_command(kind):
            def test(page,state):
                state['mode']='unavailable'
                start(page,'note')
                page.wait_for_function("JSON.parse(document.querySelector('#case-results').textContent).length===1")
                first_id=state['writes'][0]['body']['request_id']
                state['mode']='hold'
                if kind=='save':
                    page.evaluate("caseFixture.keep('Independent successful draft B')")
                start(page,kind)
                assert len(state['writes'])==2
                assert state['writes'][1]['body']['request_id']!=first_id
                state['held'].pop().fulfill(json={'saved':True})
                page.wait_for_function("JSON.parse(document.querySelector('#case-results').textContent).length===2")
                if kind=='save':
                    assert cache(page)['recovery'] is None
                remount(page)
                start(page,'note')
                assert len(state['writes'])==3
                assert state['writes'][2]['body']['request_id']==first_id
                assert state['writes'][2]['body']==state['writes'][0]['body']
                state['held'].pop().fulfill(json={'saved':True})
                page.wait_for_function("JSON.parse(document.querySelector('#case-results').textContent).length===3")
                assert json.loads(page.locator('#case-results').inner_text())==[None,{'saved':True},{'saved':True}]
            return test
        scenario('A503-B-linked200-A-remount-retry-preserves-A-id',cross_command('linked'))
        scenario('A503-B-save200-clearSaved-A-retry-preserves-A-id',cross_command('save'))
    finally:
        browser.close()
        args.report.write_text(json.dumps(dict(results=results,network='all intercepted; no server or external endpoint'),indent=2))
