"""Synthetic QA advisory contracts; never source/maintenance authorization."""
from datetime import datetime
from typing import Literal
from pydantic import Field, StrictStr, model_validator
from src.domain.condition_evidence import EvidenceModel
from src.domain.human_records import HumanRecord

Audience = Literal['OPERATIONS_QA', 'MAINTENANCE_QA', 'ENGINEERING_QA']

class AdvisoryDraft(EvidenceModel):
    canonical_asset_id: StrictStr = Field(min_length=1, max_length=200)
    recommendation_ref: StrictStr = Field(min_length=1, max_length=100)
    summary: StrictStr = Field(min_length=1, max_length=200)
    finding: StrictStr = Field(min_length=1, max_length=6000)
    evidence_caveat: StrictStr = Field(min_length=1, max_length=6000)
    audiences: tuple[Audience, ...] = Field(min_length=1, max_length=3)
    replaces: StrictStr | None = Field(default=None, max_length=100)

    @model_validator(mode='after')
    def meaningful(self):
        if any(not x.strip() for x in (self.summary, self.finding, self.evidence_caveat)) or len(set(self.audiences)) != len(self.audiences):
            raise ValueError('nonblank text and unique audiences required')
        return self

class Advisory(HumanRecord, AdvisoryDraft):
    upstream: dict
    publication: dict | None = None
    availability: Literal['UNPUBLISHED', 'IN_APP_QA_AVAILABLE', 'WITHDRAWN'] = 'UNPUBLISHED'
    scope: Literal['SYNTHETIC_QA_ONLY_NOT_WORK_AUTHORIZATION'] = 'SYNTHETIC_QA_ONLY_NOT_WORK_AUTHORIZATION'

    @model_validator(mode='after')
    def immutable_publication(self):
        if self.publication is not None and self.status != 'APPROVED':
            raise ValueError('published review cannot be reopened')
        if (self.availability == 'UNPUBLISHED') != (self.publication is None):
            raise ValueError('publication availability mismatch')
        if self.review and self.review.reviewer in self.upstream['excluded_reviewers']:
            raise ValueError('upstream contributor cannot review advisory')
        return self

class Acknowledgement(EvidenceModel):
    record_id: str
    revision: Literal[1] = 1
    advisory_id: str
    publication_version: int
    canonical_asset_id: str
    actor: str
    updated_at: datetime
    status: Literal['ACKNOWLEDGED'] = 'ACKNOWLEDGED'
    meaning: Literal['RECEIPT_ONLY_NOT_APPROVAL_OR_WORK_AUTHORIZATION'] = 'RECEIPT_ONLY_NOT_APPROVAL_OR_WORK_AUTHORIZATION'
