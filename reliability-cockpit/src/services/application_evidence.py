"""Local adapters only. Case links retain asset authorization; no source clients."""

from src.domain.engineering import EngineeringError, EngineeringCase
from sqlalchemy import select
from src.repositories.engineering import CaseRow


class ApplicationEvidenceCatalog:
    def __init__(self, canonical_catalog, case_service):
        self.canonical = canonical_catalog
        self.cases = case_service

    def registered(self, asset):
        return self.canonical.registered(asset)

    def validate_case(self, actor, asset, case_ref):
        case = self.cases.get(actor, case_ref)
        if case.canonical_asset_id != asset:
            raise EngineeringError("CASE_ASSET_MISMATCH", 422)
        return case

    def resolve(self, *args):
        return self.canonical.resolve(*args)

    def guard_case(self, connection, actor, asset, case_ref):
        if connection.engine is not self.cases.repo.engine:
            raise EngineeringError("APPLICATION_STORE_IDENTITY_MISMATCH", 503)
        raw = connection.scalar(select(CaseRow.document).where(CaseRow.case_id == case_ref).with_for_update())
        case = self.cases.visible(actor, EngineeringCase.model_validate(raw) if raw else None)
        if case.canonical_asset_id != asset:
            raise EngineeringError("CASE_ASSET_MISMATCH", 422)
        return case

    def guard_evidence(self, connection, actor, asset, refs):
        if hasattr(self.canonical, "guard_evidence"):
            self.canonical.guard_evidence(connection, actor, asset, refs)
