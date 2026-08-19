"""Domain models — frozen dataclasses with contract-shaped field names.

Core fields are vendor-neutral snake_case. Modbus specifics (register
numbers, word/byte order, addressing mode) are quarantined in the nested
``ModbusReadConfig`` dataclass and surface only under ``sources.cems``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True, frozen=True)
class ModbusReadConfig:
    """Quarantined vendor block: how to read one parameter off the PLC."""

    register: int
    register_type: str = "holding"  # "holding" | "input"
    data_type: str = "float32"  # "float32" | "uint16" | "uint32"
    word_order: str = "big"  # "big" | "little"
    byte_order: str = "big"  # "big" | "little"
    address_base: int | None = None  # e.g. 40001-based addressing; None = direct
    zero_based: bool = False


@dataclass(slots=True, frozen=True)
class Stack:
    stack_id: str
    code: str
    name: str
    status: str = "active"  # active | maintenance | broken
    description: str | None = None
    maintenance_from: datetime | None = None
    maintenance_to: datetime | None = None

    def is_under_maintenance(self, at: datetime) -> bool:
        if self.status != "maintenance":
            return False
        if self.maintenance_from is not None and at < self.maintenance_from:
            return False
        if self.maintenance_to is not None and at > self.maintenance_to:
            return False
        return True


@dataclass(slots=True, frozen=True)
class ParameterSpec:
    code: str
    stack_id: str
    name: str
    unit: str
    status: str  # knowledge vocabulary: unknown | documented | verified | forbidden | deprecated
    collect_enabled: bool = True  # operational switch: is this parameter polled
    threshold: float | None = None
    normalization_enabled: bool = True
    maintenance_override_enabled: bool = True
    o2_reference: float | None = None
    adjust_factor: float = 1.0
    adjust_constant: float = 0.0
    modbus: ModbusReadConfig = field(default_factory=lambda: ModbusReadConfig(register=0))

    def has_adjustment(self) -> bool:
        return (
            self.o2_reference is not None
            or self.adjust_factor != 1.0
            or self.adjust_constant != 0.0
        )


@dataclass(slots=True, frozen=True)
class Reading:
    parameter_code: str
    stack_id: str
    observed_at: datetime
    value_raw: float | None
    value_normalized: float | None = None
    value_correction: float | None = None
    value_final: float | None = None
    transformation_status: str = "ok"  # "ok" | "failed"
    sources: dict | None = None


@dataclass(slots=True, frozen=True)
class AggregatedReading:
    parameter_code: str
    stack_id: str
    window_start: datetime
    avg_value: float
    min_value: float
    max_value: float
    sample_count: int
