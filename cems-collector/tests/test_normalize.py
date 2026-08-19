"""Normalization tests — behavior parity with the DAZ LegacyNormalizationService."""

from __future__ import annotations

import math
import unittest
from datetime import datetime, timezone

from src.domain.models import ParameterSpec, Stack
from src.services.normalize import (
    GAS_CONVERSION_FACTOR,
    Normalizer,
    maintenance_value_for,
    normalize_code,
    round_stage_value,
)

TS = datetime(2026, 8, 19, 12, 0, 0, tzinfo=timezone.utc)


def spec(code: str, **overrides) -> ParameterSpec:
    defaults = dict(
        code=code,
        stack_id="1",
        name=code,
        unit="mg/Nm3",
        status="documented",
        threshold=None,
    )
    defaults.update(overrides)
    return ParameterSpec(**defaults)


class TestHelpers(unittest.TestCase):
    def test_normalize_code(self):
        # Laravel parity: spaces become underscores, everything uppercased.
        self.assertEqual(normalize_code("laju alir"), "LAJU_ALIR")
        self.assertEqual(normalize_code("o2"), "O2")

    def test_maintenance_values(self):
        self.assertEqual(maintenance_value_for("Hg"), 0.0001)
        self.assertEqual(maintenance_value_for("SO2"), 1.0)

    def test_round_stage_half_away_from_zero(self):
        self.assertEqual(round_stage_value("SO2", 123.4565), 123.457)
        self.assertEqual(round_stage_value("SO2", -123.4565), -123.457)
        self.assertEqual(round_stage_value("Hg", 0.012345678), 0.01235)


class TestNormalizeStage(unittest.TestCase):
    def test_normalization_disabled_passthrough(self):
        parameter = spec("SO2", normalization_enabled=False)
        readings = Normalizer({"SO2": parameter}).transform_batch({"SO2": 123.4567}, TS)
        self.assertEqual(len(readings), 1)
        reading = readings[0]
        self.assertEqual(reading.transformation_status, "ok")
        self.assertAlmostEqual(reading.value_normalized, 123.457, places=6)
        self.assertIsNone(reading.value_correction)
        self.assertAlmostEqual(reading.value_final, 123.457, places=6)

    def test_unknown_parameter_passthrough(self):
        readings = Normalizer({}).transform_batch({"Mystery": 42.0}, TS)
        reading = readings[0]
        self.assertEqual(reading.transformation_status, "ok")
        self.assertAlmostEqual(reading.value_final, 42.0)

    def test_gas_conversion_applied_to_so2(self):
        parameter = spec("SO2", threshold=550.0)
        readings = Normalizer({"SO2": parameter}).transform_batch({"SO2": 100.0}, TS)
        expected = round_stage_value("SO2", 100.0 * GAS_CONVERSION_FACTOR)
        self.assertAlmostEqual(readings[0].value_normalized, expected, places=9)

    def test_gas_conversion_exempt_codes(self):
        # O2 raw must stay <= 18 so the raw-O2 override does not trigger.
        parameters = {"O2": spec("O2"), "PM": spec("PM"), "Laju_alir": spec("Laju_alir")}
        readings = Normalizer(parameters).transform_batch(
            {"O2": 15.0, "PM": 100.0, "Laju_alir": 100.0}, TS
        )
        by_code = {r.parameter_code: r for r in readings}
        self.assertAlmostEqual(by_code["O2"].value_normalized, 15.0, places=6)
        self.assertAlmostEqual(by_code["PM"].value_normalized, 100.0, places=6)
        self.assertAlmostEqual(by_code["Laju_alir"].value_normalized, 100.0, places=6)

    def test_threshold_clamp_at_double_threshold(self):
        parameter = spec("SO2", threshold=10.0)
        # 10.0 raw -> ~12.27 after gas conversion -> ratio 1.227 < 2 -> kept
        readings = Normalizer({"SO2": parameter}).transform_batch({"SO2": 10.0}, TS)
        self.assertGreater(readings[0].value_normalized, 0.0)
        self.assertNotEqual(readings[0].value_normalized, 1.0)
        # 30.0 raw -> ~36.8 -> ratio 3.68 >= 2 -> maintenance value 1.0
        readings = Normalizer({"SO2": parameter}).transform_batch({"SO2": 30.0}, TS)
        self.assertAlmostEqual(readings[0].value_normalized, 1.0)

    def test_negative_forces_maintenance(self):
        parameter = spec("NOx")
        readings = Normalizer({"NOx": parameter}).transform_batch({"NOx": -5.0}, TS)
        self.assertAlmostEqual(readings[0].value_normalized, 1.0)

    def test_zero_stays_zero(self):
        parameter = spec("NOx")
        readings = Normalizer({"NOx": parameter}).transform_batch({"NOx": 0.0}, TS)
        self.assertAlmostEqual(readings[0].value_normalized, 0.0)

    def test_high_raw_o2_forces_maintenance_on_others(self):
        parameters = {"O2": spec("O2"), "SO2": spec("SO2")}
        readings = Normalizer(parameters).transform_batch({"O2": 20.0, "SO2": 100.0}, TS)
        by_code = {r.parameter_code: r for r in readings}
        self.assertAlmostEqual(by_code["SO2"].value_normalized, 1.0)
        # Laravel parity: the raw-O2 override applies to every parameter,
        # including O2 itself (air in the sample line invalidates all gases).
        self.assertAlmostEqual(by_code["O2"].value_normalized, 1.0)

    def test_stack_under_maintenance_override(self):
        stack = Stack(stack_id="1", code="CB001", name="c", status="maintenance")
        parameter = spec("SO2", threshold=550.0)
        readings = Normalizer({"SO2": parameter}, stack, at=TS).transform_batch({"SO2": 100.0}, TS)
        self.assertAlmostEqual(readings[0].value_normalized, 1.0)

    def test_maintenance_override_disabled(self):
        stack = Stack(stack_id="1", code="CB001", name="c", status="maintenance")
        parameter = spec("SO2", threshold=550.0, maintenance_override_enabled=False)
        readings = Normalizer({"SO2": parameter}, stack, at=TS).transform_batch({"SO2": 100.0}, TS)
        self.assertGreater(readings[0].value_normalized, 1.0)

    def test_hg_maintenance_value_and_rounding(self):
        parameter = spec("Hg", threshold=0.03)
        # 1.0 raw -> ~1.227 -> ratio >= 2 -> maintenance 0.0001
        readings = Normalizer({"Hg": parameter}).transform_batch({"Hg": 1.0}, TS)
        self.assertAlmostEqual(readings[0].value_normalized, 0.0001)


