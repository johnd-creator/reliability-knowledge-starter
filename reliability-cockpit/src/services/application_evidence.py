"""Local adapters only. Case links retain asset authorization; no source clients."""
from src.domain.engineering import EngineeringError

class ApplicationEvidenceCatalog:
    def __init__(self, canonical_catalog, case_service):
        self.canonical = canonical_catalog
        self.cases = case_service
    def registered(self, asset):return self.canonical.registered(asset)
    def validate_case(self, actor, asset, case_ref):
        case = self.cases.get(actor,case_ref)
        if case.canonical_asset_id != asset:raise EngineeringError("CASE_ASSET_MISMATCH",422)
        return case
    def resolve(self, *args):return self.canonical.resolve(*args)
