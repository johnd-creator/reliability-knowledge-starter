"""Registry loader: YAML file -> domain models (stacks + parameter specs).

The registry is the local equivalent of pi-knowledge mappings: the collector
never hardcodes register numbers. Modbus details stay nested under the
``modbus:`` key and are quarantined under ``sources.cems`` downstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.config import CemsConfig
from src.domain.models import ModbusReadConfig, ParameterSpec, Stack


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class Registry:
    stacks: list[Stack]
    parameters: list[ParameterSpec]


def _require(entry: dict, key: str, context: str):
    value = entry.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise RegistryError(f"{context}: missing required field '{key}'")
    return value


def _load_stack(entry: dict) -> Stack:
    return Stack(
        stack_id=str(_require(entry, "stack_id", "stack")),
        code=str(_require(entry, "code", "stack")),
        name=str(_require(entry, "name", "stack")),
        status=str(entry.get("status", "active")),
        description=entry.get("description"),
        maintenance_from=None,
        maintenance_to=None,
    )


def _load_parameter(entry: dict, default_stack_id: str) -> ParameterSpec:
    raw_code = entry.get("code")
    if not isinstance(raw_code, str):
        # YAML 1.1 parses bare NO/YES/ON/OFF as booleans — catch it here with
        # a clear hint instead of silently collecting a "False" parameter.
        raise RegistryError(
            f"parameter code must be a quoted string (got {type(raw_code).__name__}: "
            f"{raw_code!r}) — quote codes like NO in the registry YAML"
        )
    code = raw_code.strip()
    if not code:
        raise RegistryError("parameter: missing required field 'code'")
    modbus_raw = entry.get("modbus") or {}
    try:
        modbus = ModbusReadConfig(
            register=int(_require(modbus_raw, "register", f"parameter {code} modbus")),
            register_type=str(modbus_raw.get("register_type", "holding")),
            data_type=str(modbus_raw.get("data_type", "float32")),
            word_order=str(modbus_raw.get("word_order", "big")),
            byte_order=str(modbus_raw.get("byte_order", "big")),
            address_base=modbus_raw.get("address_base"),
            zero_based=bool(modbus_raw.get("zero_based", False)),
        )
    except (TypeError, ValueError) as error:
        raise RegistryError(f"parameter {code}: invalid modbus block: {error}") from error

    normalization = entry.get("normalization") or {}
    adjustment = entry.get("adjustment") or {}

    o2_reference = adjustment.get("o2_reference")
    try:
        return ParameterSpec(
            code=code,
            stack_id=str(entry.get("stack_id", default_stack_id)),
            name=str(_require(entry, "name", f"parameter {code}")),
            unit=str(_require(entry, "unit", f"parameter {code}")),
            status=str(entry.get("status", "documented")),
            collect_enabled=bool(entry.get("collect", True)),
            threshold=float(entry["threshold"]) if entry.get("threshold") is not None else None,
            normalization_enabled=bool(normalization.get("enabled", True)),
            maintenance_override_enabled=bool(normalization.get("maintenance_override_enabled", True)),
            o2_reference=float(o2_reference) if o2_reference is not None else None,
            adjust_factor=float(adjustment.get("adjust", 1.0)),
            adjust_constant=float(adjustment.get("constant", 0.0)),
            modbus=modbus,
        )
    except (TypeError, ValueError) as error:
        raise RegistryError(f"parameter {code}: invalid numeric field: {error}") from error


def parse_registry(data: dict, default_stack_id: str | None = None) -> Registry:
    stacks = [_load_stack(entry) for entry in data.get("stacks") or []]
    if not stacks:
        raise RegistryError("registry has no stacks")
    if default_stack_id is None:
        default_stack_id = stacks[0].stack_id
    known_stacks = {stack.stack_id for stack in stacks}

    parameters: list[ParameterSpec] = []
    seen: set[tuple[str, str]] = set()
    for entry in data.get("parameters") or []:
        parameter = _load_parameter(entry, default_stack_id)
        if parameter.stack_id not in known_stacks:
            raise RegistryError(
                f"parameter {parameter.code}: unknown stack_id {parameter.stack_id!r}"
            )
        key = (parameter.code, parameter.stack_id)
        if key in seen:
            raise RegistryError(f"duplicate parameter code in registry: {parameter.code}")
        seen.add(key)
        parameters.append(parameter)

    if not parameters:
        raise RegistryError("registry has no parameters")
    return Registry(stacks=stacks, parameters=parameters)


def load_registry(config: CemsConfig) -> Registry:
    path = Path(config.parameter_registry_path)
    if not path.exists():
        raise RegistryError(
            f"registry file not found: {path} (set CEMS_PARAMETER_REGISTRY)"
        )
    with path.open("r", encoding="utf-8") as handle:
        try:
            data = yaml.safe_load(handle) or {}
        except yaml.YAMLError as error:
            raise RegistryError(f"invalid registry YAML: {error}") from error
    if not isinstance(data, dict):
        raise RegistryError("registry YAML must be a mapping")
    return parse_registry(data, default_stack_id=config.stack_id)
