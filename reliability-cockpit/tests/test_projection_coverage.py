"""Internal B4 adapter contract/security semantics; pure synthetic evidence."""
from dataclasses import replace
from datetime import datetime,timedelta,timezone
import json,unittest
from pathlib import Path
from unittest.mock import Mock
from jsonschema import Draft202012Validator,FormatChecker
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.integration_status import IntegrationStatus,IntegrationComponentStatus,Component
from src.domain.projection_coverage import Activity,DomainCoverage,CoverageSnapshot,DOMAINS
from src.repositories.projection_coverage import ProjectionCoverageReader,CoverageLimits
from src.services.projection_coverage import ProjectionCoverageService

NOW=datetime(2026,10,16,12,tzinfo=timezone.utc)
POLICY=FreshnessPolicy(maximo_wo_max_age_seconds=660,mart_factual_projection_max_age_seconds=660,pi_collector_max_age_seconds=1800)

class CoverageServiceTest(unittest.TestCase):
    def status(self):
        return IntegrationStatus(observed_at=NOW,components=tuple(IntegrationComponentStatus(component=c,
            state='CURRENT',availability='AVAILABLE',last_successful_activity=NOW,
            collection_freshness={'state':'CURRENT','observed_at':NOW,'max_age_seconds':660},
            projection_freshness={'state':'CURRENT','observed_at':NOW,'max_age_seconds':660})
            for c in Component))

    def snapshot(self):
        a=Activity('00000000-0000-4000-8000-000000000001','COMPLETE',NOW,NOW,'FULL',True,1)
        return CoverageSnapshot(NOW,'VERIFIED',tuple(DomainCoverage(d,latest=a,last_complete=a,
            reconciliation='VERIFIED',last_complete_verified=True,proof_complete=True) for d in DOMAINS))

    def apply(self,evidence=None,status=None,policy=POLICY):
        reader=Mock();reader.read.return_value=evidence or self.snapshot()
        return ProjectionCoverageService(reader,enabled=True,policy=policy,clock=lambda:NOW).reconcile(status or self.status())

    def mart(self,result): return next(c for c in result.status.components if c.component==Component.RELIABILITY_MART)

    def test_default_disabled_no_reader_io_exact_identity(self):
        reader=Mock();before=self.status();after=ProjectionCoverageService(reader).reconcile(before)
        self.assertIs(after.status,before);self.assertEqual(after.status.model_dump_json(),before.model_dump_json())
        reader.read.assert_not_called()

    def test_reader_default_disabled_no_database_io(self):
        db=Mock();out=ProjectionCoverageReader(db).read()
        self.assertEqual(out.capability,'DISABLED');db.read_snapshot.assert_not_called()
        self.assertTrue(all(d.debt is None for d in out.domains))

    def test_complete_requires_existing_independent_gates(self): self.assertEqual(self.mart(self.apply()).state,'CURRENT')

    def test_unknown_legacy_evidence_never_current(self):
        result=self.apply(CoverageSnapshot.unknown(NOW,'NO_CANDIDATE_HISTORY'))
        self.assertEqual(self.mart(result).state,'UNKNOWN');self.assertEqual(result.legacy_activity_at,NOW)

    def test_incomplete_or_blocked_never_current(self):
        for state in ('INCOMPLETE','BLOCKED','UNKNOWN'):
            s=self.snapshot();s=replace(s,domains=(replace(s.domains[0],reconciliation=state),s.domains[1]))
            with self.subTest(state=state): self.assertNotEqual(self.mart(self.apply(s)).state,'CURRENT')

    def test_old_complete_not_refreshed_by_latest_partial(self):
        s=self.snapshot();d=s.domains[1]
        s=replace(s,domains=(s.domains[0],replace(d,last_complete=replace(d.last_complete,completed_at=NOW-timedelta(hours=1)),
            latest=replace(d.latest,state='PARTIAL'),reconciliation='INCOMPLETE')))
        result=self.apply(s);self.assertNotEqual(self.mart(result).state,'CURRENT')
        self.assertEqual(self.mart(result).projection_freshness.state,'STALE')

    def test_old_complete_fails_freshness_without_changing_threshold(self):
        s=self.snapshot();s=replace(s,domains=tuple(replace(d,last_complete=replace(d.last_complete,
            completed_at=NOW-timedelta(seconds=661))) for d in s.domains))
        result=self.apply(s);self.assertEqual(self.mart(result).state,'STALE')
        self.assertEqual(self.mart(result).projection_freshness.max_age_seconds,660)
        self.assertEqual(POLICY.pi_collector_max_age_seconds,1800)

    def test_missing_policy_remains_unknown(self): self.assertEqual(self.mart(self.apply(policy=FreshnessPolicy())).state,'UNKNOWN')

    def test_existing_blocked_or_unavailable_not_upgraded(self):
        before=self.status()
        for state,availability in [('BLOCKED','AVAILABLE'),('UNKNOWN','AVAILABLE'),('DEGRADED','UNAVAILABLE'),('NOT_CONFIGURED','NOT_CONFIGURED')]:
            components=tuple(c.model_copy(update={'state':state,'availability':availability}) if c.component==Component.RELIABILITY_MART else c for c in before.components)
            with self.subTest(state=state):
                self.assertNotEqual(self.mart(self.apply(status=before.model_copy(update={'components':components}))).state,'CURRENT')

    def test_source_collection_freshness_independent(self):
        before=self.status()
        components=tuple(c.model_copy(update={'collection_freshness':c.collection_freshness.model_copy(
            update={'observed_at':NOW-timedelta(hours=1)})}) if c.component==Component.MAXIMO else c for c in before.components)
        out=self.apply(status=before.model_copy(update={'components':components}))
        self.assertNotEqual(self.mart(out).state,'CURRENT')
        self.assertEqual(self.mart(out).projection_freshness.state,'CURRENT')

    def test_incomplete_domain_set_does_not_certify_complete(self):
        s=replace(self.snapshot(),domains=(self.snapshot().domains[0],))
        self.assertEqual(self.mart(self.apply(s)).state,'UNKNOWN')

    def test_future_complete_timestamp_unknown(self):
        s=self.snapshot();s=replace(s,domains=tuple(replace(d,last_complete=replace(d.last_complete,
            completed_at=NOW+timedelta(seconds=1))) for d in s.domains))
        self.assertEqual(self.mart(self.apply(s)).state,'UNKNOWN')

    def test_pi_mapping_registry_and_source_components_byte_identical(self):
        before=self.status();after=self.apply(status=before).status
        for old,new in zip(before.components,after.components):
            if old.component!=Component.RELIABILITY_MART: self.assertEqual(old.model_dump_json(),new.model_dump_json())
        self.assertEqual(before.coverage.model_dump_json(),after.coverage.model_dump_json())
        self.assertEqual(set(before.model_dump()),set(after.model_dump()))

    def test_candidate_output_validates_unchanged_public_schema(self):
        path=Path(__file__).resolve().parents[2]/'reliability-data-contracts/schemas/integration-status.schema.json'
        validator=Draft202012Validator(json.loads(path.read_text()),format_checker=FormatChecker())
        validator.validate(self.apply().status.model_dump(mode='json'))

    def test_limits_strict_and_finite(self):
        for kw in ({'rows':0},{'rows':2001},{'runs':65},{'seconds':11},{'queries':129},{'bytes':0},{'rows':True},{'seconds':1.5}):
            with self.subTest(kw=kw),self.assertRaises(ValueError): CoverageLimits(**kw)

    def test_missing_database_is_not_configured_with_unknown_counts(self):
        result=ProjectionCoverageReader(enabled=True,expected_database='synthetic').read()
        self.assertEqual(result.capability,'NOT_CONFIGURED');self.assertIsNone(result.domains[0].manifest)

    def test_unsupported_database_never_falls_back(self):
        result=ProjectionCoverageReader(Mock(),enabled=True,expected_database='synthetic').read()
        self.assertEqual(result.domains[0].reasons,('DATABASE_IDENTITY_UNVERIFIED',))

    def test_missing_complete_proof_cannot_certify_current(self):
        s=self.snapshot();s=replace(s,domains=tuple(replace(d,proof_complete=False) for d in s.domains))
        self.assertEqual(self.mart(self.apply(s)).state,'UNKNOWN')
