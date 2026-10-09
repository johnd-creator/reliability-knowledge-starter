"""Reviewed human observations; never a source fact or health assessment."""
from datetime import datetime
from typing import Annotated, Literal
from pydantic import Field, StrictStr, StrictInt, model_validator
from src.domain.condition_evidence import EvidenceModel
from src.domain.text import NONBLANK_TEXT_PATTERN
from src.domain.inspection_measurement import ManualMeasurement

TextItem = Annotated[StrictStr,Field(min_length=1,max_length=2000,pattern=NONBLANK_TEXT_PATTERN)]
class ReviewedInspectionEvidence(EvidenceModel):
    canonical_asset_id: StrictStr
    record_id: StrictStr
    revision: StrictInt = Field(ge=1)
    stable_version: StrictStr = Field(pattern=r'^[0-9a-f]{64}$')
    inspector_ref: StrictStr
    inspected_at: datetime | None = None
    method: StrictStr
    method_version: StrictStr
    measurements: tuple[ManualMeasurement,...] = Field(default=(),max_length=100)
    observations: tuple[TextItem,...] = Field(default=(),max_length=20)
    interpretations: tuple[TextItem,...] = Field(default=(),max_length=20)
    reviewer: StrictStr
    reviewed_at: datetime
    decision: Literal['APPROVED'] = 'APPROVED'
    interpretation: Literal['REVIEWED_HUMAN_EVIDENCE'] = 'REVIEWED_HUMAN_EVIDENCE'
    assessment: Literal['NOT_ASSESSED'] = 'NOT_ASSESSED'
    @model_validator(mode='after')
    def independent(self):
        if self.reviewer == self.inspector_ref:
            raise ValueError('independent reviewer required')
        return self
