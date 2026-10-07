"""Canonical local-evidence integration status, never an equipment health score."""
from datetime import datetime
from enum import StrEnum
from pydantic import Field
from src.domain.condition_evidence import EvidenceModel

class Component(StrEnum):
    MAXIMO = "MAXIMO"
    PI_COLLECTOR = "PI_COLLECTOR"
    RELIABILITY_MART = "RELIABILITY_MART"
    ASSET_AF_MAPPING = "ASSET_AF_MAPPING"
    PI_CONDITION_PROJECTION = "PI_CONDITION_PROJECTION"

class TrustState(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    BLOCKED = "BLOCKED"
    DEGRADED = "DEGRADED"
    NOT_CONFIGURED = "NOT_CONFIGURED"

class Availability(StrEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    NOT_CONFIGURED = "NOT_CONFIGURED"

class MappingReadiness(StrEnum):
    VERIFIED = "VERIFIED"
    UNMAPPED = "UNMAPPED"
    AMBIGUOUS = "AMBIGUOUS"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"

class Quality(StrEnum):
    GOOD = "GOOD"
    BAD = "BAD"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"

class DegradedReason(StrEnum):
    HUMAN_CROSSWALK_REQUIRED = "HUMAN_CROSSWALK_REQUIRED"
    AMBIGUOUS_MAPPING = "AMBIGUOUS_MAPPING"
    PARTIAL_MAPPING_COVERAGE = "PARTIAL_MAPPING_COVERAGE"
    COLLECTOR_UNAVAILABLE = "COLLECTOR_UNAVAILABLE"
    COLLECTOR_OBSERVATION_UNAVAILABLE = "COLLECTOR_OBSERVATION_UNAVAILABLE"
    COLLECTOR_ERRORS = "COLLECTOR_ERRORS"
    CURSOR_MISSING = "CURSOR_MISSING"
    NO_SUCCESSFUL_ACTIVITY = "NO_SUCCESSFUL_ACTIVITY"
    MART_UNAVAILABLE = "MART_UNAVAILABLE"
    MART_NOT_CONFIGURED = "MART_NOT_CONFIGURED"
    GOVERNANCE_SCHEMA_NOT_READY = "GOVERNANCE_SCHEMA_NOT_READY"
    CONDITION_SCHEMA_NOT_READY = "CONDITION_SCHEMA_NOT_READY"
    NO_APPROVED_SIGNALS = "NO_APPROVED_SIGNALS"
    NO_PROJECTED_EVIDENCE = "NO_PROJECTED_EVIDENCE"
    PARTIAL_SIGNAL_SET = "PARTIAL_SIGNAL_SET"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_STALE = "SOURCE_STALE"
    COLLECTION_STALE = "COLLECTION_STALE"
    PROJECTION_STALE = "PROJECTION_STALE"
    PROJECTION_ERROR = "PROJECTION_ERROR"
    BAD_QUALITY = "BAD_QUALITY"
    UNKNOWN_QUALITY = "UNKNOWN_QUALITY"
    UNKNOWN_FRESHNESS_POLICY = "UNKNOWN_FRESHNESS_POLICY"
    UNKNOWN_TIMESTAMP = "UNKNOWN_TIMESTAMP"

class FreshnessDimension(EvidenceModel):
    state: TrustState = TrustState.UNKNOWN
    observed_at: datetime | None = None
    max_age_seconds: float | None = Field(default=None, gt=0)

class CoverageSummary(EvidenceModel):
    registered_assets: int | None = Field(default=None, ge=0)
    verified_mapping_assets: int | None = Field(default=None, ge=0)
    ambiguous_mapping_assets: int | None = Field(default=None, ge=0)
    approved_signal_assets: int | None = Field(default=None, ge=0)
    projected_assets: int | None = Field(default=None, ge=0)
    approved_signals: int | None = Field(default=None, ge=0)
    projected_signals: int | None = Field(default=None, ge=0)
    technical_registry_total: int | None = Field(default=None, ge=0)
    technical_registry_active: int | None = Field(default=None, ge=0)
    technical_snapshots: int | None = Field(default=None, ge=0)

class CollectorObservation(EvidenceModel):
    availability: Availability = Availability.UNKNOWN
    last_successful_activity: datetime | None = None
    latest_completed_at: datetime | None = None
    cursor_present: bool | None = None
    errors: int | None = Field(default=None, ge=0)
    registry_total: int | None = Field(default=None, ge=0)
    registry_active: int | None = Field(default=None, ge=0)
    snapshots: int | None = Field(default=None, ge=0)
    oldest_source_timestamp: datetime | None = None
    unknown_source_timestamps: int | None = Field(default=None, ge=0)
    future_source_timestamps: int | None = Field(default=None, ge=0)
    bad_quality_signals: int | None = Field(default=None, ge=0)
    unknown_quality_signals: int | None = Field(default=None, ge=0)

class IntegrationComponentStatus(EvidenceModel):
    component: Component
    state: TrustState
    availability: Availability
    collection_freshness: FreshnessDimension = Field(default_factory=FreshnessDimension)
    source_freshness: FreshnessDimension = Field(default_factory=FreshnessDimension)
    projection_freshness: FreshnessDimension = Field(default_factory=FreshnessDimension)
    mapping_readiness: MappingReadiness = MappingReadiness.UNKNOWN
    quality: Quality = Quality.UNKNOWN
    last_successful_activity: datetime | None = None
    degraded_reasons: tuple[DegradedReason, ...] = ()

class IntegrationStatus(EvidenceModel):
    contract_version: str = "1.0"
    observed_at: datetime
    canonical_asset_id: str | None = None
    governance_schema_ready: bool | None = None
    condition_schema_ready: bool | None = None
    coverage: CoverageSummary = Field(default_factory=CoverageSummary)
    components: tuple[IntegrationComponentStatus, ...]
