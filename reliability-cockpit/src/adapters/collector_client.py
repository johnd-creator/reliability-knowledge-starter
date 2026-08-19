"""HTTP client for the maximo-collector API (the cockpit's data source).

The cockpit is a pure dashboard: it never talks to Maximo. It pulls
contract-shaped views from the collector and rebuilds its own domain models.
Field names match reliability-data-contracts on both sides, so conversion is
mechanical (parse ISO datetimes, rebuild the quarantined sources block).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Mapping

import requests

from src.domain.equipment import Equipment, MaximoEquipmentSource
from src.domain.item import Item
from src.domain.labor import Labor
from src.domain.person import Person
from src.domain.service_request import ServiceRequest
from src.domain.work_order import WorkOrder


class CollectorClientError(RuntimeError):
    """Collector API unreachable or returned an unexpected payload."""


def _dt(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _build(model_cls: type, view: Mapping[str, Any], *, datetime_fields: tuple[str, ...]):
    kwargs: dict[str, Any] = {}
    for f in getattr(model_cls, "__dataclass_fields__", {}).values():
        if f.name not in view:
            continue
        value = view[f.name]
        if f.name in datetime_fields:
            value = _dt(value)
        kwargs[f.name] = value
    return model_cls(**kwargs)


def equipment_from_view(view: Mapping[str, Any]) -> Equipment:
    # Map collector assetnum → cockpit id
    view = dict(view)
    if "id" not in view and "assetnum" in view:
        view["id"] = view.pop("assetnum")
    equipment = _build(
        Equipment,
        {k: v for k, v in view.items() if k != "sources"},
        datetime_fields=(
            "installed_at", "status_changed_at", "source_changed_at",
        ),
    )
    sources = view.get("sources") or {}
    maximo = sources.get("maximo")
    if isinstance(maximo, Mapping):
        maximo = dict(maximo)
        for key in ("installdate", "changedate"):
            if key in maximo:
                maximo[key] = _dt(maximo[key])
        equipment.maximo_source = MaximoEquipmentSource(**maximo)
    return equipment


def work_order_from_view(view: Mapping[str, Any]) -> WorkOrder:
    # Map collector worktype → cockpit work_type
    view = dict(view)
    if "id" not in view and "wonum" in view:
        view["id"] = view.pop("wonum")
    if "work_type" not in view and "worktype" in view:
        view["work_type"] = view.pop("worktype")
    return _build(
        WorkOrder,
        dict(view),
        datetime_fields=(
            "reported_at", "source_changed_at", "status_changed_at",
            "scheduled_start", "scheduled_finish", "target_completion",
        ),
    )


def service_request_from_view(view: Mapping[str, Any]) -> ServiceRequest:
    return _build(
        ServiceRequest,
        dict(view),
        datetime_fields=(
            "reported_at", "source_changed_at", "affected_at",
            "actual_start", "actual_finish", "target_start", "target_finish",
            "status_changed_at",
        ),
    )


def person_from_view(view: Mapping[str, Any]) -> Person:
    return _build(Person, dict(view), datetime_fields=("status_changed_at",))


def item_from_view(view: Mapping[str, Any]) -> Item:
    return _build(Item, dict(view), datetime_fields=("status_changed_at",))


def labor_from_view(view: Mapping[str, Any]) -> Labor:
    return _build(Labor, dict(view), datetime_fields=())


# resource -> (endpoint, view->domain builder, watermark column)
RESOURCES: dict[str, tuple[str, Callable[[Mapping], Any], bool]] = {
    "equipment": ("/equipment", equipment_from_view, True),
    "workorder": ("/work-orders", work_order_from_view, True),
    "servicerequest": ("/service-requests", service_request_from_view, True),
    "person": ("/persons", person_from_view, True),
    "item": ("/items", item_from_view, True),
    "labor": ("/labor", labor_from_view, False),  # no watermark by design
}


class CollectorClient:
    """Read-only HTTP client for the maximo-collector API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8002", timeout_seconds: int = 60):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def pull(self, resource: str, *, changed_since: datetime | None = None, limit: int = 1000) -> list:
        """Pull one resource's rows as cockpit domain models."""
        if resource not in RESOURCES:
            raise CollectorClientError(f"unknown resource: {resource}")
        endpoint, builder, has_watermark = RESOURCES[resource]
        params: dict[str, Any] = {"limit": limit}
        if has_watermark and changed_since is not None:
            params["changed_since"] = changed_since.isoformat()
        try:
            resp = requests.get(self._base_url + endpoint, params=params, timeout=self._timeout)
            resp.raise_for_status()
            payload = resp.json()
        except requests.RequestException as error:
            raise CollectorClientError(
                f"collector API {endpoint} failed (is mxcollector serve running on "
                f"{self._base_url}?): {error}"
            ) from error
        except ValueError as error:
            raise CollectorClientError(f"collector API {endpoint} returned non-JSON: {error}") from error
        if not isinstance(payload, list):
            raise CollectorClientError(f"collector API {endpoint} returned {type(payload).__name__}, expected list")
        return [builder(view) for view in payload]

    def health(self) -> bool:
        try:
            resp = requests.get(self._base_url + "/health", timeout=self._timeout)
            return resp.status_code == 200
        except requests.RequestException:
            return False
