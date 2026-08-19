"""Safety-guard tests: read-only Modbus wrapper + config floors. No network."""

from __future__ import annotations

import pathlib
import unittest

from src.adapters.modbus.client import (
    ModbusClient,
    ModbusError,
    ModbusGuardError,
    READ_ONLY_FUNCTIONS,
)
from src.config import CemsConfig

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class FakeResponse:
    def __init__(self, registers):
        self.registers = registers

    def isError(self):
        return False


class FakeDelegate:
    def __init__(self, registers=(0, 0)):
        self.registers = registers
        self.calls = []

    def read_holding_registers(self, address, count=1, **kwargs):
        self.calls.append(("holding", address, count, kwargs))
        return FakeResponse(list(self.registers))

    def read_input_registers(self, address, count=1, **kwargs):
        self.calls.append(("input", address, count, kwargs))
        return FakeResponse(list(self.registers))

    def write_coil(self, address, value, **kwargs):  # must never be reachable
        raise AssertionError("write_coil reached the delegate")

    def write_registers(self, address, values, **kwargs):
        raise AssertionError("write_registers reached the delegate")

    def close(self):
        pass


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


class FakeSleep:
    def __init__(self, clock):
        self.clock = clock
        self.calls = []

    def __call__(self, seconds):
        self.calls.append(seconds)
        self.clock.now += seconds


def make_client(registers=(0, 0), gap=0.05):
    clock = FakeClock()
    sleep = FakeSleep(clock)
    config = CemsConfig(
        min_request_gap_seconds=gap,
        max_registers_per_read=125,
        retry_attempts=1,
        retry_delay_seconds=0,
    ).validate_runtime_safety()
    client = ModbusClient(
        config, client_factory=lambda: FakeDelegate(registers), clock=clock, sleep=sleep
    )
    return client, clock, sleep


class TestReadOnlyGuard(unittest.TestCase):
    def test_read_only_functions_exact_set(self):
        self.assertEqual(READ_ONLY_FUNCTIONS, {"read_holding_registers", "read_input_registers"})

    def test_write_coil_blocked(self):
        client, _, _ = make_client()
        with self.assertRaises(ModbusGuardError):
            client.write_coil(1, True)

    def test_write_registers_blocked(self):
        client, _, _ = make_client()
        with self.assertRaises(ModbusGuardError):
            client.write_registers(1, [0, 0])

    def test_masked_and_readwrite_blocked(self):
        client, _, _ = make_client()
        for name in ("mask_write_register", "readwrite_holding_registers"):
            with self.assertRaises(ModbusGuardError):
                getattr(client, name)

    def test_unknown_attribute_still_attribute_error(self):
        client, _, _ = make_client()
        with self.assertRaises(AttributeError):
            client.definitely_not_a_modbus_function

    def test_adapter_source_has_no_write_calls(self):
        source = (PROJECT_ROOT / "src" / "adapters" / "modbus" / "client.py").read_text()
        for token in (
            ".write_coil(",
            ".write_register(",
            ".write_registers(",
            ".write_multiple_coils(",
            ".mask_write_register(",
        ):
            self.assertNotIn(token, source, f"adapter must not call {token}")

    def test_register_type_allowlist(self):
        client, _, _ = make_client()
        with self.assertRaises(ValueError):
            client.read_registers("coil", 0, 2)

    def test_register_count_cap(self):
        client, _, _ = make_client()
        with self.assertRaises(ModbusError):
            client.read_registers("holding", 0, 126)
        with self.assertRaises(ModbusError):
            client.read_registers("holding", 0, 0)

    def test_negative_address_blocked(self):
        client, _, _ = make_client()
        with self.assertRaises(ModbusError):
            client.read_registers("holding", -1, 2)


class TestRateLimit(unittest.TestCase):
    def test_gap_enforced_between_transactions(self):
        client, clock, sleep = make_client(gap=0.05)
        client.read_registers("holding", 3100, 2)
        self.assertEqual(sleep.calls, [])  # first transaction is free
        client.read_registers("holding", 3102, 2)
        self.assertEqual(sleep.calls, [0.05])  # gap applied on the second

    def test_no_sleep_after_waiting(self):
        client, clock, sleep = make_client(gap=0.05)
        client.read_registers("holding", 3100, 2)
        clock.now += 1.0  # plenty of time elapsed
        client.read_registers("holding", 3102, 2)
        self.assertEqual(sleep.calls, [])

    def test_unit_kwargs_resolved_from_delegate_signature(self):
        client, _, _ = make_client()
        client.connect()
        kwargs = client._resolve_unit_kwargs()
        self.assertEqual(kwargs, {})  # fake accepts **kwargs -> nothing injected


class TestConfigSafety(unittest.TestCase):
    def test_poll_interval_floor(self):
        with self.assertRaises(ValueError):
            CemsConfig(poll_interval_seconds=0.5).validate_runtime_safety()

    def test_request_gap_floor(self):
        with self.assertRaises(ValueError):
            CemsConfig(min_request_gap_seconds=0.001).validate_runtime_safety()

    def test_register_cap_ceiling(self):
        with self.assertRaises(ValueError):
            CemsConfig(max_registers_per_read=126).validate_runtime_safety()

    def test_empty_stack_scope_rejected(self):
        with self.assertRaises(ValueError):
            CemsConfig(stack_id="  ").validate_runtime_safety()

    def test_defaults_pass_validation(self):
        CemsConfig().validate_runtime_safety()


if __name__ == "__main__":
    unittest.main()
