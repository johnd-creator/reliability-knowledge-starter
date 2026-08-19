#!/usr/bin/env python3
"""Build the complete BSR1 attribute registry from verified discovery files.

This is an offline transformation. It never calls PI. The hierarchy walk and
stream verification must be run separately before invoking this script.

Existing entries in ``mappings/bsr1-parameters.yaml`` keep their reviewed
semantic parameter category. Newly discovered attributes are retained under
``unclassified`` until a human assigns business meaning; this avoids guessing
semantics from a tag name while still making every discovered WebId available
to downstream tooling.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _canonical_equipment(name: str) -> str:
    if name.startswith("BSR1."):
        return name
    return f"BSR1.{name}"


def _flatten_semantic_mapping(data: dict) -> dict[str, dict]:
    by_web_id: dict[str, dict] = {}
    for equipment, equipment_data in (data.get("equipment") or {}).items():
        for parameter, entries in (equipment_data.get("parameters") or {}).items():
            if parameter == "unclassified":
                continue
            for entry in entries or []:
                web_id = entry.get("web_id")
                if not web_id:
                    continue
                if web_id in by_web_id:
                    raise ValueError(f"duplicate semantic web_id: {web_id}")
                by_web_id[web_id] = {
                    "equipment": equipment,
                    "parameter": parameter,
                    **entry,
                }
    return by_web_id


def _load_stream_health(path: Path) -> tuple[dict[str, dict], dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    health = {entry["web_id"]: entry for entry in data.get("attributes", [])}
    if len(health) != len(data.get("attributes", [])):
        raise ValueError("stream verification contains duplicate WebIds")
    return health, data


def build(walk_path: Path, health_path: Path, existing_path: Path) -> dict:
    walk = json.loads(walk_path.read_text(encoding="utf-8"))
    existing = yaml.safe_load(existing_path.read_text(encoding="utf-8")) or {}
    semantic = _flatten_semantic_mapping(existing)
    health, verification = _load_stream_health(health_path)

    walk_by_web_id = {entry["web_id"]: entry for entry in walk}
    if len(walk_by_web_id) != len(walk):
        raise ValueError("BSR1 walk contains duplicate WebIds")
    missing_health = set(walk_by_web_id) - set(health)
    if missing_health:
        raise ValueError(f"{len(missing_health)} walked WebIds have no stream health result")

    equipment: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for web_id, walked in sorted(
        walk_by_web_id.items(),
        key=lambda item: (
            _canonical_equipment(item[1]["equipment"]),
            item[1].get("sub_element") or "",
            item[1].get("attribute") or "",
            item[0],
        ),
    ):
        reviewed = semantic.get(web_id)
        checked = health[web_id]
        stream_status = checked["stream_status"]
        entry = {
            "name": reviewed.get("name", walked.get("attribute", "")) if reviewed else walked.get("attribute", ""),
            "unit": (reviewed.get("unit") if reviewed else walked.get("units")) or "",
            "position": (reviewed.get("position") if reviewed else walked.get("sub_element")) or "",
            "web_id": web_id,
            "stream_status": stream_status,
            "status": "verified" if stream_status == "ok" else "broken",
            "source_system": walked.get("system_name"),
            "data_type": walked.get("type"),
        }
        if reviewed:
            parameter = reviewed["parameter"]
            target_equipment = reviewed["equipment"]
        else:
            parameter = "unclassified"
            target_equipment = _canonical_equipment(walked["equipment"])
        equipment[target_equipment][parameter].append(entry)

    total = len(walk)
    summary = verification.get("summary") or {}
    return {
        "site": existing.get("site", "BSR"),
        "unit": existing.get("unit", "BSR1"),
        "source": "pi",
        "status": "verified",
        "verified_at": verification.get("verified_at") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "attribute_count": total,
        "semantic_mapping_count": len(semantic),
        "verification": {
            "method": verification.get("method", "GET /streams/{webId}/value per attribute (read-only)"),
            "summary": summary,
            "note": "All discovered attributes are retained. pi-collector loads only status=verified and stream_status=ok entries.",
        },
        "equipment": {
            name: {
                "parameter_count": sum(len(values) for values in parameters.values()),
                "parameters": dict(sorted(parameters.items())),
            }
            for name, parameters in sorted(equipment.items())
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--walk", type=Path, default=Path("/tmp/bsr1_walk_v2.json"))
    parser.add_argument("--health", type=Path, default=Path("discovery/stream-verification.json"))
    parser.add_argument("--output", type=Path, default=Path("mappings/bsr1-parameters.yaml"))
    args = parser.parse_args()
    data = build(args.walk, args.health, args.output)
    args.output.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )
    print(
        f"wrote {data['attribute_count']} BSR1 attributes "
        f"({data['semantic_mapping_count']} semantic, "
        f"{data['verification']['summary'].get('ok', 0)} stream-ok) -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
