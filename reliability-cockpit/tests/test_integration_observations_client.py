import json
import unittest
from unittest.mock import Mock
from datetime import datetime,timezone
from src.adapters.integration_observations import LocalCollectorObservations, MAX_BYTES

class ObservationClientTest(unittest.TestCase):
    def client(self,payloads,status=200):
        session=Mock();responses=[]
        for payload in payloads:
            response=Mock(status_code=status)
            response.iter_content.return_value=[json.dumps(payload).encode()]
            response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
            responses.append(response)
        session.get.side_effect=responses
        return LocalCollectorObservations('http://collector.invalid','http://pi-collector.invalid',session=session),session
    def test_fixed_get_paths_no_source_credentials_and_successful_wo_only(self):
        time='2026-10-07T12:00:00+00:00'
        client,session=self.client([{'mxwodetail':{'watermark':time}},[
            {'object_structure':'mxwodetail','mode':'incremental','finished_at':time,'errors':0,'skipped':0},
            {'object_structure':'mxasset','finished_at':time,'errors':0,'skipped':0}]])
        result=client.maximo();self.assertEqual(result.availability,'AVAILABLE');self.assertTrue(result.cursor_present)
        self.assertIsNotNone(result.last_successful_activity);self.assertFalse(session.trust_env)
        self.assertEqual([c.args[0] for c in session.get.call_args_list],['http://collector.invalid/sync/status','http://collector.invalid/collect-runs?limit=100'])
        self.assertTrue(all(c.kwargs['allow_redirects'] is False for c in session.get.call_args_list))
    def test_error_run_and_recovery_floor_do_not_claim_success(self):
        client,_=self.client([{'mxwodetail':{}},[{'object_structure':'mxwodetail','mode':'recovery-floor','finished_at':'2026-10-07T12:00:00Z','errors':0,'skipped':0}]])
        self.assertIsNone(client.maximo().last_successful_activity)
    def test_no_configuration_does_not_use_local_default_or_network(self):
        session=Mock();client=LocalCollectorObservations(session=session)
        self.assertEqual(client.maximo().availability,'NOT_CONFIGURED');self.assertEqual(client.pi().availability,'NOT_CONFIGURED');session.get.assert_not_called()
    def test_redirect_rejected(self):
        client,_=self.client([{}],status=302);self.assertEqual(client.pi().availability,'UNKNOWN')
    def test_bounded_response_rejected(self):
        client,session=self.client([{}])
        # Rebuild response because Mock turns side_effect lists into iterators.
        response=Mock(status_code=200);response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.iter_content.return_value=[b'x'*(MAX_BYTES+1)];session.get.side_effect=None;session.get.return_value=response
        self.assertEqual(client.pi().availability,'UNKNOWN')
    def test_secret_bearing_url_is_rejected_without_http(self):
        client,session=self.client([]);client.pi_base='http://user:secret@collector.invalid'
        self.assertEqual(client.pi().availability,'UNKNOWN');session.get.assert_not_called()
    def test_invalid_or_naive_observation_cannot_claim_success(self):
        for payload in ({'availability':'AVAILABLE','last_successful_activity':'2026-10-07T12:00:00'}, {'availability':'AVAILABLE','PI_PASSWORD':'secret'}):
            client,_=self.client([payload]);self.assertEqual(client.pi().availability,'UNKNOWN')

    def test_unchanged_overlap_rows_are_not_collection_errors(self):
        time='2026-10-07T12:00:00+00:00'
        client,_=self.client([{'mxwodetail':{'watermark':time}},[{'object_structure':'mxwodetail','mode':'incremental','finished_at':time,'errors':0,'skipped':25,'upserted':0}]])
        result=client.maximo();self.assertEqual(result.errors,0);self.assertIsNotNone(result.last_successful_activity)
