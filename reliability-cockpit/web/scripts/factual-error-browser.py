"""Actual Overview component; all requests intercepted before network/TLS."""
from pathlib import Path
import json,sys,os
from playwright.sync_api import sync_playwright

def main():
 bundle=Path(sys.argv[1]).read_text();results=[];escaped=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE'))
  try:
   for scenario in [403,503,500,'network']:
    context=browser.new_context();page=context.new_page()
    def route(r):
     url=r.request.url
     if url=='https://nadi-factual-fixture.invalid/':r.fulfill(content_type='text/html',body='<html><body><div id="root"></div><script src="/candidate.js"></script></body></html>')
     elif url.endswith('/candidate.js'):r.fulfill(content_type='application/javascript',body=bundle)
     elif '/api/cockpit/v1/reliability/decision-overview?' in url:
      if scenario=='network':r.abort()
      else:r.fulfill(status=scenario,json={'detail':{'code':'INTERNAL_SECRET_DO_NOT_RENDER'}})
     else:escaped.append(url);r.abort()
    context.route('**/*',route);page.goto('https://nadi-factual-fixture.invalid/')
    expected='Akses data faktual memerlukan capability atau scope' if scenario==403 else 'Layanan data faktual belum tersedia'
    page.get_by_role('alert').filter(has_text=expected).wait_for();text=page.locator('body').inner_text();assert 'INTERNAL_SECRET' not in text;assert 'Reliability Mart tidak tersedia' not in text
    results.append({'scenario':scenario,'visible_message':expected,'passed':True});context.close()
   assert not escaped
  finally:browser.close()
 print(json.dumps({'actual_overview_component':True,'scenarios':results,'unexpected_requests':escaped,'no_real_session_or_tls_bypass':True},indent=2))
if __name__=='__main__':main()
