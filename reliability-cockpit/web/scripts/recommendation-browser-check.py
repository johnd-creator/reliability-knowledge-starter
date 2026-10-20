"""Manual isolated regression: build scripts/recommendation/entry.tsx with browserBundle,
then pass --bundle /tmp/.../candidate.js and an explicitly trusted --chromium path.
Every browser request is intercepted; this test starts no HTTP/Next/API service.
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
origin = 'https://recommendation-fixture.invalid'
results = []
initial = dict(record_id='recommendation:fixture', canonical_asset_id='asset:qa', revision=7,
               status='DRAFT', created_at='2026-10-20T00:00:00Z', updated_at='2026-10-20T00:00:00Z',
               created_by='author', review=None, case_ref='case:fixture', rationale='Original rationale',
               proposed_action='Original action', priority='HUMAN', responsible_team_ref=None,
               responsible_person_ref=None, target_date=None, follow_up_status='PROPOSED',
               existing_work_order_ref=None, reviewed_case=None, completion_verification=None,
               supporting_evidence=[], provenance='SYNTHETIC_QA')

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, executable_path=str(args.chromium))
    try:
        def scenario(name, test):
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(5000)
            state = dict(row=initial.copy(), writes=[], held=[], mode='ok', escaped=[])
            def route(request_route):
                req = request_route.request
                if req.url == origin + '/recommendations':
                    request_route.fulfill(body='<html><body><div id="root"></div><script src="/candidate.js"></script></body></html>', content_type='text/html')
                elif req.url == origin + '/candidate.js':
                    request_route.fulfill(body=bundle, content_type='text/javascript')
                elif req.url.startswith(origin + '/api/engineering-qa/recommendations/'):
                    if req.method == 'GET':
                        request_route.fulfill(json=state['row'])
                    else:
                        state['writes'].append(dict(method=req.method, body=req.post_data_json, csrf=req.headers.get('x-csrf-token')))
                        if state['mode'] == 'hold':
                            state['held'].append(request_route)
                        elif state['mode'] == 'unavailable':
                            request_route.fulfill(status=503, json={'detail': {'code': 'QA_BACKEND_UNAVAILABLE'}})
                        elif req.post_data_json['expected_revision'] != state['row']['revision']:
                            request_route.fulfill(status=409, json={'detail': {'code': 'REVISION_CONFLICT'}})
                        else:
                            state['row'].update(req.post_data_json.get('draft', {}))
                            state['row']['revision'] += 1
                            request_route.fulfill(json=state['row'])
                else:
                    state['escaped'].append(req.url)
                    request_route.abort()
            context.route('**/*', route)
            try:
                page.goto(origin + '/recommendations')
                page.locator('#recommendation-rationale').wait_for()
                test(page, state)
                assert not state['escaped'], state['escaped']
                results.append(dict(name=name, result='PASS', writes=state['writes']))
                print('PASS', name)
            except Exception as exc:
                results.append(dict(name=name, result='FAIL', error=str(exc), writes=state['writes']))
                raise
            finally:
                context.close()

        def remount(page):
            page.evaluate('recommendationFixture.mount(false)')
            page.locator('#recommendation-rationale').wait_for(state='detached')
            page.evaluate('recommendationFixture.mount(true)')
            page.locator('#recommendation-rationale').wait_for()

        def check_value(page, value):
            assert page.locator('#recommendation-rationale').input_value() == value

        def dirty_submit(page, state):
            page.locator('#recommendation-rationale').fill('Edited rationale')
            assert page.get_by_role('button', name='Ajukan rekomendasi untuk review', exact=True).is_disabled()
            assert not state['writes']
            for selector, value in [('#recommendation-action', 'Edited action'), ('#recommendation-owner', 'person:qa'), ('#recommendation-team', 'team:qa'), ('#recommendation-date', '2026-11-20')]:
                page.locator(selector).fill(value)
            page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).click()
            page.wait_for_function("document.querySelector('[data-testid=recovery]').textContent==='EMPTY'")
            assert len(state['writes']) == 1 and state['writes'][0]['method'] == 'PUT'
            write = state['writes'][0]
            assert write['csrf'] == 'synthetic-only' and write['body']['expected_revision'] == 7
            assert write['body']['draft']['rationale'] == 'Edited rationale'
            assert write['body']['draft']['proposed_action'] == 'Edited action'
            assert write['body']['draft']['responsible_person_ref'] == 'person:qa'
            assert write['body']['draft']['responsible_team_ref'] == 'team:qa'
            assert write['body']['draft']['target_date'] == '2026-11-20'
            page.locator('#recommendation-rationale').wait_for()
            assert page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).is_disabled()
            assert page.get_by_role('button', name='Ajukan rekomendasi untuk review', exact=True).is_enabled()
        scenario('dirty-submit-blocked-explicit-save-all-fields', dirty_submit)

        def recovery(page, state):
            page.locator('#recommendation-rationale').fill('Unsaved after focus')
            page.evaluate('recommendationFixture.transient()')
            remount(page)
            check_value(page, 'Unsaved after focus')
            page.evaluate("recommendationFixture.session({csrf_token:'refreshed-synthetic'})")
            remount(page)
            check_value(page, 'Unsaved after focus')
            assert not state['writes']
        scenario('focus-remount-and-csrf-refresh-retain-draft', recovery)

        def retry(page, state):
            page.locator('#recommendation-rationale').fill('Retry unchanged intent')
            state['mode'] = 'unavailable'
            page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).click()
            page.wait_for_function("document.querySelector('[data-testid=busy]').textContent==='false'")
            remount(page)
            check_value(page, 'Retry unchanged intent')
            state['mode'] = 'ok'
            page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).click()
            page.wait_for_function("document.querySelector('[data-testid=recovery]').textContent==='EMPTY'")
            assert len(state['writes']) == 2
            assert state['writes'][0]['body']['request_id'] == state['writes'][1]['body']['request_id']
        scenario('503-remount-retry-retains-values-and-request-id', retry)

        def conflict(page, state):
            page.locator('#recommendation-rationale').fill('Original base draft')
            state['row']['revision'] = 8
            page.evaluate('recommendationFixture.row({revision:8})')
            check_value(page, 'Original base draft')
            page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).click()
            page.wait_for_function("document.querySelector('[data-testid=busy]').textContent==='false'")
            assert state['writes'][0]['body']['expected_revision'] == 7
            check_value(page, 'Original base draft')
            assert '"revision":7' in page.locator('[data-testid=recovery]').inner_text()
            page.once('dialog', lambda dialog: dialog.dismiss())
            page.get_by_role('button', name='Batalkan perubahan Recommendation', exact=True).click()
            check_value(page, 'Original base draft')
            page.once('dialog', lambda dialog: dialog.accept())
            page.get_by_role('button', name='Batalkan perubahan Recommendation', exact=True).click()
            check_value(page, 'Original rationale')
            assert page.locator('[data-testid=recovery]').inner_text() == 'EMPTY'
        scenario('conflict-keeps-original-CAS-and-confirmed-cancel-rebases', conflict)

        def identity_clear(patch):
            def test(page, state):
                page.locator('#recommendation-rationale').fill('Private draft')
                page.evaluate('(patch)=>recommendationFixture.session(patch)', patch)
                page.wait_for_function("document.querySelector('[data-testid=recovery]').textContent==='EMPTY'")
                page.evaluate("recommendationFixture.session({subject:'author',roles:['AUTHOR'],asset_ids:['asset:qa']})")
                page.locator('#recommendation-rationale').wait_for()
                check_value(page, 'Original rationale')
                assert not state['writes']
            return test
        for label, patch in [('subject',dict(subject='other')),('role',dict(roles=['REVIEWER'])),('scope',dict(asset_ids=['asset:other'])),('added-role',dict(roles=['AUTHOR','REVIEWER'])),('added-scope',dict(asset_ids=['asset:qa','asset:other']))]:
            scenario(label+'-change-clears-private-draft', identity_clear(patch))

        def expired(page, state):
            page.locator('#recommendation-rationale').fill('Private expired draft')
            page.evaluate('recommendationFixture.expire()')
            page.wait_for_function("document.querySelector('[data-testid=recovery]').textContent==='EMPTY'")
            remount(page)
            check_value(page, 'Original rationale')
        scenario('confirmed-expiry-clears-recovery', expired)

        def pending(page, state):
            page.locator('#recommendation-rationale').fill('Pending draft')
            state['mode'] = 'hold'
            page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).click()
            page.wait_for_function("document.querySelector('[data-testid=busy]').textContent==='true'")
            remount(page)
            check_value(page, 'Pending draft')
            assert page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).is_disabled()
            assert page.get_by_role('button', name='Batalkan perubahan Recommendation', exact=True).is_disabled()
            assert len(state['writes']) == 1
            state['row'].update(state['writes'][0]['body']['draft'])
            state['row']['revision'] = 8
            state['held'].pop().fulfill(json=state['row'])
            page.wait_for_function("document.querySelector('[data-testid=busy]').textContent==='false'")
            page.wait_for_function("document.querySelector('[data-testid=recovery]').textContent==='EMPTY'")
            assert len(state['writes']) == 1
        scenario('pending-remount-lock-prevents-second-write-and-discard', pending)

        def pending_identity(page, state):
            page.locator('#recommendation-rationale').fill('Old identity pending draft')
            state['mode'] = 'hold'
            page.get_by_role('button', name='Simpan draf rekomendasi', exact=True).click()
            page.wait_for_function("document.querySelector('[data-testid=busy]').textContent==='true'")
            page.evaluate("recommendationFixture.session({subject:'other'})")
            page.wait_for_function("document.querySelector('[data-testid=recovery]').textContent==='EMPTY'")
            state['held'].pop().fulfill(json={**state['row'], 'rationale':'Late old response', 'revision':8})
            page.evaluate("recommendationFixture.session({subject:'author'})")
            page.locator('#recommendation-rationale').wait_for()
            check_value(page, 'Original rationale')
            assert page.locator('[data-testid=recovery]').inner_text() == 'EMPTY'
            assert len(state['writes']) == 1
        scenario('late-write-response-cannot-resurrect-cleared-identity-draft', pending_identity)

        def other_record(page, state):
            page.locator('#recommendation-rationale').fill('Retained record A draft')
            page.evaluate("recommendationFixture.row({record_id:'recommendation:other',rationale:'Record B original'})")
            check_value(page, 'Record B original')
            page.once('dialog', lambda dialog: dialog.dismiss())
            page.locator('#recommendation-rationale').fill('Record B edit')
            check_value(page, 'Record B original')
            assert 'Retained record A draft' in page.locator('[data-testid=recovery]').inner_text()
            page.once('dialog', lambda dialog: dialog.accept())
            page.locator('#recommendation-rationale').fill('Record B edit')
            check_value(page, 'Record B edit')
            recovery = json.loads(page.locator('[data-testid=recovery]').inner_text())
            assert recovery['base']['record_id'] == 'recommendation:other'
            assert recovery['draft']['rationale'] == 'Record B edit'
            assert not state['writes']
        scenario('different-record-edit-requires-explicit-prior-draft-discard', other_record)
    finally:
        browser.close()
        args.report.write_text(json.dumps(dict(results=results, network='all intercepted; no server or external endpoint'), indent=2))
