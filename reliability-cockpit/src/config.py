#!/usr/bin/env python3
"""Shared configuration for the Reliability Cockpit.

All secrets come from the environment (or a local .env) — never from source
control. The sidecar never stores production credentials.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def load_env() -> None:
    """Load .env from the repo root and from the user home, if present."""
    _load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    _load_dotenv(Path.home() / ".reliability-cockpit.env")


@dataclass(frozen=True)
class MaximoConfig:
    """Legacy read-only adapter configuration retained for isolated adapter tests.

    Normal Cockpit runtime uses :class:`CollectorConfig` and never constructs
    this adapter. Source credentials are therefore scoped to maximo-collector.
    """

    base_url: str
    oas_path: str = "/oslc/oas"
    oslc_root: str = "/oslc/os"
    site_id: str = "BSR"
    org_id: str = "IP"
    timeout_seconds: int = 30
    rate_limit_seconds: float = 1.0
    page_size: int = 100
    max_response_bytes: int = 1_048_576
    auth_mode: str = "bearer"
    token: str | None = None
    session_cookie: str | None = None

    @classmethod
    def from_environment(cls) -> "MaximoConfig":
        return cls(
            base_url=os.getenv("MAXIMO_BASE_URL", "http://maximo.invalid/maximo").rstrip("/"),
            oas_path=os.getenv("MAXIMO_OAS_PATH", "/oslc/oas"),
            oslc_root=os.getenv("MAXIMO_OSLC_ROOT", "/oslc/os"),
            site_id=os.getenv("MAXIMO_SITE_ID", "BSR"),
            org_id=os.getenv("MAXIMO_ORG_ID", "IP"),
            timeout_seconds=int(os.getenv("MAXIMO_TIMEOUT_SECONDS", "30")),
            rate_limit_seconds=float(os.getenv("MAXIMO_RATE_LIMIT_SECONDS", "1.0")),
            page_size=int(os.getenv("MAXIMO_PAGE_SIZE", "100")),
            max_response_bytes=int(os.getenv("MAXIMO_MAX_RESPONSE_BYTES", str(1_048_576))),
            auth_mode=os.getenv("MAXIMO_AUTH_MODE", "bearer"),
            token=os.getenv("MAXIMO_READ_ONLY_TOKEN") or None,
            session_cookie=os.getenv("MAXIMO_SESSION_COOKIE") or None,
        )


@dataclass(frozen=True)
class CollectorConfig:
    """Addresses of local collector APIs; no source-system credential lives here."""

    maximo_api_base: str = "http://127.0.0.1:8002"
    pi_api_base: str = "http://127.0.0.1:8001"
    cems_api_base: str = "http://127.0.0.1:8003"
    timeout_seconds: int = 60

    @classmethod
    def from_environment(cls) -> "CollectorConfig":
        return cls(
            maximo_api_base=os.getenv("MAXIMO_COLLECTOR_API_BASE", cls.maximo_api_base).rstrip("/"),
            pi_api_base=os.getenv("PI_COLLECTOR_API_BASE", cls.pi_api_base).rstrip("/"),
            cems_api_base=os.getenv("CEMS_COLLECTOR_API_BASE", cls.cems_api_base).rstrip("/"),
            timeout_seconds=int(os.getenv("COLLECTOR_TIMEOUT_SECONDS", "60")),
        )


@dataclass(frozen=True)
class DbtConfig:
    dsn: str = "postgresql://cockpit:cockpit@localhost:5432/cockpit"
    echo: bool = False

    @classmethod
    def from_environment(cls) -> "DbtConfig":
        return cls(
            dsn=os.getenv("DATABASE_URL", "postgresql://cockpit:cockpit@localhost:5432/cockpit"),
            echo=os.getenv("DATABASE_ECHO", "0") == "1",
        )


@dataclass(frozen=True)
class MartDbConfig:
    """Dedicated Reliability Mart connection configuration.

    No fallback to ``DATABASE_URL`` is intentional: the legacy Cockpit store
    and the canonical Mart are separate persistence boundaries.
    """

    dsn: str | None = None
    echo: bool = False
    statement_timeout_ms: int = 5000

    @classmethod
    def from_environment(cls) -> "MartDbConfig":
        timeout = int(os.getenv("RELIABILITY_MART_STATEMENT_TIMEOUT_MS", "5000"))
        if timeout < 1:
            raise ValueError("RELIABILITY_MART_STATEMENT_TIMEOUT_MS must be positive")
        return cls(
            dsn=os.getenv("RELIABILITY_MART_DATABASE_URL") or None,
            echo=os.getenv("RELIABILITY_MART_DATABASE_ECHO", "0") == "1",
            statement_timeout_ms=timeout,
        )


@dataclass(frozen=True)
class AppConfig:
    db: DbtConfig = field(default_factory=DbtConfig.from_environment)
    collectors: CollectorConfig = field(default_factory=CollectorConfig.from_environment)
