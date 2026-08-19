"""Registry loader: parse verified parameter mappings from pi-knowledge YAML.

The pi-knowledge repository is the source of truth for which PI attributes to
collect. This module reads its mappings YAML and produces AttributeRegistration
domain objects with stable attribute IDs.

Expected YAML format (from pi-knowledge/mappings/bsr1-parameters.yaml):
    site: BSR
    unit: BSR1
    source: pi
    status: verified
    equipment:
      BSR1.Turbine:
        parameter_count: 48
        parameters:
          bearing_temperature:
          - name: Bearing 1 Left Temperature
            unit: degC
            position: ''
            web_id: F1Ab...
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from src.domain.models import AttributeRegistration

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slug(text: str) -> str:
    """Lowercase slug: non-alphanumeric → underscore, collapse repeats."""
    return _NON_ALNUM.sub("_", text.lower()).strip("_")


def _build_attribute_id(site: str, unit: str, equipment: str, parameter: str, name: str, position: str) -> str:
    """Deterministic, human-readable, URL-safe attribute ID."""
    parts = [site, unit, _slug(equipment), parameter, _slug(name)]
    if position:
        parts.append(_slug(position))
    return "-".join(p for p in parts if p)


def load_registry(yaml_path: str | Path) -> list[AttributeRegistration]:
    """Load verified PI attributes from a pi-knowledge mapping YAML file.

    An entry is included only when ALL of these hold:
      * it has a non-empty ``web_id``
      * its ``status`` is ``verified`` (entries marked ``broken`` — PI Point
        deleted — are skipped; they would return HTTP 410 on every request)
      * if ``stream_status`` is present, it equals ``ok``
    """
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"registry YAML not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not data or "equipment" not in data:
        return []

    site = data.get("site", "")
    unit = data.get("unit", "")
    registrations: list[AttributeRegistration] = []

    for eq_name, eq_data in (data.get("equipment") or {}).items():
        parameters = eq_data.get("parameters") or {}
        for param_category, entries in parameters.items():
            for entry in entries:
                web_id = entry.get("web_id", "")
                if not web_id:
                    continue  # skip entries without verified WebId
                entry_status = entry.get("status", "verified")
                if entry_status != "verified":
                    continue  # skip broken/deprecated/unknown entries
                stream_status = entry.get("stream_status", "ok")
                if stream_status != "ok":
                    continue  # stream verified broken (410 Gone)
                name = entry.get("name", "")
                position = entry.get("position", "") or ""
                reg = AttributeRegistration(
                    attribute_id=_build_attribute_id(site, unit, eq_name, param_category, name, position),
                    site=site,
                    unit=unit,
                    equipment=eq_name,
                    parameter=param_category,
                    business_name=name,
                    position=position or None,
                    unit_of_measure=entry.get("unit"),
                    web_id=web_id,
                    af_path=f"{site} > {unit} > {eq_name} > {name}",
                )
                registrations.append(reg)

    return registrations
