"""Injected local SELECT/read services only; disabled by default, no source client."""
from datetime import datetime, timezone
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from src.domain.asset_context import (AssetIdentityContext, AssetSourceIdentity,
    ContextAvailability as Availability, ContextPage, UnifiedAssetContext)
from src.domain.condition_evidence import FreshnessPolicy
from src.domain.engineering import Principal, CaseStatus, EngineeringError
from src.repositories.mart_reader import MartQueryRepository
from src.services.condition_query import ConditionQueryService
from src.services.engineering_evidence import aware
from src.services.maximo_intelligence import LocalMaintenanceIntelligence

def collected_at(provenance):
    raw = (provenance or {}).get("ingested_at")
    if not isinstance(raw, str):
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return value if value.tzinfo is not None else None
    except ValueError:
        return None

class AssetContextService:
    def __init__(self, mart_database, *, cases=None, inspections=None,
                 recommendations=None, policy=None, clock=None, enabled=False):
        self.enabled = enabled
        self.assets = MartQueryRepository(mart_database)
        self.maintenance = LocalMaintenanceIntelligence(mart_database)
        self.policy = policy or FreshnessPolicy()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.conditions = ConditionQueryService(mart_database, policy=self.policy, clock=self.clock)
        self.cases, self.inspections, self.recommendations = cases, inspections, recommendations

    def gate(self, actor, asset):
        if not self.enabled:
            raise EngineeringError("FEATURE_DISABLED", 404)
        if not isinstance(actor, Principal) or not actor.roles or len(actor.asset_ids) > 1000:
            raise EngineeringError("AUTHENTICATION_REQUIRED", 401)
        if asset not in actor.asset_ids:
            raise EngineeringError("NOT_FOUND", 404)

    def page(self, operation, *, offset, limit):
        if operation is None:
            return ContextPage(availability=Availability.NOT_CONFIGURED, offset=offset, limit=limit)
        try:
            result = operation()
            return ContextPage(availability=Availability.AVAILABLE if result["items"] else Availability.EMPTY,
                items=tuple(result["items"]), total=result.get("total"), offset=offset,
                limit=limit, has_more=result["has_more"])
        except EngineeringError as error:
            if error.status != 503:
                raise
        except SQLAlchemyError:
            pass
        except (ValidationError, ValueError, TypeError, KeyError):
            return ContextPage(availability=Availability.INVALID_RECORD, offset=offset, limit=limit)
        return ContextPage(availability=Availability.UNAVAILABLE, offset=offset, limit=limit)

    def read(self, actor, asset, *, offset=0, limit=25):
        self.gate(actor, asset)
        if type(offset) is not int or type(limit) is not int or not 0 <= offset <= 10000 or not 1 <= limit <= 100:
            raise EngineeringError("INVALID_PAGINATION", 422)
        now = self.clock()
        identity = None
        identity_state = Availability.AVAILABLE
        try:
            row = self.assets.get_asset(asset)
            if row is None:
                raise EngineeringError("NOT_FOUND", 404)
            identity = AssetIdentityContext(canonical_asset_id=asset, description=row.description,
                location_ref=row.location_ref, parent_asset_ref=row.parent_asset_ref,
                equipment_type=row.asset_type, unit_ref=row.unit,
                source_identity=AssetSourceIdentity(record_ref=row.source_asset_number),
                source_timestamp=aware(row.source_updated_at), collected_at=collected_at(row.provenance),
                projected_at=aware(row.mart_updated_at),
                projection_freshness=self.policy.state("PROJECTION", aware(row.mart_updated_at), now,
                    component="RELIABILITY_MART").removeprefix("PROJECTION_"))
        except SQLAlchemyError:
            identity_state = Availability.UNAVAILABLE
        except (ValidationError, ValueError, TypeError):
            identity_state = Availability.INVALID_RECORD
        maintenance = self.page(lambda: self.maintenance.work_orders(actor, asset, offset=offset, limit=limit, sort="chronology_desc"), offset=offset, limit=limit)
        condition = None
        condition_state = Availability.UNAVAILABLE
        try:
            condition = self.conditions.asset_evidence(asset)
            condition_state = Availability.AVAILABLE if condition is not None else Availability.EMPTY
            if condition and "PROJECTION_ERROR" in condition.statuses:
                condition_state = Availability.UNAVAILABLE
        except SQLAlchemyError:
            pass
        pages = {}
        for name in ("cases", "inspections", "recommendations"):
            service = getattr(self, name)
            pages[name] = self.page(
                (lambda service=service: service.list(actor, asset_id=asset, offset=offset, limit=limit)) if service else None,
                offset=offset, limit=limit)
        return UnifiedAssetContext(canonical_asset_id=asset, read_at=now,
            identity=identity, identity_availability=identity_state, maintenance=maintenance,
            condition=condition, condition_availability=condition_state, **pages,
            reviewed_inspections=tuple(r for r in pages["inspections"].items if r.status == CaseStatus.APPROVED))
