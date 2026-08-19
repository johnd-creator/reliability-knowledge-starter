"""PI Web API adapter — placeholder.

PI access is not yet verified by pi-knowledge (endpoints pending discovery).
This module documents the intended interface; it raises NotImplementedError
until the PI knowledge repository records verified endpoints.
"""

from __future__ import annotations


class PiClient:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def build_headers(self) -> dict:
        raise NotImplementedError("PI access not yet verified; see pi-knowledge")

    def get_datapoint_web_id(self, path: str) -> str:
        raise NotImplementedError("PI access not yet verified; see pi-knowledge")

    def read_interpolated(self, web_id: str, start: str, end: str, interval: str) -> list[dict]:
        raise NotImplementedError("PI access not yet verified; see pi-knowledge")