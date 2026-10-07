"""Hermetic all-green and real-like identity-blocked Phase-1 gates."""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,Mock
from sqlalchemy.orm import Session
from src.cli import main,parse_args
from src.domain.phase1_readiness import GateId,Verdict,GateReason
from src.domain.integration_status import Component
from src.services.phase1_readiness import phase1_readiness
from src.repositories.mart_models import AssetAfMappingMart
import test_integration_status as fixture
import test_condition_evidence as condition_fixture
from test_condition_evidence import NOW
from test_asset_af_mapping_admin import _mapping
from dataclasses import asdict

class Phase1ReadinessTest(unittest.TestCase):
    setUp=condition_fixture.ConditionProjectionTest.setUp
    tearDown=condition_fixture.ConditionProjectionTest.tearDown
    approve=condition_fixture.ConditionProjectionTest.approve
    reader=condition_fixture.ConditionProjectionTest.reader
    source_document=condition_fixture.ConditionProjectionTest.source_document
    project=condition_fixture.ConditionProjectionTest.project
    service=fixture.IntegrationStatusTest.service
    def gates(self,result):return {g.gate:g for g in result.gates}
    def status(self):self.project(self.source_document());return self.service().status()

    def test_synthetic_all_green_reaches_pass(self):
        result=phase1_readiness(self.status())
        self.assertEqual(result.verdict,Verdict.PASS);self.assertEqual(len(result.gates),9)
        self.assertEqual(set(self.gates(result)),set(GateId));self.assertTrue(all(g.verdict==Verdict.PASS for g in result.gates))

    def test_real_like_zero_mappings_blocks_human_gate_and_projection(self):
        with Session(self.engine) as s,s.begin():
            row=s.get(AssetAfMappingMart,self.mapping_id)
            for key,value in asdict(_mapping("RETIRED")).items():
                if key!="id":setattr(row,key,value)
        result=phase1_readiness(self.service().status());gates=self.gates(result)
        self.assertEqual(result.verdict,"BLOCKED")
        for gate in (GateId.MAPPING,GateId.SIGNAL_SELECTION,GateId.CONDITION_PROJECTION):
            self.assertEqual(gates[gate].verdict,"BLOCKED");self.assertEqual(gates[gate].reason,"HUMAN_CROSSWALK_REQUIRED")
        self.assertEqual(gates[GateId.MAXIMO].verdict,"PASS")
        self.assertEqual(gates[GateId.INTEGRATION_STATUS].verdict,"PASS")

    def test_unknown_policy_cannot_pass_collection_or_projection(self):
        self.project(self.source_document());result=phase1_readiness(self.service(policy=False).status())
        self.assertEqual(self.gates(result)[GateId.PI_COLLECTOR].reason,"UNKNOWN_FRESHNESS_POLICY")
        self.assertEqual(self.gates(result)[GateId.CONDITION_PROJECTION].verdict,"UNKNOWN")
        self.assertNotEqual(result.verdict,"PASS")

    def test_source_stale_cannot_be_hidden_by_current_collector(self):
        self.project(self.source_document({"motor_current":{"Timestamp":"1970-01-01T00:00:00Z"}}))
        gates=self.gates(phase1_readiness(self.service().status()))
        self.assertEqual(gates[GateId.PI_COLLECTOR].verdict,"PASS")
        self.assertEqual(gates[GateId.CONDITION_PROJECTION].reason,"SOURCE_STALE")

    def test_missing_schema_is_separate_runtime_gate(self):
        with self.engine.begin() as c:c.exec_driver_sql("DROP TABLE condition_evidence_latest")
        gates=self.gates(phase1_readiness(self.service().status()))
        self.assertEqual(gates[GateId.CONDITION_SCHEMA].verdict,"BLOCKED")
        self.assertEqual(gates[GateId.CONDITION_SCHEMA].reason,"CONDITION_SCHEMA_NOT_READY")

    def test_partial_selection_coverage_cannot_pass(self):
        self.approve("synthetic-temp","bearing_temperature")
        self.project(self.source_document({"bearing_temperature":{"unavailable":True}}))
        gate=self.gates(phase1_readiness(self.service().status()))[GateId.CONDITION_PROJECTION]
        self.assertEqual(gate.verdict,"PARTIAL");self.assertEqual(gate.reason,"PARTIAL_SIGNAL_SET")

    def test_bad_quality_cannot_pass_even_when_current(self):
        self.project(self.source_document({"motor_current":{"Good":False}}))
        gate=self.gates(phase1_readiness(self.service().status()))[GateId.CONDITION_PROJECTION]
        self.assertEqual(gate.reason,"QUALITY_NOT_ACCEPTED");self.assertEqual(gate.verdict,"PARTIAL")

    def test_cli_default_local_is_read_only_and_json_no_admin_or_credentials(self):
        status=self.status()
        args=parse_args(["phase1-readiness"]);self.assertFalse(args.require_pass);self.assertIsNone(args.status_file)
        with patch("src.api.reliability._integration_service") as service,patch("src.cli.get_database") as legacy,patch("src.cli.AssetAfMappingCommandStore") as admin:
            service.return_value.status.return_value=status
            out=io.StringIO()
            with contextlib.redirect_stdout(out):self.assertEqual(args.func(args),0)
            document=json.loads(out.getvalue());self.assertEqual(document["evidence_origin"],"LOCAL_RUNTIME")
            self.assertEqual(document["verdict"],"PASS");legacy.assert_not_called();admin.assert_not_called()
            for forbidden in ("password","Authorization","af_element_ref","12.5"):
                self.assertNotIn(forbidden,json.dumps(document))

    def test_offline_cli_marks_origin_and_require_pass_exit(self):
        self.project(self.source_document());status=self.service(policy=False).status()
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/"status.json";file.write_text(status.model_dump_json())
            args=parse_args(["phase1-readiness","--status-file",str(file),"--require-pass"])
            output=io.StringIO()
            with patch("src.api.reliability._integration_service") as live,contextlib.redirect_stdout(output):
                self.assertEqual(args.func(args),2);live.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())["evidence_origin"],"OPERATOR_DOCUMENT")

    def test_cli_errors_do_not_echo_secret_document_or_dsn(self):
        args=parse_args(["phase1-readiness"])
        with patch("src.api.reliability._integration_service",side_effect=RuntimeError("postgresql://secret")):
            output=io.StringIO()
            with contextlib.redirect_stdout(output):self.assertEqual(args.func(args),2)
            self.assertEqual(json.loads(output.getvalue())["reason"],"PREFLIGHT_OBSERVATION_FAILED")
            self.assertNotIn("secret",output.getvalue())
