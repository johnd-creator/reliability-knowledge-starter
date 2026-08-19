"""Modbus TCP client — read-only guard, rate limit, register-count cap.

This is the safety core of the cems-collector, mirroring the OSLC guard of
the maximo-collector: only the two Modbus *read* function codes are exposed
(FC03 read_holding_registers, FC04 read_input_registers). Any attempt to
reach a write/mask function raises ModbusGuardError — including attribute
access on this wrapper. The PLC is never written, and Modbus has no
authentication handshake, so unlike the Maximo collector there is no
write-shaped exception at all.
"""

from __future__ import annotations

import inspect
import logging
import time
from dataclasses import dataclass

from src.adapters.modbus.decoding import (
    decode_registers,
    normalize_register_type,
    register_count,
    resolve_register_address,
)
from src.config import CemsConfig
from src.domain.models import ModbusReadConfig

LOG = logging.getLogger(__name__)

READ_ONLY_FUNCTIONS = frozenset({"read_holding_registers", "read_input_registers"})

# Anything containing these tokens is a mutating function code — always blocked.
_BLOCKED_TOKENS = ("write", "mask", "readwrite")


class ModbusError(RuntimeError):
    """Raised for transport/protocol failures (timeouts, exceptions, errors)."""


class ModbusGuardError(RuntimeError):
    """Raised when a non-read-only Modbus function is attempted."""


@dataclass(frozen=True)
class ReadResult:
    value: float
    registers: tuple[int, ...]
    context: dict


class ModbusClient:
    """Read-only Modbus TCP wrapper around pymodbus (imported lazily)."""

    def __init__(
        self,
        config: CemsConfig,
        client_factory=None,
        clock=time.monotonic,
        sleep=time.sleep,
    ):
        self._config = config
        self._client_factory = client_factory
        self._client = None
        self._unit_kwargs: dict | None = None
        self._last_request = 0.0
        self._clock = clock
        self._sleep = sleep

    # -- lifecycle ---------------------------------------------------------------
    def connect(self) -> None:
        if self._client is not None:
            return
        if self._client_factory is not None:
            self._client = self._client_factory()
        else:
            from pymodbus.client import ModbusTcpClient

            self._client = ModbusTcpClient(
                host=self._config.host,
                port=self._config.port,
                timeout=self._config.timeout_seconds,
            )
            self._client.connect()
        self._unit_kwargs = None  # resolve lazily per delegate signature

    def close(self) -> None:
        if self._client is not None:
            try:
                closer = getattr(self._client, "close", None)
                if callable(closer):
                    closer()
            finally:
                self._client = None
                self._unit_kwargs = None

    def _ensure_connected(self) -> None:
        if self._client is None:
            self.connect()

    # -- read-only guard -----------------------------------------------------------
    def __getattr__(self, name: str):
        # Only called for attributes this wrapper does not define. Mutating
        # Modbus function codes must never pass through, not even by accident
        # via the underlying pymodbus client.
        lowered = name.lower()
        if any(token in lowered for token in _BLOCKED_TOKENS):
            raise ModbusGuardError(
                f"blocked non-read-only Modbus function: {name} "
                "(cems-collector is read-only against the PLC)"
            )
        raise AttributeError(name)

    # -- rate limiting --------------------------------------------------------------
    def _throttle(self) -> None:
        gap = self._config.min_request_gap_seconds
        elapsed = self._clock() - self._last_request
        delay = gap - elapsed
        if delay > 0:
            self._sleep(delay)
        self._last_request = self._clock()

    # -- core read ------------------------------------------------------------------
    def read_registers(self, register_type: str, address: int, count: int) -> list[int]:
        """Read registers with the read-only guard, cap, and rate limit applied."""
        normalized = normalize_register_type(register_type)
        if not 1 <= count <= self._config.max_registers_per_read:
            raise ModbusError(
                f"register count {count} outside 1..{self._config.max_registers_per_read}"
            )
        if address < 0:
            raise ModbusError(f"negative register address: {address}")

        self._ensure_connected()
        function = getattr(self._client, normalized if normalized == "read_input_registers" else "read_holding_registers")
        if normalized not in READ_ONLY_FUNCTIONS and function.__name__ not in READ_ONLY_FUNCTIONS:
            raise ModbusGuardError(f"blocked non-read-only Modbus function: {normalized}")

        last_error: Exception | None = None
        for attempt in range(max(1, self._config.retry_attempts)):
            self._throttle()
            try:
                response = function(address, count=count, **self._resolve_unit_kwargs())
                if getattr(response, "isError", lambda: False)():
                    raise ModbusError(f"modbus error response: {response}")
                return list(response.registers)
            except Exception as error:  # noqa: BLE001 — transport failure, retry bounded
                last_error = error
                LOG.warning(
                    "modbus read failed (attempt %s/%s) type=%s address=%s: %s",
                    attempt + 1, max(1, self._config.retry_attempts), normalized, address, error,
                )
                self.close()
                if attempt + 1 < max(1, self._config.retry_attempts):
                    self._sleep(self._config.retry_delay_seconds)
                    self.connect()
        raise ModbusError(
            f"modbus read failed after {max(1, self._config.retry_attempts)} attempts "
            f"(type={normalized} address={address}): {last_error}"
        )

    def _resolve_unit_kwargs(self) -> dict:
        if self._unit_kwargs is None:
            function = self._client.read_holding_registers
            try:
                parameters = inspect.signature(function).parameters
            except (TypeError, ValueError):  # pragma: no cover — exotic delegates
                parameters = {}
            if "device_id" in parameters:
                self._unit_kwargs = {"device_id": self._config.unit_id}
            elif "slave" in parameters:
                self._unit_kwargs = {"slave": self._config.unit_id}
            else:
                self._unit_kwargs = {}
        return self._unit_kwargs

    # -- convenience ----------------------------------------------------------------
    def read_parameter(self, modbus: ModbusReadConfig) -> ReadResult:
        """Resolve, read, and decode one parameter. Returns value + raw registers."""
        register_type = normalize_register_type(modbus.register_type)
        count = register_count(modbus.data_type)
        address = resolve_register_address(modbus.register, modbus.address_base, modbus.zero_based)
        registers = self.read_registers(register_type, address, count)
        value = decode_registers(registers, modbus.data_type, modbus.word_order, modbus.byte_order)
        context = {
            "register": modbus.register,
            "register_address": address,
            "register_type": register_type,
            "data_type": (modbus.data_type or "float32").lower(),
            "address_base": modbus.address_base if modbus.address_base is not None else "direct",
            "zero_based": bool(modbus.zero_based),
            "word_order": modbus.word_order or "big",
            "byte_order": modbus.byte_order or "big",
        }
        return ReadResult(value=value, registers=tuple(registers), context=context)
