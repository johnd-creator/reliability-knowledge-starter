"""Vendor-neutral, informational local maintenance references; never WO commands."""
from datetime import datetime
from typing import Literal
from pydantic import Field, StrictStr
from src.domain.condition_evidence import EvidenceModel

class MaximoWorkOrderIdentity(EvidenceModel):
    source_object: Literal["MXWODETAIL"] = "MXWODETAIL"
    source_record_ref: StrictStr = Field(min_length=1,max_length=200)
    site: Literal["BSR"] = "BSR"
    organization: Literal["IP"] = "IP"

class MaintenanceSources(EvidenceModel):
    maximo: MaximoWorkOrderIdentity

class ExistingWorkOrderReference(EvidenceModel):
    canonical_asset_id: StrictStr = Field(min_length=1,max_length=200)
    canonical_record_id: StrictStr = Field(min_length=1,max_length=200)
    record_status: StrictStr | None = Field(default=None,max_length=80)
    work_type: StrictStr | None = Field(default=None,max_length=80)
    source_changed_at: datetime | None = None
    collected_at: datetime | None = None
    projected_at: datetime | None = None
    sources: MaintenanceSources
    informational_only: Literal[True] = True
    interpretation: Literal["SOURCE_FACT"] = "SOURCE_FACT"
    freshness: Literal["UNKNOWN"] = "UNKNOWN"
