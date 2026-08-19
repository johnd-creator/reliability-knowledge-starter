"""Decoding tests: float32 word/byte orders, uint, address resolution."""

from __future__ import annotations

import struct
import unittest

from src.adapters.modbus.decoding import (
    decode_float32_registers,
    decode_registers,
    decode_uint_registers,
    normalize_datatype,
    normalize_register_type,
    normalize_word_or_byte_order,
    register_count,
    resolve_register_address,
)


def float32_registers(value: float) -> list[int]:
    payload = struct.pack(">f", value)
    return list(struct.unpack(">HH", payload))


class TestFloat32Decoding(unittest.TestCase):
    def test_big_big_roundtrip(self):
        registers = float32_registers(123.456)
        self.assertAlmostEqual(
            decode_float32_registers(registers, "big", "big"), 123.456, places=5
        )

    def test_little_word_order_swaps_registers(self):
        registers = float32_registers(123.456)
        self.assertAlmostEqual(
            decode_float32_registers(registers[::-1], "little", "big"), 123.456, places=5
        )

    def test_little_byte_order_swaps_payload(self):
        registers = float32_registers(123.456)
        # byte_order little reinterprets the ordered payload as <f
        words = registers
        payload = struct.pack(">HH", words[0], words[1])
        expected = struct.unpack("<f", payload)[0]
        self.assertAlmostEqual(
            decode_float32_registers(registers, "big", "little"), expected, places=5
        )

    def test_requires_two_registers(self):
        with self.assertRaises(ValueError):
            decode_float32_registers([42], "big", "big")

    def test_decode_registers_dispatches_by_datatype(self):
        registers = float32_registers(-7.25)
        self.assertAlmostEqual(
            decode_registers(registers, "float32", "big", "big"), -7.25, places=5
        )
        self.assertEqual(decode_registers([65535], "uint16"), 65535.0)
        self.assertEqual(decode_registers([0x0001, 0x0002], "uint32"), (1 << 16) | 2)

    def test_register_count(self):
        self.assertEqual(register_count("float32"), 2)
        self.assertEqual(register_count("uint16"), 1)
        self.assertEqual(register_count("float"), 2)


class TestNormalizeHelpers(unittest.TestCase):
    def test_word_order(self):
        self.assertEqual(normalize_word_or_byte_order("BIG"), "big")
        self.assertEqual(normalize_word_or_byte_order(None), "big")
        with self.assertRaises(ValueError):
            normalize_word_or_byte_order("middle")

    def test_datatype_aliases(self):
        self.assertEqual(normalize_datatype("Float"), "float32")
        self.assertEqual(normalize_datatype("int"), "uint16")
        self.assertEqual(normalize_datatype("uint32"), "uint32")
        with self.assertRaises(ValueError):
            normalize_datatype("float64")

    def test_register_type(self):
        self.assertEqual(normalize_register_type(None), "holding")
        self.assertEqual(normalize_register_type("INPUT"), "input")
        with self.assertRaises(ValueError):
            normalize_register_type("coil")


class TestAddressResolution(unittest.TestCase):
    def test_direct(self):
        self.assertEqual(resolve_register_address(3150), 3150)

    def test_modicon_base_zero_based(self):
        # documented 40001 -> protocol address 0 (classic Modicon)
        self.assertEqual(resolve_register_address(40001, address_base=40001, zero_based=True), 0)
        self.assertEqual(resolve_register_address(40005, address_base=40001, zero_based=True), 4)

    def test_one_based_numbering(self):
        self.assertEqual(resolve_register_address(5, address_base=1, zero_based=True), 4)
        self.assertEqual(resolve_register_address(5, address_base=1, zero_based=False), 5)

    def test_negative_address_rejected(self):
        with self.assertRaises(ValueError):
            resolve_register_address(3, address_base=10, zero_based=True)


class TestUintDecoding(unittest.TestCase):
    def test_single_register(self):
        self.assertEqual(decode_uint_registers([42]), 42.0)

    def test_multi_register_big_endian_concat(self):
        self.assertEqual(decode_uint_registers([1, 2]), 65538.0)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            decode_uint_registers([])


if __name__ == "__main__":
    unittest.main()
