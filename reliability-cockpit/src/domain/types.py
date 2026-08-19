"""Shared scalar type aliases and helpers (vendor-neutral)."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

Boolean = Union[bool, None]
Integer = Union[int, None]
Numeric = Union[float, int, None]
OptionalDatetime = Union[datetime, None]
Strings = List[str]