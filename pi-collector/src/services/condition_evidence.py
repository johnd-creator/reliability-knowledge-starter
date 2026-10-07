"""Internal operator adapter for explicit selected signals; not a public proxy.

Plans must come from trusted Mart administration. Self-declared VERIFIED JSON
is not authorization. Keep this library/file workflow outside the PI HTTP API.
At most five signals, five guarded source GETs per selected snapshot, no history.
"""
from datetime import datetime, timezone
from src.domain.governed import GovernedAfTarget, validate_governed_af_target

MAX_SIGNALS = 5

def validate_plan(plan):
    allowed = {"contract_version", "canonical_asset_id", "mapping_id", "sources", "signals"}
    if not isinstance(plan, dict) or set(plan) != allowed or plan["contract_version"] != "1.0":
        raise ValueError("explicit governed plan required")
    target = validate_governed_af_target(GovernedAfTarget(canonical_asset_id=plan["canonical_asset_id"], **plan["sources"]["pi"]))
    signals = plan["signals"]
    if not isinstance(signals, (list, tuple)) or not 1 <= len(signals) <= MAX_SIGNALS:
        raise ValueError("one to five explicit approved signals required")
    expected = {"signal_id", "mapping_id", "sources", "semantic_name", "approval_status", "approved_by", "approved_at", "evidence_ref"}
    for signal in signals:
        if set(signal) != expected or any(not isinstance(v, str) or not v.strip() or v != v.strip()
                                        for k, v in signal.items() if k != "sources"):
            raise ValueError("explicit approval evidence required")
        sources = signal["sources"]
        if (not isinstance(sources, dict) or set(sources) != {"pi"} or not isinstance(sources["pi"], dict)
            or set(sources["pi"]) != {"attribute_ref"} or not isinstance(sources["pi"]["attribute_ref"], str)
            or not sources["pi"]["attribute_ref"].strip() or sources["pi"]["attribute_ref"] != sources["pi"]["attribute_ref"].strip()):
            raise ValueError("exact selected attribute required")
        if signal["approval_status"] != "APPROVED" or signal["mapping_id"] != plan["mapping_id"]:
            raise ValueError("only approved signals for the exact mapping")
        approved_at = datetime.fromisoformat(signal["approved_at"].replace("Z", "+00:00"))
        if approved_at.tzinfo is None:
            raise ValueError("aware signal approval timestamp required")
    for field in ("signal_id", "sources", "semantic_name"):
        if len({s["sources"]["pi"]["attribute_ref"] if field == "sources" else s[field] for s in signals}) != len(signals):
            raise ValueError("duplicate selected signal")
    return target

def collect_condition_evidence(boundary, plan, *, collector_last_success_at=None):
    target = validate_plan(plan)  # Validate the WHOLE selection before any source call.
    results = []
    for signal in plan["signals"]:
        try:
            name, snapshot = boundary.get_evidence_snapshot(target, signal["sources"]["pi"]["attribute_ref"])
            value = snapshot.source_value
            if snapshot.value_type == "NUMERIC" and value is None:
                value = snapshot.value
            elif snapshot.value_type == "DIGITAL_STATE" and isinstance(value, dict):
                # Explicit vendor-neutral digital semantics; preserve zero/false/null.
                value = {"name": value.get("Name"), "code": value.get("Value"), "is_system": value.get("IsSystem")}
            status = ("BAD_QUALITY" if snapshot.value_good is False or snapshot.value_questionable is True else
                      "UNKNOWN_VALUE" if value is None else "UNKNOWN_QUALITY" if snapshot.value_good is None else "EVIDENCE_AVAILABLE")
            evidence = {"contract_version": "1.0", "canonical_asset_id": plan["canonical_asset_id"],
                "mapping_id": plan["mapping_id"], "signal_id": signal["signal_id"], "semantic_name": signal["semantic_name"],
                "sources": {"pi": {**plan["sources"]["pi"], "attribute_ref": signal["sources"]["pi"]["attribute_ref"], "attribute_name": name}},
                "value": value, "value_type": snapshot.value_type, "unit": snapshot.units,
                "source_timestamp": snapshot.source_timestamp.isoformat() if snapshot.source_timestamp else None,
                "collected_at": (snapshot.collected_at or datetime.now(timezone.utc)).isoformat(),
                "quality_good": snapshot.value_good, "quality_questionable": snapshot.value_questionable,
                "quality_substituted": snapshot.value_substituted, "quality_annotated": snapshot.value_annotated,
                "evidence_status": status, "provenance": {"source_boundary": "GOVERNED_PI_SOURCE",
                    "selection_evidence_ref": signal["evidence_ref"], "selection_approved_by": signal["approved_by"],
                    "selection_approved_at": signal["approved_at"]}}
            results.append({"signal_id": signal["signal_id"], "status": "COLLECTED", "evidence": evidence})
        except Exception:
            # Do not serialize source URLs, responses, credentials or exception strings.
            results.append({"signal_id": signal["signal_id"], "status": "SOURCE_UNAVAILABLE", "evidence": None})
    return {"plan": plan, "results": results, "collector_last_success_at": collector_last_success_at.isoformat() if collector_last_success_at else None}
