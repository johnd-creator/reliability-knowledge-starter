#!/usr/bin/env python3
"""Shared configuration for the reliability cockpit sidecar.

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
    base_url: str
    oas_path: str = "/oslc/oas"
    """OSLC object-structures under /oslc/os/<object_structure>."""
    oslc_root: str = "/oslc/os"
    site_id: str = "BSR"
    org_id: str = "IP"
    timeout_seconds: int = 30
    rate_limit_seconds: float = 1.0
    page_size: int = 100
    max_response_bytes: int = 1_048_576
    auth_mode: str = "bearer"  # "bearer" | "none" (read-only token)
    token: str | None = None
    """Read-only bearer token. Credentials are never stored by this repo."""
    session_cookie: str | None = None
    """Optional Maximo session cookie provided out-of-band at runtime."""

    @classmethod
    def from_environment(cls) -> "MaximoConfig":
        return cls(
            base_url=os.getenv("MAXIMO_BASE_URL", "http://maximo.plnindonesiapower.co.id/maximo").rstrip("/"),
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
class PiConfig:
    base_url: str = "https://pi.plnindonesiapower.co.id/piwebapi"

    @classmethod
    def from_environment(cls) -> "PiConfig":
        return cls(base_url=os.getenv("PI_BASE_URL", "https://pi.plnindonesiapower.co.id/piwebapi").rstrip("/"))


@dataclass(frozen=True)
class AppConfig:
    maximo: MaximoConfig = field(default_factory=MaximoConfig.from_environment)
    db: DbtConfig = field(default_factory=DbtConfig.from_environment)
    pi: PiConfig = field(default_factory=PiConfig.from_environment)