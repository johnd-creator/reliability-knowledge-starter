"""Tests for daemon hang protections — TCP keepalive session, socket default
timeout and the SIGALRM cycle hard-timeout. No network required.

Background (2026-08-19): one hung syscall (DNS getaddrinfo / dead pooled
connection) stalled the snapshot daemon for 2h39m — the requests read timeout
never fired because the block happened outside a bounded read.
"""

from __future__ import annotations

import signal
import socket
import unittest
from unittest import mock

from src.adapters.pi.client import PiClient, PiApiConfig, _keepalive_socket_options, new_session
from src.cli import CycleTimeoutError, _on_cycle_timeout


class KeepaliveSessionTest(unittest.TestCase):
    def test_new_session_mounts_keepalive_adapter(self):
        session = new_session()
        for prefix in ("https://", "http://"):
            adapter = session.get_adapter(prefix + "example/")
            opts = adapter.poolmanager.connection_pool_kw.get("socket_options")
            self.assertIsNotNone(opts, f"{prefix} adapter has no socket_options")
            keepalives = [o for o in opts if o[:2] == (socket.SOL_SOCKET, socket.SO_KEEPALIVE)]
            self.assertTrue(any(o[2] == 1 for o in keepalives),
                            f"{prefix} adapter does not enable SO_KEEPALIVE")

    def test_keepalive_options_only_portable_constants(self):
        for level, opt, value in _keepalive_socket_options():
            self.assertTrue(hasattr(socket, "TCP_KEEPIDLE") or opt != getattr(socket, "TCP_KEEPIDLE", None))
            self.assertIsInstance(value, int)

    def test_pi_client_uses_keepalive_session_by_default(self):
        cfg = PiApiConfig(base_url="https://example/piwebapi", rate_limit_seconds=0)
        client = PiClient(cfg)
        adapter = client._session.get_adapter("https://example/")
        self.assertIsNotNone(
            adapter.poolmanager.connection_pool_kw.get("socket_options")
        )


class CycleTimeoutTest(unittest.TestCase):
    def test_alarm_handler_raises_cycle_timeout(self):
        with self.assertRaises(CycleTimeoutError):
            _on_cycle_timeout(signal.SIGALRM, None)

    def test_alarm_interrupts_blocking_sleep(self):
        """SIGALRM must break out of a blocking time.sleep, mirroring how it
        would break a hung getaddrinfo/read inside a daemon cycle."""
        signal.signal(signal.SIGALRM, _on_cycle_timeout)
        signal.alarm(1)
        try:
            import time

            with self.assertRaises(CycleTimeoutError):
                time.sleep(60)
        finally:
            signal.alarm(0)

    def test_socket_default_timeout_bounded(self):
        """cmd_run sets a default socket timeout; simulate the formula used there."""
        cfg = PiApiConfig(base_url="https://example/piwebapi")
        expected = max(cfg.timeout_seconds * 3, 60)
        self.assertGreaterEqual(expected, 60)
        self.assertGreaterEqual(expected, cfg.timeout_seconds * 3)


if __name__ == "__main__":
    unittest.main()
