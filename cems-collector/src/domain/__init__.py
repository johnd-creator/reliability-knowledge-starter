"""Domain models (frozen dataclasses, contract-shaped)."""

from src.domain.models import (
    AggregatedReading,
    ModbusReadConfig,
    ParameterSpec,
    Reading,
    Stack,
)

__all__ = [
    "AggregatedReading",
    "ModbusReadConfig",
    "ParameterSpec",
    "Reading",
    "Stack",
]
