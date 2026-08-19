#!/usr/bin/env python3
"""Build a clean Maximo object-structure catalog from a captured OAS document.

The Maximo OAS exposes every Object Structure as ``/os/{name}`` but uses shared
``$ref`` parameters and tags rather than inline schemas, so the field list is
empty. This script resolves the shared OSLC query parameters (to confirm
capabilities) and extracts readable names/tags so the catalog is useful even
before per-structure field sampling.

Usage:
    python scripts/build_catalog.py --oas-file discovery/oslc/maximo_oas.json \\
        --output-dir discovery/oslc
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

RESOURCE_RULES: list[tuple[str, list[str]]] = [
    ("asset", ["asset"]),
    ("workorder", ["work order", "workorder", "wodetail", "worklog", "workzone"]),
    ("location", ["location"]),
    ("preventivemaintenance", ["preventive", "pm "]),
    ("failurecode", ["failure"]),
    ("meter", ["meter"]),
    ("labor", ["labor", "craft"]),
    ("materials", ["item", "inventor", "invuse", "material", "stock", "tool"]),
    ("jobplan", ["job plan", "jobplan"]),
    ("sr", ["service request", "servicerequest", "sr "]),
    ("person", ["person"]),
]


def load_oas(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"OAS file is not valid JSON: {exc}") from exc
    if isinstance(doc, str):
        doc = json.loads(doc)
    if not isinstance(doc, dict) or not doc.get("openapi"):
        raise SystemExit("OAS document is missing the 'openapi' field")
    return doc


def parse_tag(tag: str) -> tuple[str, str]:
    if not tag:
        return "", ""
    match = re.match(r"^(.*?)\s*\(([A-Z0-9_]+)\)\s*$", tag.strip())
    if match:
        return match.group(1).strip(), match.group(2)
    return tag.strip(), ""


def map_resource(text: str) -> str:
    lowered = text.lower()
    for resource, keywords in RESOURCE_RULES:
        if any(keyword in lowered for keyword in keywords):
            return resource
    return "other"


def shared_param_names(path_item: dict[str, Any], shared: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for method in ("get", "post"):
        operation = path_item.get(method) or {}
        for param in operation.get("parameters") or []:
            if not isinstance(param, dict):
                continue
            if param.get("name"):
                names.add(str(param["name"]).lower())
            ref = param.get("$ref", "")
            if ref.startswith("#/parameters/"):
                shared_param = shared.get(ref.split("/")[-1], {})
                if shared_param.get("name"):
                    names.add(str(shared_param["name"]).lower())
    return names


def build_structures(oas: dict[str, Any]) -> list[dict[str, Any]]:
    paths = oas.get("paths", {})
    shared = oas.get("parameters", {})
    structures: list[dict[str, Any]] = []
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        match = re.match(r"^/os/([^/{]+)$", str(path))
        if not match:
            continue
        name = match.group(1)
        tags = (item.get("get", {}) or {}).get("tags") or (item.get("post", {}) or {}).get("tags") or []
        readable, canonical = parse_tag(str(tags[0]) if tags else "")
        resource = map_resource(f"{readable} {canonical} {name}")
        methods = [m.upper() for m in ("get", "post", "put", "delete", "patch") if m in item]
        params = shared_param_names(item, shared)
        structures.append(
            {
                "name": name,
                "canonical": canonical or name.upper(),
                "readable": readable,
                "resource": resource,
                "endpoint": f"/oslc/os/{name}",
                "methods": methods,
                "status": "documented",
                "supports": {
                    "filter": "oslc.where" in params,
                    "sort": "oslc.orderby" in params,
                    "paging": "oslc.paging" in params or "oslc.pagesize" in params,
                    "select": "oslc.select" in params or "oslc.properties" in params,
                },
            }
        )
    structures.sort(key=lambda item: item["name"])
    return structures


def build_capabilities(oas: dict[str, Any], structures: list[dict[str, Any]]) -> dict[str, Any]:
    shared = oas.get("parameters", {})
    query_params = sorted(
        {str(v.get("name")) for v in shared.values() if isinstance(v, dict) and v.get("in") == "query" and v.get("name")}
    )
    lowered = {name.lower() for name in query_params}
    return {
        "system": "maximo",
        "openapi_available": True,
        "filtering": "oslc.where" in lowered,
        "sorting": "oslc.orderby" in lowered,
        "pagination": "oslc.paging" in lowered,
        "field_selection": "oslc.select" in lowered,
        "search": "oslc.searchterms" in lowered,
        "openapi_version": oas.get("openapi"),
        "object_structure_count": len(structures),
        "oslc_query_parameters": query_params,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--oas-file", type=Path, required=True, help="captured Maximo OAS document (JSON)")
    parser.add_argument("--output-dir", type=Path, default=Path("discovery/oslc"), help="where to write catalog files")
    parser.add_argument("--base-url", default="http://maximo.plnindonesiapower.co.id/maximo")
    args = parser.parse_args(argv)

    oas = load_oas(args.oas_file)
    structures = build_structures(oas)
    capabilities = build_capabilities(oas, structures)

    catalog = {
        "system": "maximo",
        "catalog_version": 2,
        "source": "authenticated-oas",
        "base_url": args.base_url,
        "object_structure_count": len(structures),
        "note": "Field-level detail requires live OSLC sampling (GET /oslc/os/{name}?_maxitems=1). Capabilities confirmed from shared OSLC parameters.",
        "object_structures": structures,
    }
    write_json(args.output_dir / "catalog.json", catalog)
    write_json(args.output_dir / "capabilities.json", capabilities)

    by_resource: dict[str, int] = {}
    for structure in structures:
        by_resource[structure["resource"]] = by_resource.get(structure["resource"], 0) + 1
    print(f"Catalog: {len(structures)} object structures -> {args.output_dir / 'catalog.json'}")
    print(f"Capabilities: {args.output_dir / 'capabilities.json'}")
    print(f"By resource: {by_resource}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
