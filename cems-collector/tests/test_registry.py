"""Registry parsing tests — validation rules + the real shipped registry."""

from __future__ import annotations

import pathlib
import unittest

from src.config import CemsConfig
from src.services.registry import RegistryError, load_registry, parse_registry

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]

MINIMAL = {
    "stacks": [
        {"stack_id": "1", "code": "CB001", "name": "Cerobong 1", "status": "active"},
    ],
    "parameters": [
        {
            "code": "SO2",
            "name": "Sulfur Dioxide",
            "unit": "mg/Nm3",
            "status": "documented",
            "threshold": 550.0,
            "modbus": {"register": 3150, "register_type": "holding", "data_type": "float32"},
            "normalization": {"enabled": True},
            "adjustment": {"o2_reference": None, "adjust": 1.0, "constant": 0.0},
        },
    ],
}


class TestParseRegistry(unittest.TestCase):
    def test_minimal_valid(self):
        registry = parse_registry(MINIMAL)
        self.assertEqual(len(registry.stacks), 1)
        self.assertEqual(len(registry.parameters), 1)
        parameter = registry.parameters[0]
        self.assertEqual(parameter.modbus.register, 3150)
        self.assertTrue(parameter.normalization_enabled)
        self.assertFalse(parameter.has_adjustment())

    def test_missing_modbus_register_rejected(self):
        data = {
            "stacks": MINIMAL["stacks"],
            "parameters": [{"code": "X", "name": "x", "unit": "%"}],
        }
        with self.assertRaises(RegistryError):
            parse_registry(data)

    def test_missing_required_field_rejected(self):
        data = {
            "stacks": MINIMAL["stacks"],
            "parameters": [
                {"code": "X", "name": "x", "modbus": {"register": 1}},
            ],
        }
        with self.assertRaises(RegistryError):
            parse_registry(data)

    def test_duplicate_code_rejected(self):
        data = {
            "stacks": MINIMAL["stacks"],
            "parameters": [MINIMAL["parameters"][0], MINIMAL["parameters"][0]],
        }
        with self.assertRaises(RegistryError):
            parse_registry(data)

    def test_unknown_stack_rejected(self):
        data = {
            "stacks": MINIMAL["stacks"],
            "parameters": [
                {**MINIMAL["parameters"][0], "stack_id": "9"},
            ],
        }
        with self.assertRaises(RegistryError):
            parse_registry(data)

    def test_no_stacks_rejected(self):
        with self.assertRaises(RegistryError):
            parse_registry({"parameters": MINIMAL["parameters"]})

    def test_invalid_numeric_rejected(self):
        data = {
            "stacks": MINIMAL["stacks"],
            "parameters": [
                {**MINIMAL["parameters"][0], "threshold": "high"},
            ],
        }
        with self.assertRaises(RegistryError):
            parse_registry(data)

    def test_yaml_boolean_code_rejected_with_hint(self):
        # YAML 1.1 parses bare NO/YES/ON/OFF as booleans — must not slip through.
        data = {
            "stacks": MINIMAL["stacks"],
            "parameters": [
                {**MINIMAL["parameters"][0], "code": False},
            ],
        }
        with self.assertRaisesRegex(RegistryError, "quoted string"):
            parse_registry(data)


class TestShippedRegistry(unittest.TestCase):
    def test_shipped_registry_loads(self):
        config = CemsConfig(
            parameter_registry_path=str(PROJECT_ROOT / "registry" / "cems-parameters.yaml")
        ).validate_runtime_safety()
        registry = load_registry(config)
        self.assertEqual(len(registry.stacks), 1)
        self.assertEqual(registry.stacks[0].stack_id, "1")
        self.assertEqual(len(registry.parameters), 15)

        codes = {p.code for p in registry.parameters}
        self.assertIn("SO2", codes)
        self.assertIn("NO", codes)  # must survive the YAML-1.1 boolean trap
        self.assertIn("Opacity", codes)  # production-only parameter (register 3116)
        self.assertIn("Laju_alir", codes)
        self.assertIn("Pressure", codes)

        for parameter in registry.parameters:
            self.assertIsInstance(parameter.code, str)
            self.assertIsInstance(parameter.modbus.register, int)
            self.assertGreater(parameter.modbus.register, 0)
            self.assertIn(parameter.modbus.register_type, ("holding", "input"))
            self.assertIn(parameter.status, ("unknown", "documented", "verified", "forbidden", "deprecated"))

    def test_shipped_registry_matches_production_pipeline(self):
        """The verified production spans/O2-correction must stay in the registry."""
        config = CemsConfig(
            parameter_registry_path=str(PROJECT_ROOT / "registry" / "cems-parameters.yaml")
        ).validate_runtime_safety()
        by_code = {p.code: p for p in load_registry(config).parameters}

        expected_span = {"SO2": 0.4, "NOx": 0.5, "PM": 0.6, "Flow": 0.6, "Laju_alir": 44.15625}
        o2_corrected = {"SO2", "NOx", "PM", "Flow", "Hg", "CO2", "NO", "NO2"}
        passthrough = {"O2", "CO", "Humidity", "Pressure", "Temp", "Opacity"}

        for code, span in expected_span.items():
            self.assertAlmostEqual(by_code[code].adjust_factor, span, msg=code)
        for code in o2_corrected:
            if code != "Laju_alir":
                self.assertEqual(by_code[code].o2_reference, 7.0, msg=code)
        self.assertIsNone(by_code["Laju_alir"].o2_reference)
        for code in passthrough:
            self.assertFalse(by_code[code].has_adjustment(), msg=code)
        # Production does not apply the DAZ Laravel gas conversion.
        for parameter in by_code.values():
            self.assertFalse(parameter.normalization_enabled)


if __name__ == "__main__":
    unittest.main()
