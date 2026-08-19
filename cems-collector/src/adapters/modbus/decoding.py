"""Modbus register decoding — pure functions, ported from the DAZ collector.

Float32 values arrive as two consecutive 16-bit registers; both the word
order (which register holds the high word) and the byte order (endianness
inside each register) are configurable per parameter.
"""

from __future__ import annotations

import struct


def normalize_word_or_byte_order(value: str | None) -> str:
    order = (value or "big").strip().lower()
    if order not in ("big", "little"):
        raise ValueError(f"unsupported word/byte order: {value!r}")
    return order


def normalize_datatype(value: str | None) -> str:
    data_type = (value or "float32").strip().lower()
    aliases = {
        "float": "float32",
        "float32": "float32",
        "float16": "float32",  # not supported upstream either; treated as float32
        "int": "uint16",
        "uint": "uint16",
        "uint16": "uint16",
        "int16": "uint16",
        "uint32": "uint32",
        "int32": "uint32",
    }
    if data_type not in aliases:
        raise ValueError(f"unsupported modbus data_type: {value!r}")
    return aliases[data_type]


def normalize_register_type(value: str | None) -> str:
    register_type = (value or "holding").strip().lower()
    if register_type not in ("holding", "input"):
        raise ValueError(f"unsupported register_type: {value!r}")
    return register_type


def decode_float32_registers(
    registers: list[int],
    word_order: str | None = "big",
    byte_order: str | None = "big",
) -> float:
    """Decode two 16-bit registers as one float32.

    word_order: which register carries the high word ("big" = first).
    byte_order: endianness of the 32-bit payload once words are ordered.
    """
    if len(registers) != 2:
        raise ValueError(f"float32 needs exactly 2 registers, got {len(registers)}")
    words = list(registers)
    if normalize_word_or_byte_order(word_order) == "little":
        words = words[::-1]
    payload = struct.pack(">HH", words[0] & 0xFFFF, words[1] & 0xFFFF)
    if normalize_word_or_byte_order(byte_order) == "little":
        value = struct.unpack("<f", payload)[0]
    else:
        value = struct.unpack(">f", payload)[0]
    return float(value)


def decode_uint_registers(registers: list[int]) -> float:
    """Decode 1 register as uint16 or N registers as a big-endian integer."""
    if not registers:
        raise ValueError("no registers to decode")
    if len(registers) == 1:
        return float(registers[0] & 0xFFFF)
    value = 0
    for register in registers:
        value = (value << 16) | (register & 0xFFFF)
    return float(value)


def decode_registers(registers: list[int], data_type: str | None,
                     word_order: str | None = "big",
                     byte_order: str | None = "big") -> float:
    normalized = normalize_datatype(data_type)
    if normalized in ("uint16", "uint32"):
        return decode_uint_registers(registers)
    return decode_float32_registers(registers, word_order, byte_order)


def register_count(data_type: str | None) -> int:
    return 2 if normalize_datatype(data_type) == "float32" else 1


def resolve_register_address(
    register: int,
    address_base: int | None = None,
    zero_based: bool = False,
) -> int:
    """Translate a documented register number into a protocol address.

    address_base None  -> "direct": the number is already the address.
    address_base 40001 -> classic Modicon addressing (base-40001, offset
                          into the holding block); zero_based shifts by one.
    """
    if address_base is None:
        address = int(register)
    else:
        offset = int(register) - int(address_base)
        address = offset + (0 if zero_based else 1)
    if address < 0:
        raise ValueError(f"register {register} resolves to negative address {address}")
    return address
