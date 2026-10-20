"""Actual local catalogs: factual pin upgrades and owning-store lock order."""
import json
import os
import threading
import unittest
from hashlib import sha256
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from jsonschema import Draft202012Validator

from sqlalchemy import event, select, update, text
from src.domain.engineering import EngineeringError, EvidenceKind
from src.repositories.mart_models import AssetMasterMart, MaintenanceEventMart, FmeaAssessmentMart
import test_bundle_c_integration as fixture


class EngineeringIntegrityTest(unittest.TestCase):
    # Reuse supported setup/helpers without collecting its inherited test suite.
    application_engine = fixture.BundleCIntegrationTest.application_engine
    setUp = fixture.BundleCIntegrationTest.setUp
    tearDown = fixture.BundleCIntegrationTest.tearDown
    call = fixture.BundleCIntegrationTest.call
    step = fixture.BundleCIntegrationTest.step
    create_inspection = fixture.BundleCIntegrationTest.create_inspection
    approved_inspection = fixture.BundleCIntegrationTest.approved_inspection
    approved_case = fixture.BundleCIntegrationTest.approved_case

    def proposal(self, *, kind="MAINTENANCE", record="maintenance:SYNTHETIC:C", key="rec", case=None):
        if case is None:
            inspection = self.approved_inspection()
            case = self.approved_case(inspection)
        return self.recommendations.command(self.directory("author"), "CREATE", dict(
            canonical_asset_id=self.asset, case_ref=case["case_id"], rationale="Synthetic finding",
            proposed_action="Synthetic proposal", evidence_selections=[dict(kind=kind,
                record_id=record, mode="FROZEN_SNAPSHOT")]), key)

    def change(self, row, action, payload=None, *, reviewer=False, key=None):
        return self.recommendations.command(self.directory("reviewer" if reviewer else "author"),
            action, payload or {}, key or f"{action}-{row.record_id}-{row.revision}",
            record_id=row.record_id, expected_revision=row.revision)

    def correction(self, **values):
        with self.pi.engine.begin() as c:
            c.execute(update(MaintenanceEventMart).where(
                MaintenanceEventMart.canonical_id == "maintenance:SYNTHETIC:C").values(**values))

    def refused_unchanged(self, row, operation):
        history = self.recommendations.history(self.directory("author"), row.record_id)
        with self.assertRaises(EngineeringError) as error:
            operation()
        self.assertEqual(error.exception.code, "EVIDENCE_VERSION_CHANGED")
        self.assertEqual(self.recommendations.get(self.directory("author"), row.record_id), row)
        self.assertEqual(self.recommendations.history(self.directory("author"), row.record_id), history)

    def test_content_correction_same_timestamp_blocks_all_new_actions_and_preserves_history(self):
        row = self.proposal()
        self.assertTrue(row.supporting_evidence[0].stable_version.startswith("mart-facts-v2:"))
        self.correction(status="CAN")
        self.refused_unchanged(row, lambda: self.change(row, "SUBMIT"))
        self.correction(status="COMP")
        row = self.change(row, "SUBMIT")
        review = dict(decision="APPROVED", reason="Independent review")
        self.correction(status="CAN")
        self.refused_unchanged(row, lambda: self.change(row, "REVIEW", review, reviewer=True))
        self.correction(status="COMP")
        row = self.change(row, "REVIEW", review, reviewer=True)
        self.correction(labor_hours=1.5)
        self.refused_unchanged(row, lambda: self.change(row, "FOLLOWUP", dict(status="PLANNED", reason="Local")))
        self.correction(labor_hours=None)
        for status in ("PLANNED", "IN_PROGRESS", "COMPLETED"):
            row = self.change(row, "FOLLOWUP", dict(status=status, reason="Local"))
        complete = dict(reason="Independent local verification", evidence_selections=[dict(
            kind="MAINTENANCE", record_id="maintenance:SYNTHETIC:C", mode="FROZEN_SNAPSHOT")])
        self.correction(status="CAN")
        self.refused_unchanged(row, lambda: self.change(row, "VERIFY_COMPLETION", complete, reviewer=True))
        self.correction(status="COMP")
        done = self.change(row, "VERIFY_COMPLETION", complete, reviewer=True)
        self.assertEqual(done.follow_up_status, "VERIFIED")
        self.assertEqual(done.supporting_evidence, row.supporting_evidence)

    def test_legacy_factual_pins_fail_closed_without_implicit_history_rewrite(self):
        # Emulate old adapter output at capture, not a migration or DB rewrite.
        original = self.local.resolve
        def legacy(*args, **kwargs):
            ref = original(*args, **kwargs)
            digest = sha256(json.dumps(dict(snapshot=ref.snapshot.model_dump(mode="json"),
                timestamp=ref.source_timestamp.isoformat() if ref.source_timestamp else None),
                sort_keys=True).encode()).hexdigest()
            return ref.model_copy(update={"stable_version": digest})
        with patch.object(self.local, "resolve", side_effect=legacy):
            draft = self.proposal(key="legacy-draft")
            submitted = self.change(draft, "SUBMIT")
            approved = self.change(submitted, "REVIEW", dict(decision="APPROVED", reason="Old review"), reviewer=True)
        self.refused_unchanged(approved, lambda: self.change(approved, "FOLLOWUP", dict(status="PLANNED", reason="New")))
        self.assertEqual(len(approved.supporting_evidence[0].stable_version), 64)

    def test_allowlisted_content_identity_and_provenance_change_versions_but_ingest_churn_does_not(self):
        def resolve(kind="MAINTENANCE", record="maintenance:SYNTHETIC:C"):
            return self.local.resolve(self.asset, EvidenceKind(kind), record, "FROZEN_SNAPSHOT", "author", self.now)
        baseline = resolve()
        self.correction(sources={"maximo": {"password": "DO-NOT-COPY", "raw": "ignored"}},
            provenance={"ingested_at": "later", "password": "DO-NOT-COPY"}, reported_by="private-person")
        self.assertEqual(resolve().stable_version, baseline.stable_version)
        self.assertNotIn("DO-NOT-COPY", resolve().model_dump_json())
        self.correction(provenance={"source_record_id": "changed-identity"})
        self.assertNotEqual(resolve().stable_version, baseline.stable_version)
        with self.pi.engine.begin() as c:
            c.execute(update(AssetMasterMart).where(AssetMasterMart.canonical_id == self.asset).values(status="OPERATING"))
        asset = resolve("ASSET", self.asset)
        with self.pi.engine.begin() as c:
            c.execute(update(AssetMasterMart).where(AssetMasterMart.canonical_id == self.asset).values(status="DECOMMISSIONED"))
        self.assertNotEqual(resolve("ASSET", self.asset).stable_version, asset.stable_version)
        with self.pi.engine.begin() as c:
            c.execute(FmeaAssessmentMart.__table__.insert().values(canonical_id="fmea:SYNTHETIC:1",
                contract_version="1.0", asset_ref=self.asset, lifecycle_status="ACTIVE", site_code="BSR",
                organization_code="IP", provenance={}, relationship_evidence={},
                mart_created_at=self.now, mart_updated_at=self.now))
        fmea = resolve("FMEA", "fmea:SYNTHETIC:1")
        with self.pi.engine.begin() as c:
            c.execute(update(FmeaAssessmentMart).values(revision="2"))
        self.assertNotEqual(resolve("FMEA", "fmea:SYNTHETIC:1").stable_version, fmea.stable_version)
        self.assertNotEqual(resolve("WORK_ORDER", "WO-C").stable_version, resolve().stable_version)

    def test_factual_digest_rejects_nonfinite_and_invalid_scalar_types(self):
        self.correction(labor_hours=float("inf"))
        with self.assertRaises(EngineeringError) as error:
            self.local.resolve(self.asset, EvidenceKind.MAINTENANCE, "maintenance:SYNTHETIC:C", "FROZEN_SNAPSHOT", "author", self.now)
        self.assertEqual(error.exception.code, "EVIDENCE_CONTENT_INVALID")
        with self.pi.engine.begin() as c:
            c.execute(update(AssetMasterMart).values(criticality={"not": "a canonical scalar"}))
        with self.assertRaises(EngineeringError):
            self.local.resolve(self.asset, EvidenceKind.ASSET, self.asset, "FROZEN_SNAPSHOT", "author", self.now)

    def test_contract_valid_large_unicode_content_is_stable_and_changes_are_detected(self):
        schema = json.loads((Path(__file__).resolve().parents[2] /
            "reliability-data-contracts/schemas/asset-master.schema.json").read_text())
        # Owning source schema has no description/status maxLength; do not
        # introduce a 12k business limit or 32KiB encoded-document limit here.
        description_schema = schema["properties"]["description"]
        status_schema = schema["properties"]["status"]
        for content in ("x" * 12001, "\U0001f642\u754c\u00e9" * 20000):
            with self.subTest(codepoints=len(content)):
                Draft202012Validator(description_schema).validate(content)
                Draft202012Validator(status_schema).validate(content)
                with self.pi.engine.begin() as c:
                    c.execute(update(AssetMasterMart).values(description=content))
                first = self.local.resolve(self.asset, EvidenceKind.ASSET, self.asset,
                    "FROZEN_SNAPSHOT", "author", self.now)
                again = self.local.resolve(self.asset, EvidenceKind.ASSET, self.asset,
                    "FROZEN_SNAPSHOT", "author", self.now)
                self.assertEqual(first.stable_version, again.stable_version)
                self.assertLess(len(first.model_dump_json().encode()), 16384)
                changed = content[:-1] + ("y" if content[-1] == "x" else "\u00e8")
                self.assertEqual(len(content), len(changed))
                self.assertEqual(len(content.encode()), len(changed.encode()))
                with self.pi.engine.begin() as c:
                    c.execute(update(AssetMasterMart).values(description=changed))
                corrected = self.local.resolve(self.asset, EvidenceKind.ASSET, self.asset,
                    "FROZEN_SNAPSHOT", "author", self.now)
                self.assertNotEqual(first.stable_version, corrected.stable_version)


