"""Shared configuration for the reliability cockpit sidecar.

All secrets come from the environment (or a local .env) — never from source
control. The sidecar never stores production credentials.

The data source is the maximo-collector API (:8002), not a direct OSLC connection.
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
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def load_env() -> None:
    """Load .env from the repo root and from the user home, if present."""
    _load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    _load_dotenv(Path.home() / ".reliability-cockpit.env")


@dataclass(frozen=True)
class CollectorConfig:
    collector_base_url: str = (
        os.getenv("MAXIMO_COLLECTOR_API_BASE", "http://127.0.0.1:8002").rstrip("/")
    )
    """Base URL for the maximo-collector API. Default: http://127.0.0.1:8002"""

    timeout_seconds: int = 60
    """Collector API request timeout."""

    page_size: int = 100
    """Default page / limit size for pulls."""

    rate_limit_seconds: float = 0.5
    """Sleep between collector API calls (collector read-only)."""


@dataclass(frozen=True)
class AppConfig:
    db: dict[str, str] = field(default_factory=lambda: {
        "dsn": os.getenv("DATABASE_URL", "postgresql://cockpit:cockpit@localhost:5432/cockpit"),
        "echo": os.getenv("DATABASE_ECHO", "0") == "1",
    })
    collector: CollectorConfig = field(default_factory=CollectorConfig.from_environment)


CollectorConfig.from_environment = classmethod(lambda cls: cls(
    collector_base_url=os.getenv("MAXIMO_COLLECTOR_API_BASE"),
    timeout_seconds=int(os.getenv("MAXIMO_COLLECTOR_TIMEOUT", "60")),
    page_size=int(os.getenv("MAXIMO_COLLECTOR_PAGE_SIZE", "100")),
    rate_limit_seconds=float(os.getenv("MAXIMO_COLLECTOR_RATE", "0.5")),
))

AppConfig.maximo = property(lambda self: None)  # type: ignore[assignment]
