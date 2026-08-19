"""CollectService tests with FakeClient/FakeStore — hermetic, no network/DB."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.adapters.modbus.client import ModbusError, ReadResult
from src.config import CemsConfig
from src.domain.models import ModbusReadConfig, ParameterSpec, Stack
from src.services.collect import CollectService

TS = datetime(2026, 8, 19, 12, 0, 0, tzinfo=timezone.utc)


def spec(code: str, register: int = 3100, register_type: str = "holding") -> ParameterSpec:
    return ParameterSpec(
        code=code,
        stack_id="1",
        name=code,
        unit="mg/Nm3",
        status="documented",
        collect_enabled=True,
        modbus=ModbusReadConfig(register=register, register_type=register_type),
    )


class FakeClient:
    """read_parameter handler injected per test."""

    def __init__(self, handler):
        self.handler = handler
        self.calls: list[ModbusReadConfig] = []

    def read_parameter(self, modbus: ModbusReadConfig) -> ReadResult:
        self.calls.append(modbus)
        result = self.handler(modbus)
        if isinstance(result, Exception):
            raise result
        value = result
        return ReadResult(
            value=value,
            registers=(1234, 5678),
            context={
                "register": modbus.register,
                "register_address": modbus.register,
                "register_type": modbus.register_type,
                "data_type": "float32",
                "address_base": modbus.address_base if modbus.address_base is not None else "direct",
                "zero_based": modbus.zero_based,
                "word_order": modbus.word_order,
                "byte_order": modbus.byte_order,
            },
        )


class FakeStore:
    def __init__(self, specs, stack=None):
        self.specs = specs
        self.stack = stack
        self.inserted = []
        self.runs = []

    def active_parameters(self, stack_id=None):
        return self.specs

    def get_stack(self, stack_id):
        return self.stack

    def insert_readings(self, readings):
        self.inserted.extend(readings)
        return len(readings)

    def record_run(self, run):
        self.runs.append(run)


def make_service(handler, specs, stack=None):
    config = CemsConfig(
        min_request_gap_seconds=0.01,
        max_registers_per_read=125,
        retry_attempts=1,
        retry_delay_seconds=0,
    ).validate_runtime_safety()
    client = FakeClient(handler)
    store = FakeStore(specs, stack)
    return CollectService(client, store, config), client, store


class TestCollectOnce(unittest.TestCase):
    def test_happy_path(self):
        specs = [spec("SO2", 3150), spec("O2", 3114)]
        values = {3150: 350.0, 3114: 11.0}
        service, client, store = make_service(lambda m: values[m.register], specs)
        stats = service.collect_once()

        self.assertEqual(stats.rows_seen, 2)
        self.assertEqual(stats.upserted, 2)
        self.assertEqual(stats.errors, 0)
        self.assertEqual(len(store.inserted), 2)
        by_code = {r.parameter_code: r for r in store.inserted}
        self.assertEqual(by_code["SO2"].stack_id, "1")
        self.assertEqual(by_code["SO2"].transformation_status, "ok")
        self.assertIsNotNone(by_code["SO2"].value_final)
        # vendor read context quarantined under sources.cems
        sources = by_code["SO2"].sources
        self.assertIn("cems", sources)
        self.assertEqual(sources["cems"]["read"]["register"], 3150)
        self.assertEqual(sources["cems"]["raw_registers"], [1234, 5678])
        # one run row recorded
        self.assertEqual(len(store.runs), 1)
        self.assertEqual(store.runs[0].run_type, "collect")

    def test_read_failure_skips_parameter_not_cycle(self):
        specs = [spec("SO2", 3150), spec("CO", 3126)]
        values = {3150: 350.0}

        def handler(modbus):
            if modbus.register == 3126:
                return ModbusError("timeout")
            return values[modbus.register]

        service, client, store = make_service(handler, specs)
        stats = service.collect_once()
        self.assertEqual(stats.errors, 1)
        self.assertEqual(stats.rows_seen, 1)
        codes = {r.parameter_code for r in store.inserted}
        self.assertEqual(codes, {"SO2"})

    def test_empty_registry_raises_clear_error(self):
        service, _, _ = make_service(lambda m: 1.0, [])
        with self.assertRaisesRegex(RuntimeError, "load-registry"):
            service.collect_once()

    def test_failed_transform_counted_as_skipped(self):
        specs = [spec("CO", 3126)]
        service, client, store = make_service(lambda m: 0.0, specs)  # CO raw 0 -> failed
        stats = service.collect_once()
        self.assertEqual(stats.skipped, 1)
        self.assertEqual(store.inserted[0].transformation_status, "failed")


class TestDiagnostics(unittest.TestCase):
    def test_implausible_so2_triggers_probe_and_learns(self):
        specs = [spec("SO2", 3150)]
        probes = {"count": 0}

        def handler(modbus):
            if modbus.register_type == "input":
                probes["count"] += 1
                return 350.0  # plausible via the alternate register type
            return 0.5  # implausible on the configured holding type

        service, client, store = make_service(handler, specs)
        stats = service.collect_once()
        # the plausible probe value replaced the implausible read
        by_code = {r.parameter_code: r for r in store.inserted}
        raw = by_code["SO2"].value_raw
        self.assertAlmostEqual(raw, 350.0)
        # probe variants were tried (multiple candidates before input/big/big)
        self.assertGreater(len(client.calls), 1)
        # the learned override is remembered in memory for the next cycle
        self.assertIn("SO2", service._overrides)
        self.assertEqual(service._overrides["SO2"]["register_type"], "input")

    def test_plausible_so2_does_not_probe(self):
        specs = [spec("SO2", 3150)]
        service, client, store = make_service(lambda m: 350.0, specs)
        service.collect_once()
        self.assertEqual(len(client.calls), 1)

    def test_probe_without_result_keeps_original(self):
        specs = [spec("CO", 3126)]

        def handler(modbus):
            return -1.0  # implausible everywhere

        service, client, store = make_service(handler, specs)
        service.collect_once()
        by_code = {r.parameter_code: r for r in store.inserted}
        # CO raw -1 is operationally invalid -> failed transform
        self.assertEqual(by_code["CO"].transformation_status, "failed")


if __name__ == "__main__":
    unittest.main()
