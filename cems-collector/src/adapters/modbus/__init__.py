"""Read-only Modbus adapter: client guard, decoding, diagnostics."""

from src.adapters.modbus.client import (
    ModbusClient,
    ModbusError,
    ModbusGuardError,
    ReadResult,
    READ_ONLY_FUNCTIONS,
)

__all__ = [
    "ModbusClient",
    "ModbusError",
    "ModbusGuardError",
    "ReadResult",
    "READ_ONLY_FUNCTIONS",
]
