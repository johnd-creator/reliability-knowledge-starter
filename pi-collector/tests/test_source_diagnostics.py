"""Source-free first-request diagnostics, redaction, and accounting."""
import ast, io, json, tempfile, unittest
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import Mock, patch
import requests
from src.adapters.pi.client import PiClient, PiClientError, new_session
from src.config import PiApiConfig
from src.domain.source_diagnostics import SourceFailureCode
from src.services.condition_budget import ConditionGetBudget
from src.services.condition_evidence import collect_condition_evidence
from src.services.governed_source import GovernedSourceBoundary
from src.cli import parse_args, cmd_condition_evidence
from test_condition_evidence import plan, fixture
SECRET = 'SYNTHETIC_PASSWORD_TOKEN_COOKIE_SECRET'
PRIVATE_URL = 'https://private.synthetic.invalid/secret'

def response(status=200, payload=None, raw=None):
    r = requests.Response()
    r.status_code = status
    r._content = raw if raw is not None else json.dumps(payload).encode()
    r._content_consumed = True
    return r

class SourceDiagnosticsTest(unittest.TestCase):

    def acquire(self, effect):
        session = Mock()
        session.request.side_effect = effect
        client = PiClient(PiApiConfig(base_url=fixture.BASE, username='synthetic', password=SECRET), session=session)
        budget = ConditionGetBudget(5)
        budget.install(client)
        codes = []
        batch = collect_condition_evidence(GovernedSourceBoundary(client), plan(), diagnostics=codes)
        self.assertEqual(budget.used, 1)
        self.assertEqual(session.request.call_count, 1)
        self.assertEqual(batch['results'][0]['status'], 'SOURCE_UNAVAILABLE')
        self.assertIsNone(batch['results'][0]['evidence'])
        call = session.request.call_args
        self.assertTrue(call.args[1].endswith('/elements/' + plan()['sources']['pi']['af_element_ref']))
        self.assertFalse(call.kwargs['allow_redirects'])
        for text in [SECRET, PRIVATE_URL]:
            self.assertNotIn(text, json.dumps([batch, codes]))
        return codes[0]['code']

    def test_transport_categories_no_retry(self):
        for error, code in [(requests.exceptions.SSLError, 'SOURCE_TLS_FAILED'), (requests.exceptions.Timeout, 'SOURCE_TIMEOUT'), (requests.exceptions.ConnectionError, 'SOURCE_CONNECT_FAILED'), (requests.exceptions.RequestException, 'SOURCE_CAUSE_UNKNOWN')]:
            with self.subTest(code=code):
                self.assertEqual(self.acquire(error(SECRET + PRIVATE_URL)), code)

    def test_http_categories(self):
        for status, code in [(401, 'SOURCE_AUTH_FAILED'), (403, 'SOURCE_AUTH_FAILED'), (410, 'SOURCE_HTTP_ERROR'), (500, 'SOURCE_HTTP_ERROR'), (302, 'SOURCE_HTTP_ERROR')]:
            with self.subTest(status=status):
                self.assertEqual(self.acquire(lambda *a, **k: response(status, {'secret': SECRET})), code)

    def test_json_and_lineage(self):
        for r in [response(raw=(SECRET + PRIVATE_URL).encode()), response(payload=[SECRET]), response(payload={'WebId': 'WRONG'}), response(payload={'WebId': plan()['sources']['pi']['af_element_ref'], 'Links': {'Database': PRIVATE_URL}})]:
            with self.subTest():
                self.assertEqual(self.acquire(lambda *a, **k: r), 'SOURCE_CONTRACT_INVALID')

    def test_unknown_and_spoofed_error_redacted(self):
        for error in [ValueError(SECRET + PRIVATE_URL), PiClientError(SECRET + PRIVATE_URL)]:
            error.failure_code = SECRET + PRIVATE_URL
            b = Mock()
            b.get_evidence_snapshot.side_effect = error
            codes = []
            batch = collect_condition_evidence(b, plan(), diagnostics=codes)
            self.assertEqual(codes[0]['code'], 'SOURCE_CAUSE_UNKNOWN')
            for text in [SECRET, PRIVATE_URL]:
                self.assertNotIn(text, json.dumps([batch, codes]))

    def test_budget_exhaustion_no_extra_transport(self):
        p = plan()
        s = fixture.SyntheticSession(p, {})
        c = PiClient(PiApiConfig(base_url=fixture.BASE), session=s)
        budget = ConditionGetBudget(1)
        budget.install(c)
        codes = []
        batch = collect_condition_evidence(GovernedSourceBoundary(c), p, diagnostics=codes)
        self.assertEqual(budget.used, 1)
        self.assertEqual(len(s.calls), 1)
        self.assertIsNone(batch['results'][0]['evidence'])
        self.assertEqual(codes[0]['code'], 'SOURCE_BUDGET_EXHAUSTED')

    def test_default_session_no_retry(self):
        with new_session() as s:
            for scheme in ['https://', 'http://']:
                self.assertEqual(s.get_adapter(scheme).max_retries.total, 0)

    def test_private_cli_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            inp = d / 'plan.json'
            inp.write_text(json.dumps(plan()))
            args = parse_args(['condition-evidence', '--plan-file', str(inp), '--execute', '--output', str(d / 'handoff.json'), '--report-file', str(d / 'receipt.json'), '--max-source-gets', '5', '--diagnostics'])
            s = Mock()
            s.__enter__ = Mock(return_value=s)
            s.__exit__ = Mock(return_value=False)
            s.request.side_effect = requests.exceptions.SSLError(SECRET + PRIVATE_URL)
            out, err = (io.StringIO(), io.StringIO())
            with patch('src.adapters.pi.client.new_session', return_value=s), patch.dict('os.environ', {'PI_WEB_API_BASE_URL': fixture.BASE}, clear=True), redirect_stdout(out), redirect_stderr(err):
                self.assertEqual(cmd_condition_evidence(args), 0)
            receipt = json.loads((d / 'receipt.json').read_text())
            self.assertEqual(receipt['contract_version'], '1.1')
            self.assertEqual(receipt['source_gets'], 1)
            self.assertEqual(receipt['max_source_gets'], 5)
            self.assertEqual(receipt['source_failures'], [{'signal_id': plan()['signals'][0]['signal_id'], 'code': 'SOURCE_TLS_FAILED'}])
            self.assertEqual((d / 'receipt.json').stat().st_mode & 511, 384)
            handoff = json.loads((d / 'handoff.json').read_text())
            self.assertNotIn('source_failures', handoff)
            self.assertIsNone(handoff['results'][0]['evidence'])
            for text in [SECRET, PRIVATE_URL]:
                self.assertNotIn(text, out.getvalue() + err.getvalue() + json.dumps([receipt, handoff]))

    def test_consumer_allowlist_matches(self):
        tree = ast.parse((Path(__file__).resolve().parents[2] / 'reliability-cockpit/src/services/condition_refresh.py').read_text())
        n = next((n for n in tree.body if isinstance(n, ast.Assign) and any((isinstance(t, ast.Name) and t.id == 'SAFE_SOURCE_FAILURE_CODES' for t in n.targets))))
        self.assertEqual(set(ast.literal_eval(n.value.args[0])), {c.value for c in SourceFailureCode})
