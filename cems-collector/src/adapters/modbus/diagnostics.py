"""Self-healing read diagnostics — ported from the DAZ collector.

When SO2 or CO reads look implausible, the collector probes every
combination of register type x addressing x word/byte order (max 16
variants), plausibility-checks each decoded value, and remembers the
working configuration in memory for the rest of the process lifetime.
Probes only ever *read* registers; nothing is written to the PLC.
"""

from __future__ import annotations

import logging
import math
from dataclasses import replace

from src.adapters.modbus.client import ModbusClient, ModbusError, ReadResult
from src.domain.models import ModbusReadConfig

LOG = logging.getLogger(__name__)

DIAGNOSTIC_ORDER_COMBINATIONS = (
    ("big", "big"),
    ("little", "big"),
    ("big", "little"),
    ("little", "little"),
)


def plausibility_bounds(parameter_code: str) -> tuple[float, float] | None:
    code = str(parameter_code).upper()
    if code == "SO2":
        # Divergence from DAZ (documented): upstream used (0.0, 5000.0) while
        # the probe *trigger* is value <= 1.0, so a probe would immediately
        # re-accept the same implausible reading. The lower bound here is
        # aligned with the trigger so the probe actually explores variants.
        return (1.0, 5000.0)
    if code == "CO":
        return (0.01, math.inf)
    return None


def is_plausible_probe_value(parameter_code: str, value: float) -> bool:
    if not math.isfinite(value):
        return False
    bounds = plausibility_bounds(parameter_code)
    if bounds is None:
        return True
    lower, upper = bounds
    return lower <= value <= upper


def classify_co_value(value: float | None) -> str:
    if value is None:
        return "failed"
    if not math.isfinite(value):
        return "implausible_non_finite"
    if value == 0.0:
        return "raw_zero"
    if value < 0.0:
        return "implausible_negative"
    if value < 0.01:
        return "implausible_tiny"
    return "ok"


def should_probe_after_success(parameter_code: str, value: float) -> bool:
    code = str(parameter_code).upper()
    if code == "SO2":
        return (not math.isfinite(value)) or value <= 1.0 or value > 5000.0
    if code == "CO":
        return classify_co_value(value) != "ok"
    return False


def probe_candidates(modbus: ModbusReadConfig) -> list[ModbusReadConfig]:
    """All read-variant combinations, deduplicated (max 16)."""
    base_type = (modbus.register_type or "holding").lower()
    other_type = "input" if base_type == "holding" else "holding"
    candidates: list[ModbusReadConfig] = []
    seen: set[tuple] = set()
    for candidate_type in (base_type, other_type):
        for explicit_addressing in (None, (1, False)):
            for word_order, byte_order in DIAGNOSTIC_ORDER_COMBINATIONS:
                candidate = replace(
                    modbus,
                    register_type=candidate_type,
                    word_order=word_order,
                    byte_order=byte_order,
                    address_base=explicit_addressing[0] if explicit_addressing else None,
                    zero_based=explicit_addressing[1] if explicit_addressing else False,
                )
                signature = (
                    candidate.register_type,
                    candidate.address_base if candidate.address_base is not None else "direct",
                    candidate.zero_based,
                    candidate.word_order,
                    candidate.byte_order,
                )
                if signature in seen:
                    continue
                seen.add(signature)
                candidates.append(candidate)
    return candidates


def probe_parameter(
    client: ModbusClient,
    modbus: ModbusReadConfig,
    parameter_code: str,
    log_cooldowns: dict[str, float] | None = None,
    clock=float,
) -> ReadResult | None:
    """Try every read variant; return the first plausible result, if any."""
    cooldowns = log_cooldowns if log_cooldowns is not None else {}
    code = str(parameter_code).upper()

    if code not in ("SO2", "CO"):
        return None

    now = clock()
    if now - cooldowns.get(f"{code}:probe-start", 0.0) >= 45.0:
        cooldowns[f"{code}:probe-start"] = now
        LOG.warning("starting %s diagnostic probe sequence", code)

    for candidate in probe_candidates(modbus):
        try:
            result = client.read_parameter(candidate)
        except (ModbusError, ValueError) as error:
            LOG.warning(
                "%s diagnostic probe failed | register=%s type=%s addressing=%s/%s "
                "word=%s byte=%s | %s",
                code, candidate.register, candidate.register_type,
                candidate.address_base if candidate.address_base is not None else "direct",
                candidate.zero_based, candidate.word_order, candidate.byte_order, error,
            )
            continue

        if is_plausible_probe_value(code, result.value):
            if now - cooldowns.get(f"{code}:probe-selected", 0.0) >= 45.0:
                cooldowns[f"{code}:probe-selected"] = now
                LOG.warning(
                    "%s diagnostic selected probe result | recommended_config=%s | value=%s",
                    code, result.context, result.value,
                )
            return result

        LOG.warning(
            "%s diagnostic probe implausible | context=%s | raw_registers=%s | decoded=%s",
            code, result.context, result.registers, result.value,
        )

    return None
