"""Hard per-run budget and private receipt, using hermetic PI transport."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from src.cli import parse_args,cmd_condition_evidence
from src.services.condition_budget import ConditionGetBudget
from src.services.condition_evidence import collect_condition_evidence
from test_condition_evidence import fixture,plan

class ConditionBudgetTest(unittest.TestCase):
    def client(self):
        p=plan();session=fixture.SyntheticSession(p,{})
        client=fixture.PiClient(fixture.PiApiConfig(base_url=fixture.BASE),session=session)
        return p,client,session
    def test_one_signal_exactly_five_gets_and_sixth_refused(self):
        p,client,session=self.client();budget=ConditionGetBudget(5);budget.install(client)
        with patch('src.adapters.pi.client.time.sleep'):
            batch=collect_condition_evidence(fixture.SyntheticBoundary(client),p)
            self.assertEqual(batch['results'][0]['status'],'COLLECTED');self.assertEqual(budget.used,5)
            with self.assertRaises(ValueError):client.request('GET','/streams/SYNTHETIC-ATTRIBUTE/value')
        self.assertEqual(budget.used,5)
    def test_history_and_writes_rejected_without_consuming_budget(self):
        _,client,_=self.client();budget=ConditionGetBudget(5);budget.install(client)
        for method,path in [('POST','/streams/x/value'),('GET','/streams/x/recorded'),('GET','/streams/x/interpolated')]:
            with self.assertRaises(ValueError):client.request(method,path)
        self.assertEqual(budget.used,0)
    def test_exhaustion_is_source_unavailable_not_retry(self):
        p,client,_=self.client();budget=ConditionGetBudget(1);budget.install(client)
        batch=collect_condition_evidence(fixture.SyntheticBoundary(client),p)
        self.assertEqual(batch['results'][0]['status'],'SOURCE_UNAVAILABLE');self.assertEqual(budget.used,1)
    def test_invalid_budget(self):
        for value in (0,26,True,1.5):
            with self.assertRaises(ValueError):ConditionGetBudget(value)
    def test_cli_private_count_and_hash_receipt(self):
        p,client,_=self.client()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);inp=root/'plan.json';inp.write_text(json.dumps(p));out=root/'out.json';report=root/'receipt.json'
            args=parse_args(['condition-evidence','--plan-file',str(inp),'--output',str(out),'--report-file',str(report),'--execute','--max-source-gets','5'])
            with patch('src.adapters.pi.client.PiClient',return_value=client),patch('src.services.governed_source.GovernedSourceBoundary',fixture.SyntheticBoundary),patch('src.adapters.pi.client.time.sleep'):
                self.assertEqual(cmd_condition_evidence(args),0)
            receipt=json.loads(report.read_text());self.assertEqual(receipt['source_gets'],5)
            self.assertEqual(receipt['handoff_sha256'],hashlib.sha256(out.read_bytes()).hexdigest())
            self.assertEqual(report.stat().st_mode & 0o777,0o600)
            self.assertNotIn('password',report.read_text())

    def test_source_config_loads_only_source_keys_and_rejects_duplicates(self):
        import os
        from src.services.condition_budget import load_managed_source_environment
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/"platform.env"
            file.write_text("PI_WEB_API_BASE_URL=https://synthetic.invalid/piwebapi\nPI_TOKEN=synthetic-only\nRELIABILITY_MART_ADMIN_DATABASE_URL=never-export\nNADI_PI_COLLECTOR_MAX_AGE_SECONDS=1800\n")
            file.chmod(0o600)
            with patch.dict(os.environ,{},clear=True):
                load_managed_source_environment(file)
                self.assertEqual(os.environ['PI_TOKEN'],'synthetic-only')
                self.assertNotIn('RELIABILITY_MART_ADMIN_DATABASE_URL',os.environ)
                self.assertNotIn('NADI_PI_COLLECTOR_MAX_AGE_SECONDS',os.environ)
                with file.open('a') as f:f.write('PI_TOKEN=other\n')
                with self.assertRaises(ValueError):load_managed_source_environment(file)
