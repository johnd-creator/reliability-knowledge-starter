"""Native PdM candidate: hermetic trusted HTTP, existing lifecycle, no live DB."""
from datetime import timedelta
from test_bundle_c_integration import BundleCIntegrationTest


class PdmInputTest(BundleCIntegrationTest):
    def multi(self, request="multi", **extra):
        stamp = (self.now - timedelta(days=1)).isoformat()
        draft = dict(canonical_asset_id=self.asset, method="VIBRATION", method_version="candidate-1",
            inspector_ref="author", inspected_at=stamp, operating_context="SYNTHETIC steady regime",
            measurements=[dict(point_ref="point:SYNTHETIC", quantity="synthetic_quantity", value=value,
                unit=unit, measured_at=(self.now-timedelta(days=1,minutes=i*13)).isoformat())
                for i, (value, unit) in enumerate(((0,"unit-A"),(None,None),("trace","unit-B"),(False,None),(4.2,"unit-A")))],
            observations=[], interpretations=["Synthetic hypothesis, not confirmed failure"],
            method_extension={"instrument_ref":"instrument:SYNTHETIC","procedure_ref":"procedure:SYNTHETIC","orientation":"SYNTHETIC"})
        draft.update(extra)
        return self.call("POST", "inspections", dict(request_id=request, draft=draft), expected=201)

    def test_multirow_original_type_null_time_and_global_history(self):
        row=self.multi()
        events=self.call("GET","inspections/measurement-history?limit=2")
        self.assertEqual((events["total"],len(events["items"]),events["has_more"]),(5,2,True))
        self.assertEqual(events["items"][0]["measurement"]["value"],0)
        self.assertIsNone(events["items"][1]["measurement"]["value"])
        rest=self.call("GET","inspections/measurement-history?offset=2&limit=2")
        self.assertEqual(rest["items"][0]["measurement"]["value"],"trace")
        self.assertIs(rest["items"][1]["measurement"]["value"],False)
        self.assertEqual(events["items"][0]["measurement"]["measured_at"],row["measurements"][0]["measured_at"])
        self.assertEqual(self.call("GET","inspections/measurement-history?point=not-recorded")["total"],0)
        self.assertEqual(self.call("GET","inspections/measurement-history?quantity=synthetic_quantity")["total"],5)
        # Absent value remains schema-default null, not zero.
        missing=self.multi("missing",measurements=[dict(quantity="not measured")])
        self.assertIsNone(missing["measurements"][0]["value"])
        self.assertEqual(missing["assessment"],"NOT_ASSESSED")

    def test_filter_before_pagination_with_exact_authorization(self):
        for i in range(27): self.multi("row:"+str(i), observations=["needle" if i==26 else "ordinary"])
        result=self.call("GET","inspections?search=needle&status=DRAFT&method=VIBRATION&limit=1")
        self.assertEqual(result["total"],1)
        self.assertEqual(result["items"][0]["observations"],["needle"])
        self.assertEqual(self.call("GET","inspections?method=MCSA")["total"],0)
        self.call("GET","inspections?asset_id=asset:FOREIGN",expected=404)
        self.call("GET","inspections/measurement-history?asset_id=asset:FOREIGN",expected=404)
        for query in ("method=PD", "status=HEALTHY", "since=2026-10-01T00:00:00", "since=invalid", "since=2026-10-09T00:00:00Z&until=2026-10-01T00:00:00Z"):
            self.call("GET","inspections?"+query,expected=422)
        # Inclusive range applied to actual samples, not inspection/update time.
        row=self.multi("range")
        time=row["measurements"][0]["measured_at"].replace("+","%2B")
        self.assertEqual(self.call("GET","inspections/measurement-history?since="+time+"&until="+time)["total"],1)

    def test_full_journey_exact_revision_handoff_and_security(self):
        self.call("GET","asset-context/"+self.asset)
        row=self.multi()
        self.assertEqual(self.call("GET","inspections/"+row["record_id"])["measurements"],row["measurements"])
        submitted=self.step("inspections",row,"submit")
        self.step("inspections",submitted,"begin_review",dict(reason="Cannot self-review"),expected=403)
        reviewed=self.step("inspections",submitted,"begin_review",dict(reason="Independent"),"reviewer")
        reviewed=self.step("inspections",reviewed,"review",dict(decision="APPROVED",reason="Record only"),"reviewer")
        case=self.call("POST","cases",dict(request_id="from-multi",draft=dict(canonical_asset_id=self.asset,title="Synthetic investigation",problem_statement="Unverified finding")),expected=201)
        evidence=dict(kind="MANUAL_INSPECTION",record_id=row["record_id"],mode="FROZEN_SNAPSHOT",expected_inspection_revision=reviewed["revision"])
        self.step("cases",case,"evidence",{**evidence,"expected_inspection_revision":1},expected=409)
        linked=self.step("cases",case,"evidence",evidence)
        human=linked["evidence"][0]["snapshot"]["reviewed_inspection"]
        self.assertEqual(human["revision"],reviewed["revision"])
        self.assertEqual(human["measurements"],reviewed["measurements"])
        self.call("POST","inspections/"+row["record_id"]+"/submit",dict(request_id="stale",expected_revision=1),expected=409)
        self.call("POST","inspections",dict(request_id="csrf",draft=dict(canonical_asset_id=self.asset,method="OTHER",method_version="candidate",inspector_ref="author")),headers={"X-CSRF-Token":"invalid"},expected=403)
        self.authority.revoke(self.directory("author"),self.credentials["author"][0])
        self.call("GET","inspections/measurement-history",expected=401)

    def test_stale_approved_evidence_cannot_silently_link_new_revision(self):
        row=self.approved_inspection(); old=row["revision"]
        row=self.step("inspections",row,"reopen",dict(reason="New review"),"reviewer")
        row=self.step("inspections",row,"submit")
        row=self.step("inspections",row,"begin_review",dict(reason="Independent"),"reviewer")
        row=self.step("inspections",row,"review",dict(decision="APPROVED",reason="Record"),"reviewer")
        case=self.call("POST","cases",dict(request_id="stale-source",draft=dict(canonical_asset_id=self.asset,title="Synthetic investigation",problem_statement="Unverified finding")),expected=201)
        self.step("cases",case,"evidence",dict(kind="MANUAL_INSPECTION",record_id=row["record_id"],mode="FROZEN_SNAPSHOT",expected_inspection_revision=old),expected=409)
        self.assertEqual(self.call("GET","cases/"+case["case_id"])["revision"],1)


# PostgreSQL qualification is restricted to the disposable GitHub CI store.
import os
import unittest
from sqlalchemy.engine import make_url
from test_bundle_c_integration import BundleCPostgresIntegrationTest

@unittest.skipUnless(os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("NADI_APPLICATION_TEST_DSN"), "CI disposable PostgreSQL only; never persistent QA")
class PdmPostgresInputTest(PdmInputTest):
    def application_engine(self):
        url=make_url(os.environ["NADI_APPLICATION_TEST_DSN"])
        if url.database != "nadi_application_test" or url.host not in {"127.0.0.1", "localhost"}:
            raise RuntimeError("Only the named disposable CI store is permitted")
        return BundleCPostgresIntegrationTest.application_engine(self)