class TestValidity(unittest.TestCase):
    def test_co_zero_raw_is_failed(self):
        parameter = spec("CO")
        readings = Normalizer({"CO": parameter}).transform_batch({"CO": 0.0}, TS)
        reading = readings[0]
        self.assertEqual(reading.transformation_status, "failed")
        self.assertIsNone(reading.value_final)
        self.assertEqual(reading.value_raw, 0.0)

    def test_co_negative_normalized_is_failed(self):
        parameter = spec("CO")
        readings = Normalizer({"CO": parameter}).transform_batch({"CO": -3.0}, TS)
        self.assertEqual(readings[0].transformation_status, "failed")

    def test_missing_raw_is_failed(self):
        parameter = spec("SO2", threshold=550.0)
        readings = Normalizer({"SO2": parameter}).transform_batch({"SO2": None}, TS)
        reading = readings[0]
        self.assertEqual(reading.transformation_status, "failed")
        self.assertIsNone(reading.value_raw)

    def test_one_bad_reading_never_aborts_batch(self):
        parameters = {"SO2": spec("SO2", threshold=550.0), "O2": spec("O2")}
        readings = Normalizer(parameters).transform_batch({"SO2": None, "O2": 11.0}, TS)
        by_code = {r.parameter_code: r for r in readings}
        self.assertEqual(by_code["SO2"].transformation_status, "failed")
        self.assertEqual(by_code["O2"].transformation_status, "ok")


class TestAdjustmentStage(unittest.TestCase):
    def test_no_adjustment_keeps_normalized(self):
        parameter = spec("SO2")
        readings = Normalizer({"SO2": parameter}).transform_batch({"SO2": 50.0}, TS)
        reading = readings[0]
        self.assertIsNone(reading.value_correction)
        self.assertAlmostEqual(reading.value_final, reading.value_normalized)

    def test_o2_reference_correction(self):
        parameters = {
            "SO2": spec("SO2", o2_reference=7.0),
            "O2": spec("O2"),
        }
        readings = Normalizer(parameters).transform_batch({"SO2": 100.0, "O2": 11.0}, TS)
        by_code = {r.parameter_code: r for r in readings}
        so2 = by_code["SO2"]
        # correction factor = (21-7)/(21-11) = 1.4
        expected = round_stage_value("SO2", 100.0 * GAS_CONVERSION_FACTOR * 1.4)
        self.assertAlmostEqual(so2.value_correction, expected, places=9)
        self.assertAlmostEqual(so2.value_final, expected, places=9)

    def test_adjust_factor_and_constant(self):
        parameter = spec("Laju_alir", adjust_factor=44.15625, adjust_constant=0.0)
        readings = Normalizer({"Laju_alir": parameter}).transform_batch({"Laju_alir": 2.0}, TS)
        expected = round_stage_value("LAJU_ALIR", 2.0 * 44.15625)
        self.assertAlmostEqual(readings[0].value_correction, expected)

    def test_constant_applies_after_factor(self):
        parameter = spec("NOx", adjust_factor=2.0, adjust_constant=10.0)
        readings = Normalizer({"NOx": parameter}).transform_batch({"NOx": 5.0}, TS)
        expected = round_stage_value("NOX", 5.0 * GAS_CONVERSION_FACTOR * 2.0 + 10.0)
        self.assertAlmostEqual(readings[0].value_correction, expected)

    def test_undefined_o2_correction_fails_reading(self):
        # With normalization active, raw O2=21 becomes a maintenance value, so
        # the undefined path needs an O2 parameter that passes through raw.
        parameters = {
            "SO2": spec("SO2", o2_reference=7.0),
            "O2": spec("O2", normalization_enabled=False),
        }
        readings = Normalizer(parameters).transform_batch({"SO2": 100.0, "O2": 21.0}, TS)
        by_code = {r.parameter_code: r for r in readings}
        self.assertEqual(by_code["SO2"].transformation_status, "failed")
        self.assertIsNotNone(by_code["SO2"].value_normalized)
        self.assertIsNone(by_code["SO2"].value_final)

    def test_reading_carries_stack_and_timestamp(self):
        parameter = spec("SO2")
        readings = Normalizer({"SO2": parameter}).transform_batch({"SO2": 1.0}, TS)
        reading = readings[0]
        self.assertEqual(reading.stack_id, "1")
        self.assertEqual(reading.observed_at, TS)


if __name__ == "__main__":
    unittest.main()