@unittest.skipUnless(os.getenv("NADI_APPLICATION_TEST_DSN"), "disposable application PostgreSQL fixture not configured")
class EngineeringIntegrityPostgresTest(EngineeringIntegrityTest):
    application_engine = fixture.BundleCPostgresIntegrationTest.application_engine

    def test_expected_inspection_link_locks_case_before_inspection_and_retains_cas(self):
        inspection = self.approved_inspection()
        row = self.cases.command(self.directory("author"), "CREATE", dict(canonical_asset_id=self.asset,
            title="Link lock order", problem_statement="Synthetic lock regression"), "link-case")
        statements = []
        def trace(connection, cursor, statement, parameters, context, many):
            if "FOR UPDATE" in statement:
                statements.append(statement)
        event.listen(self.engine, "before_cursor_execute", trace)
        try:
            linked = self.cases.command(self.directory("author"), "LINK", dict(kind="MANUAL_INSPECTION",
                record_id=inspection["record_id"], mode="FROZEN_SNAPSHOT",
                expected_inspection_revision=inspection["revision"]), "link-inspection",
                case_id=row.case_id, expected_revision=row.revision)
        finally:
            event.remove(self.engine, "before_cursor_execute", trace)
        self.assertEqual(len(statements), 2)
        self.assertIn("engineering_case", statements[0])
        self.assertIn("nadi_human_record", statements[1])
        self.assertEqual(linked.evidence[0].snapshot.reviewed_inspection.revision, inspection["revision"])
        with self.assertRaises(EngineeringError) as error:
            self.cases.command(self.directory("author"), "NOTE", dict(text="Stale"), "stale-link",
                case_id=row.case_id, expected_revision=row.revision)
        self.assertEqual(error.exception.code, "REVISION_CONFLICT")

    def test_completion_union_has_one_sorted_inspection_order_across_distinct_cases(self):
        one = self.approved_inspection()
        two = self.inspections.command(self.directory("author"), "CREATE", dict(
            canonical_asset_id=self.asset, method="VIBRATION", method_version="proposal-1",
            inspector_ref="author", inspected_at=self.now.isoformat(), observations=["Synthetic second inspection"]), "inspection-two")
        for action, payload, actor in (("SUBMIT", {}, "author"),
                ("BEGIN_REVIEW", dict(reason="Independent start"), "reviewer"),
                ("REVIEW", dict(decision="APPROVED", reason="Independent review"), "reviewer")):
            two = self.inspections.command(self.directory(actor), action, payload, "two-"+action,
                record_id=two.record_id, expected_revision=two.revision)
        ids = sorted([one["record_id"], two.record_id])
        proposals = []
        for index, record in enumerate(ids):
            case = self.cases.command(self.directory("author"), "CREATE", dict(canonical_asset_id=self.asset,
                title="Completion case " + str(index), problem_statement="Synthetic"), f"case-{index}")
            case = self.cases.command(self.directory("author"), "SUBMIT", {}, f"case-submit-{index}",
                case_id=case.case_id, expected_revision=case.revision)
            case = self.cases.command(self.directory("reviewer"), "REVIEW", dict(decision="APPROVED", reason="Independent"),
                f"case-review-{index}", case_id=case.case_id, expected_revision=case.revision)
            row = self.proposal(kind="MANUAL_INSPECTION", record=record, key=f"rec-{index}",
                case={"case_id": case.case_id})
            row = self.change(row, "SUBMIT")
            row = self.change(row, "REVIEW", dict(decision="APPROVED", reason="Independent"), reviewer=True)
            for status in ("PLANNED", "IN_PROGRESS", "COMPLETED"):
                row = self.change(row, "FOLLOWUP", dict(status=status, reason="Synthetic local report"))
            proposals.append(row)
        barrier = threading.Barrier(2, timeout=6)
        original = self.recommendations.catalog.guard_case
        def guard(*args, **kwargs):
            case = original(*args, **kwargs)
            barrier.wait()  # Each transaction holds a different Case row.
            return case
        orders = {"verify-a": [], "verify-b": []}
        def trace(connection, cursor, statement, parameters, context, many):
            lane = threading.current_thread().name
            if lane in orders and "FOR UPDATE" in statement and "nadi_human_record" in statement:
                record = parameters["record_id_1"]
                if record not in orders[lane]:
                    orders[lane].append(record)
        event.listen(self.engine, "before_cursor_execute", trace)
        try:
            operations = {name: (lambda row=row, other=other: self.change(row, "VERIFY_COMPLETION",
                dict(reason="Independent verification", evidence_selections=[dict(kind="MANUAL_INSPECTION",
                    record_id=other, mode="FROZEN_SNAPSHOT")]), reviewer=True))
                for name, row, other in (("verify-a", proposals[0], ids[1]), ("verify-b", proposals[1], ids[0]))}
            result = self.concurrent(operations, patch.object(self.recommendations.catalog, "guard_case", side_effect=guard))
        finally:
            event.remove(self.engine, "before_cursor_execute", trace)
        self.assertEqual(orders, {"verify-a": ids, "verify-b": ids})
        self.assertTrue(all(row.follow_up_status == "VERIFIED" for row in result.values()))
        for row in result.values():
            self.assertEqual(len(self.recommendations.history(self.directory("author"), row.record_id)), row.revision)

    def concurrent(self, operations, hook):
        """Bounded synchronized real commands; cleanup cancels only own sessions."""
        outcomes, errors, pids = {}, [], set()
        def trace(connection, cursor, statement, parameters, context, many):
            if "FOR UPDATE" in statement:
                pids.add(connection.connection.driver_connection.info.backend_pid)
        def db_error(context):
            errors.append(getattr(context.original_exception, "sqlstate", None))
        def worker(name, operation):
            try:
                outcomes[name] = operation()
            except BaseException as error:
                outcomes[name] = error
        threads = [threading.Thread(target=worker, name=name, args=(name, operation), daemon=True)
            for name, operation in operations.items()]
        event.listen(self.engine, "before_cursor_execute", trace)
        event.listen(self.engine, "handle_error", db_error)
        # Synthetic Mart uses SQLite StaticPool (one connection). Serialize its
        # short independent reads, not the actual PostgreSQL command sessions.
        mart_read = self.mart.read_session
        mart_lock = threading.RLock()
        @contextmanager
        def serialized_mart_read():
            with mart_lock, mart_read() as session:
                yield session
        try:
            with hook, patch.object(self.mart, "read_session", serialized_mart_read):
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(12)
                if any(thread.is_alive() for thread in threads):
                    with self.engine.begin() as c:
                        for pid in pids:
                            c.execute(text("SELECT pg_cancel_backend(pid) FROM pg_stat_activity "
                                "WHERE pid=:pid AND datname=current_database()"), dict(pid=pid))
                    for thread in threads:
                        thread.join(3)
                self.assertFalse(any(thread.is_alive() for thread in threads), "workers did not stop")
            self.assertNotIn("40P01", errors)
            for outcome in outcomes.values():
                if isinstance(outcome, BaseException):
                    raise outcome
            self.assertEqual(len(outcomes), len(operations))
            return outcomes
        finally:
            event.remove(self.engine, "before_cursor_execute", trace)
            event.remove(self.engine, "handle_error", db_error)

    def test_submit_and_review_shared_case_inspection_use_same_first_lock(self):
        inspection = self.approved_inspection()
        case = self.approved_case(inspection)
        a = self.proposal(kind="MANUAL_INSPECTION", record=inspection["record_id"], key="a", case=case)
        b = self.proposal(kind="MANUAL_INSPECTION", record=inspection["record_id"], key="b", case=case)
        b = self.change(b, "SUBMIT")
        # REVIEW holds Case at rendezvous; SUBMIT is about to take Case. Old
        # SUBMIT already holds Inspection here, deterministically making 40P01.
        barrier = threading.Barrier(2, timeout=6)
        original = self.recommendations.catalog.guard_case
        def guard(*args, **kwargs):
            if threading.current_thread().name == "submit":
                barrier.wait()
                return original(*args, **kwargs)
            result = original(*args, **kwargs)
            barrier.wait()
            return result
        result = self.concurrent(dict(submit=lambda: self.change(a, "SUBMIT"),
            review=lambda: self.change(b, "REVIEW", dict(decision="APPROVED", reason="Independent"), reviewer=True)),
            patch.object(self.recommendations.catalog, "guard_case", side_effect=guard))
        self.assertEqual(result["submit"].status, "IN_REVIEW")
        self.assertEqual(result["review"].status, "APPROVED")
        for row in result.values():
            self.assertEqual(len(self.recommendations.history(self.directory("author"), row.record_id)), row.revision)
