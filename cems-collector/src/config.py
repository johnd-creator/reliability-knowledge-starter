"""Configuration loaded from environment / .env (never committed)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # optional; tests may run without python-dotenv installed
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):  # type: ignore[misc]
        return False

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Modbus protocol hard limit for a single read transaction.
MODBUS_PROTOCOL_MAX_REGISTERS = 125


@dataclass(frozen=True)
class CemsConfig:
    host: str = "172.16.201.132"
    port: int = 502
    unit_id: int = 1
    timeout_seconds: float = 3.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 5.0
    # Safety guardrails (see validate_runtime_safety for the floors).
    min_request_gap_seconds: float = 0.05
    max_registers_per_read: int = MODBUS_PROTOCOL_MAX_REGISTERS
    stack_id: str = "1"
    poll_interval_seconds: float = 5.0
    parameter_registry_path: str = "registry/cems-parameters.yaml"
    parameter_refresh_seconds: int = 60
    aggregation_interval_minutes: int = 5

    def validate_runtime_safety(self) -> "CemsConfig":
        """Validate environment-loaded settings before any production request."""
        if self.poll_interval_seconds < 1.0:
            raise ValueError("cems-collector requires CEMS_POLL_INTERVAL_SECONDS >= 1.0")
        if self.min_request_gap_seconds < 0.01:
            raise ValueError("cems-collector requires CEMS_MIN_REQUEST_GAP_SECONDS >= 0.01")
        if self.max_registers_per_read < 1 or self.max_registers_per_read > MODBUS_PROTOCOL_MAX_REGISTERS:
            raise ValueError(
                "cems-collector register cap must stay between 1 and "
                f"{MODBUS_PROTOCOL_MAX_REGISTERS} (Modbus protocol limit)"
            )
        if not self.stack_id or not self.stack_id.strip():
            raise ValueError("cems-collector requires a non-empty CEMS_STACK_ID scope")
        if self.timeout_seconds < 0.1:
            raise ValueError("cems-collector requires CEMS_MODBUS_TIMEOUT_SECONDS >= 0.1")
        if self.aggregation_interval_minutes < 1:
            raise ValueError("cems-collector requires CEMS_AGGREGATION_INTERVAL_MINUTES >= 1")
        return self

    @classmethod
    def from_environment(cls) -> "CemsConfig":
        return cls(
            host=os.getenv("CEMS_MODBUS_HOST", cls.host),
            port=int(os.getenv("CEMS_MODBUS_PORT", "502")),
            unit_id=int(os.getenv("CEMS_MODBUS_UNIT_ID", "1")),
            timeout_seconds=float(os.getenv("CEMS_MODBUS_TIMEOUT_SECONDS", "3")),
            retry_attempts=int(os.getenv("CEMS_MODBUS_RETRY_ATTEMPTS", "3")),
            retry_delay_seconds=float(os.getenv("CEMS_MODBUS_RETRY_DELAY_SECONDS", "5")),
            min_request_gap_seconds=float(os.getenv("CEMS_MIN_REQUEST_GAP_SECONDS", "0.05")),
            max_registers_per_read=int(
                os.getenv("CEMS_MAX_REGISTERS_PER_READ", str(MODBUS_PROTOCOL_MAX_REGISTERS))
            ),
            stack_id=os.getenv("CEMS_STACK_ID", "1").strip(),
            poll_interval_seconds=float(os.getenv("CEMS_POLL_INTERVAL_SECONDS", "5")),
            parameter_registry_path=os.getenv(
                "CEMS_PARAMETER_REGISTRY", "registry/cems-parameters.yaml"
            ),
            parameter_refresh_seconds=int(os.getenv("CEMS_PARAMETER_REFRESH_SECONDS", "60")),
            aggregation_interval_minutes=int(os.getenv("CEMS_AGGREGATION_INTERVAL_MINUTES", "5")),
        ).validate_runtime_safety()


@dataclass(frozen=True)
class DbConfig:
    dsn: str = "postgresql+psycopg://cemscollector:cemscollector@localhost:5435/cemscollector"
    echo: bool = False

    @classmethod
    def from_environment(cls) -> "DbConfig":
        return cls(
            dsn=os.getenv("DATABASE_URL", cls.dsn),
            echo=os.getenv("DATABASE_ECHO", "0") == "1",
        )


def load_env() -> None:
    """Load .env from the repo root and the user home override, if present."""
    load_dotenv(_REPO_ROOT / ".env")
    load_dotenv(Path.home() / ".cems-collector.env")
