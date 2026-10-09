"""Local reviewed recommendation closure; source records remain informational."""
from unittest.mock import patch
from pydantic import ValidationError
from test_recommendation import RecommendationTest, Catalog
from src.domain.engineering import EngineeringError


class RecommendationWorkflowTest(RecommendationTest):
    def test_unreviewed_case_blocks_submission(self):
        row = self.create()
        case = self.catalog.validate_case(self.author, row.canonical_asset_id, row.case_ref)
        case = case.model_copy(update={"status": "DRAFT", "review": None})
        with patch.object(self.catalog, "validate_case", return_value=case):
            self.code("REVIEWED_CASE_REQUIRED", lambda: self.change(row, "SUBMIT", {}))
        self.assertEqual(self.service.get(self.author, row.record_id), row)

    def test_case_version_change_blocks_review_and_followup(self):
        submitted = self.change(self.create(), "SUBMIT", {})
        case = self.catalog.validate_case(self.author, submitted.canonical_asset_id, submitted.case_ref)
        with patch.object(self.catalog, "validate_case", return_value=case.model_copy(update={"revision": 4})):
            self.code("REVIEWED_CASE_CHANGED", lambda: self.change(submitted, "REVIEW", {"decision": "APPROVED", "reason": "x"}, self.reviewer))
        row = self.change(submitted, "REVIEW", {"decision": "APPROVED", "reason": "Checked"}, self.reviewer)
        with patch.object(self.catalog, "validate_case", return_value=case.model_copy(update={"revision": 4})):
            self.code("REVIEWED_CASE_CHANGED", lambda: self.change(row, "FOLLOWUP", {"status": "PLANNED", "reason": "x"}))

    def test_supporting_evidence_required(self):
        self.draft["evidence_selections"] = []
        row = self.create()
        self.code("SUPPORTING_EVIDENCE_REQUIRED", lambda: self.change(row, "SUBMIT", {}))

    def complete(self):
        row = self.approved()
        for status in ("PLANNED", "IN_PROGRESS", "COMPLETED"):
            row = self.change(row, "FOLLOWUP", {"status": status, "reason": "Local follow-up"}, request=status)
        return row

    def test_completion_independent_evidence_and_replay(self):
        row = self.complete()
        original_wo = row.existing_work_order.model_dump()
        payload = {"reason": "Local completion record checked, no WO action",
                   "evidence_selections": self.draft["evidence_selections"]}
        self.code("INDEPENDENT_REVIEWER_REQUIRED", lambda: self.change(row, "VERIFY_COMPLETION", payload))
        done = self.change(row, "VERIFY_COMPLETION", payload, self.reviewer, request="verify")
        replay = self.change(row, "VERIFY_COMPLETION", payload, self.reviewer, request="verify")
        self.assertEqual(done, replay)
        self.assertEqual(done.follow_up_status, "VERIFIED")
        self.assertEqual(done.completion_verification.evidence[0].mode, "FROZEN_SNAPSHOT")
        self.assertEqual(done.existing_work_order.model_dump(), original_wo)
        self.assertEqual(len(self.service.history(self.author, row.record_id)), 7)
        self.code("INVALID_TRANSITION", lambda: self.change(done, "VERIFY_COMPLETION", payload, self.reviewer, "twice"))

    def test_empty_duplicate_live_or_foreign_completion_denied(self):
        row = self.complete()
        for selected in ([], self.draft["evidence_selections"] * 2,
                         [dict(kind="ASSET", record_id=row.canonical_asset_id, mode="LIVE_REFERENCE")]):
            self.code("COMPLETION_EVIDENCE_REQUIRED", lambda: self.change(row, "VERIFY_COMPLETION",
                {"reason": "x", "evidence_selections": selected}, self.reviewer, "bad"))
        self.code("EVIDENCE_NOT_FOUND", lambda: self.change(row, "VERIFY_COMPLETION",
            {"reason": "x", "evidence_selections": [dict(kind="ASSET", record_id="asset:FOREIGN")]}, self.reviewer, "foreign"))

    def test_changed_evidence_does_not_rewrite_accepted_snapshot(self):
        row = self.change(self.create(), "SUBMIT", {})
        ref = row.supporting_evidence[0]
        with patch.object(self.catalog, "resolve", return_value=ref.model_copy(update={
            "stable_version": "changed", "linked_by": "reviewer", "linked_at": self.now.replace(second=self.now.second + 1)})):
            self.code("EVIDENCE_VERSION_CHANGED", lambda: self.change(row, "REVIEW", {"decision": "APPROVED", "reason": "x"}, self.reviewer))
        self.assertEqual(self.service.get(self.author, row.record_id), row)
