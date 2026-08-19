"""Legacy normalization pipeline — port of the DAZ LegacyNormalizationService.

Stage order per reading (mirroring the Laravel service exactly):
  1. normalize:  gas conversion -> threshold clamp -> state overrides -> round
  2. validity:   CO readings <= 0 are operationally invalid -> failed
  3. adjust:     O2-reference correction, then factor + constant -> value_final

Values that fail any stage keep their raw (and where available normalized)
stages and are marked ``transformation_status = "failed"`` — one bad reading
never aborts the batch.

Divergence from DAZ (documented): the Laravel formula-string engine
(normalize/formula fields evaluated via shunting-yard) is replaced by
explicit numeric fields (o2_reference / adjust / constant) — same pipeline
semantics for the fields actually seeded in production, without a formula
interpreter in the collector.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Mapping

from src.domain.models import ParameterSpec, Reading, Stack

GAS_CONVERSION_FACTOR = 30.01 / (0.08206 * (25 + 273.15))
GAS_CONVERSION_EXEMPT_CODES = frozenset({"O2", "LAJU_ALIR", "PM"})
RAW_O2_MAINTENANCE_LIMIT = 18.0
THRESHOLD_CLAMP_RATIO = 2.0


def normalize_code(code: str) -> str:
    return str(code).upper().replace(" ", "_")


def maintenance_value_for(code: str) -> float:
    return 0.0001 if normalize_code(code) == "HG" else 1.0


def round_stage_value(code: str, value: float) -> float:
    """PHP-style round (half away from zero); Hg gets 5 decimals, others 3."""
    digits = 5 if normalize_code(code) == "HG" else 3
    factor = 10 ** digits
    return math.copysign(math.floor(abs(value) * factor + 0.5), value) / factor


def requires_gas_conversion(code: str) -> bool:
    return normalize_code(code) not in GAS_CONVERSION_EXEMPT_CODES


def resolve_raw_oxygen(raw_readings: Mapping[str, float | None]) -> float:
    for key in ("O2", "o2"):
        value = raw_readings.get(key)
        if value is not None and value != "":
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return 0.0


class Normalizer:
    def __init__(
        self,
        parameters: Mapping[str, ParameterSpec],
        stack: Stack | None = None,
        at: datetime | None = None,
    ):
        self._parameters = {normalize_code(k): v for k, v in parameters.items()}
        self._stack = stack
        self._at = at

    # -- public ---------------------------------------------------------------
    def transform_batch(
        self,
        raw_readings: Mapping[str, float | None],
        timestamp: datetime,
    ) -> list[Reading]:
        normalized_values: dict[str, float | None] = {}
        failed: set[str] = set()

        for code in raw_readings:
            key = normalize_code(code)
            parameter = self._parameters.get(key)
            try:
                raw = self._to_float(raw_readings[code])
                if raw is None:
                    raise ValueError("missing raw reading value")
                normalized_values[key] = self.normalize_value(
                    key, raw, parameter, raw_readings
                )
            except Exception:  # noqa: BLE001 — one bad reading never aborts the batch
                normalized_values[key] = None
                failed.add(key)

        normalized_oxygen = self._resolve_normalized_oxygen(normalized_values, raw_readings)

        readings: list[Reading] = []
        for code, raw_value in raw_readings.items():
            key = normalize_code(code)
            parameter = self._parameters.get(key)
            raw = self._to_float(raw_value)
            normalized = normalized_values.get(key)

            if (
                key in failed
                or normalized is None
                or self._is_operationally_invalid(key, raw, normalized)
            ):
                readings.append(
                    Reading(
                        parameter_code=code,
                        stack_id=parameter.stack_id if parameter else "",
                        observed_at=timestamp,
                        value_raw=raw,
                        transformation_status="failed",
                    )
                )
                continue

            has_adjustment = parameter is not None and parameter.has_adjustment()
            try:
                final = (
                    self._apply_adjustment(normalized, parameter, normalized_oxygen)
                    if has_adjustment
                    else normalized
                )
            except Exception:  # noqa: BLE001 — adjustment failure marks one reading
                readings.append(
                    Reading(
                        parameter_code=code,
                        stack_id=parameter.stack_id if parameter else "",
                        observed_at=timestamp,
                        value_raw=raw,
                        value_normalized=normalized,
                        transformation_status="failed",
                    )
                )
                continue

            final = round_stage_value(key, final)
            readings.append(
                Reading(
                    parameter_code=code,
                    stack_id=parameter.stack_id if parameter else "",
                    observed_at=timestamp,
                    value_raw=raw,
                    value_normalized=normalized,
                    value_correction=final if has_adjustment else None,
                    value_final=final,
                    transformation_status="ok",
                )
            )
        return readings

    # -- normalize stage --------------------------------------------------------
    def normalize_value(
        self,
        code: str,
        raw_value: float,
        parameter: ParameterSpec | None,
        raw_readings: Mapping[str, float | None],
    ) -> float:
        if parameter is None or not parameter.normalization_enabled:
            return round_stage_value(code, raw_value)

        value = raw_value
        raw_oxygen = resolve_raw_oxygen(raw_readings)

        if requires_gas_conversion(code):
            value *= GAS_CONVERSION_FACTOR

        value = self._threshold_clamp(code, value, parameter)
        value = self._state_overrides(code, value, parameter, raw_oxygen)
        return round_stage_value(code, value)

    def _threshold_clamp(self, code: str, value: float, parameter: ParameterSpec) -> float:
        threshold = parameter.threshold if parameter.threshold is not None else 0.0
        if threshold <= 0:
            return value
        if (value / threshold) >= THRESHOLD_CLAMP_RATIO:
            return maintenance_value_for(code)
        return value

    def _state_overrides(
        self,
        code: str,
        value: float,
        parameter: ParameterSpec,
        raw_oxygen: float,
    ) -> float:
        if value == 0.0:
            return 0.0
        if value < 0.0:
            return maintenance_value_for(code)
        if (
            parameter.maintenance_override_enabled
            and self._stack is not None
            and self._stack.is_under_maintenance(
                self._at or datetime.now()
            )
        ):
            return maintenance_value_for(code)
        if raw_oxygen > RAW_O2_MAINTENANCE_LIMIT:
            return maintenance_value_for(code)
        return value

    # -- adjust stage -------------------------------------------------------------
    def _apply_adjustment(
        self,
        normalized: float,
        parameter: ParameterSpec,
        normalized_oxygen: float,
    ) -> float:
        value = normalized
        if parameter.o2_reference is not None:
            denominator = 21.0 - normalized_oxygen
            if denominator == 0.0:
                raise ValueError("O2 correction undefined: measured O2 equals 21%")
            value = value * ((21.0 - parameter.o2_reference) / denominator)
        return value * parameter.adjust_factor + parameter.adjust_constant

    # -- helpers -----------------------------------------------------------------
    @staticmethod
    def _resolve_normalized_oxygen(
        normalized_values: Mapping[str, float | None],
        raw_readings: Mapping[str, float | None],
    ) -> float:
        # normalized_values keys are normalize_code()-uppercased.
        value = normalized_values.get("O2")
        if value is not None:
            return float(value)
        return resolve_raw_oxygen(raw_readings)

    @staticmethod
    def _is_operationally_invalid(code: str, raw: float | None, normalized: float | None) -> bool:
        if normalize_code(code) != "CO":
            return False
        if raw is not None and raw <= 0.0:
            return True
        return normalized is not None and normalized <= 0.0

    @staticmethod
    def _to_float(value) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
