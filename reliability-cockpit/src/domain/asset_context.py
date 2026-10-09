"""Bounded local context; human review is not equipment-health assessment."""
from datetime import datetime
from enum import StrEnum
from typing import Generic, Literal, TypeVar
from pydantic import Field, StrictStr
from src.domain.condition_evidence import EvidenceModel
from src.domain.engineering import EngineeringCase
from src.domain.manual_inspection import ManualInspection
from src.domain.recommendation import Recommendation
from src.domain.maintenance_context import ExistingWorkOrderReference
from src.services.condition_query import AssetConditionEvidence

class ContextAvailability(StrEnum):
    AVAILABLE = "AVAILABLE"
    EMPTY = "EMPTY"
    UNAVAILABLE = "UNAVAILABLE"
    INVALID_RECORD = "INVALID_RECORD"
    NOT_CONFIGURED = "NOT_CONFIGURED"

class AssetSourceIdentity(EvidenceModel):
    system: Literal["MAXIMO"] = "MAXIMO"
    record_ref: StrictStr | None = None
    site: Literal["BSR"] = "BSR"
    organization: Literal["IP"] = "IP"

class AssetIdentityContext(EvidenceModel):
    canonical_asset_id: StrictStr
    description: StrictStr | None = None
    location_ref: StrictStr | None = None
    parent_asset_ref: StrictStr | None = None
    equipment_type: StrictStr | None = None
    classification_ref: StrictStr | None = None
    unit_ref: StrictStr | None = None
    source_identity: AssetSourceIdentity
    source_timestamp: datetime | None = None
    collected_at: datetime | None = None
    projected_at: datetime | None = None
    source_freshness: Literal["UNKNOWN"] = "UNKNOWN"
    projection_freshness: Literal["CURRENT", "STALE", "UNKNOWN"] = "UNKNOWN"
    source_quality: Literal["UNKNOWN"] = "UNKNOWN"
    provenance: Literal["CANONICAL_MART_SOURCE_FACT"] = "CANONICAL_MART_SOURCE_FACT"
    identity_basis: Literal["REGISTERED_CANONICAL_ASSET"] = "REGISTERED_CANONICAL_ASSET"

T = TypeVar("T")
class ContextPage(EvidenceModel, Generic[T]):
    availability: ContextAvailability
    items: tuple[T, ...] = Field(default=(), max_length=100)
    total: int | None = Field(default=None, ge=0)
    offset: int = Field(default=0, ge=0, le=10000)
    limit: int = Field(default=25, ge=1, le=100)
    has_more: bool | None = None

class UnifiedAssetContext(EvidenceModel):
    contract_version: Literal["1.0"] = "1.0"
    canonical_asset_id: StrictStr
    read_at: datetime
    consistency: Literal["BOUNDED_LOCAL_READS"] = "BOUNDED_LOCAL_READS"
    identity: AssetIdentityContext | None = None
    identity_availability: ContextAvailability
    maintenance: ContextPage[ExistingWorkOrderReference]
    condition: AssetConditionEvidence | None = None
    condition_availability: ContextAvailability
    cases: ContextPage[EngineeringCase]
    inspections: ContextPage[ManualInspection]
    recommendations: ContextPage[Recommendation]
    reviewed_inspections: tuple[ManualInspection, ...] = Field(default=(), max_length=100)
    assessment: Literal["NOT_ASSESSED"] = "NOT_ASSESSED"
    review_scope: Literal["HUMAN_RECORD_REVIEW_NOT_SOURCE_VERIFICATION"] = "HUMAN_RECORD_REVIEW_NOT_SOURCE_VERIFICATION"
