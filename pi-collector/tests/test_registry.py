"""Unit tests for the registry loader — no network, no DB required."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from src.services.registry import load_registry, _slug, _build_attribute_id


SAMPLE_YAML = textwrap.dedent("""
    site: BSR
    unit: BSR1
    source: pi
    status: verified
    equipment:
      BSR1.Turbine:
        parameter_count: 2
        parameters:
          bearing_temperature:
          - name: Bearing 1 Left Temperature
            unit: degC
            position: ''
            web_id: F1DPabc123
          vibration:
          - name: Bearing 1X Vibration
            unit: um
            position: BSR1.HP Turbine
            web_id: F1DPdef456
      BSR1.Generator:
        parameter_count: 1
        parameters:
          excitation_current:
          - name: Field Current
            unit: A
            position: ''
            web_id: F1AbXYZ789
""")


class SlugTest(unittest.TestCase):
    def test_basic_slug(self):
        self.assertEqual(_slug("Bearing 1 Left Temperature"), "bearing_1_left_temperature")

    def test_special_chars(self):
        self.assertEqual(_slug("BSR1.HP Turbine"), "bsr1_hp_turbine")
        self.assertEqual(_slug("MAIN STEAM HEAD PRE1"), "main_steam_head_pre1")


class AttributeIdTest(unittest.TestCase):
    def test_deterministic_id(self):
        aid = _build_attribute_id("BSR", "BSR1", "BSR1.Turbine", "bearing_temperature", "Bearing 1 Left", "")
        self.assertEqual(aid, "BSR-BSR1-bsr1_turbine-bearing_temperature-bearing_1_left")

    def test_id_with_position(self):
        aid = _build_attribute_id("BSR", "BSR1", "BSR1.HP Turbine", "vibration", "Bearing 1X", "BSR1.HP Turbine")
        self.assertIn("bsr1_hp_turbine", aid)


class LoadRegistryTest(unittest.TestCase):
    def test_loads_all_entries_with_webid(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(SAMPLE_YAML)
            f.flush()
            regs = load_registry(f.name)

        self.assertEqual(len(regs), 3)

        reg = next(r for r in regs if r.parameter == "bearing_temperature")
        self.assertEqual(reg.site, "BSR")
        self.assertEqual(reg.unit, "BSR1")
        self.assertEqual(reg.equipment, "BSR1.Turbine")
        self.assertEqual(reg.web_id, "F1DPabc123")
        self.assertEqual(reg.unit_of_measure, "degC")
        self.assertTrue(reg.attribute_id.startswith("BSR-BSR1-"))

    def test_skips_entries_without_webid(self):
        yaml_no_wid = SAMPLE_YAML.replace("web_id: F1DPabc123", "web_id: ''")
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(yaml_no_wid)
            f.flush()
            regs = load_registry(f.name)
        self.assertEqual(len(regs), 2)  # one skipped

    def test_skips_broken_status_entries(self):
        yaml_broken = SAMPLE_YAML.replace(
            "web_id: F1DPdef456", "web_id: F1DPdef456\n        status: broken\n        stream_status: gone"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(yaml_broken)
            f.flush()
            regs = load_registry(f.name)
        self.assertEqual(len(regs), 2)  # broken entry skipped

    def test_skips_stream_status_gone_entries(self):
        yaml_gone = SAMPLE_YAML.replace(
            "web_id: F1AbXYZ789", "web_id: F1AbXYZ789\n        stream_status: gone"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(yaml_gone)
            f.flush()
            regs = load_registry(f.name)
        self.assertEqual(len(regs), 2)  # gone entry skipped

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_registry("/nonexistent/path.yaml")

    def test_position_populated(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(SAMPLE_YAML)
            f.flush()
            regs = load_registry(f.name)
        vib = next(r for r in regs if r.parameter == "vibration")
        self.assertEqual(vib.position, "BSR1.HP Turbine")


if __name__ == "__main__":
    unittest.main()
